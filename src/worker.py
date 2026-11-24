import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone
from dateutil.rrule import rrulestr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.config import settings
from src.database import SessionLocal
from src.models import Reminder, Message
from src.email_provider import send_email
from src.renderer import render_email

Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("logs/worker.log")]
)
log = logging.getLogger("email-worker")

def plan_due_reminders(db, now):
    reminders = db.scalars(
        select(Reminder).where(Reminder.active == True, Reminder.next_fire_at <= now)
    ).all()
    for reminder in reminders:
        fire_time = reminder.next_fire_at
        existing = db.scalar(select(Message).where(
            Message.reminder_id == reminder.id, Message.scheduled_for == fire_time
        ))
        if not existing:
            db.add(Message(
                contact_id=reminder.contact_id, template_id=reminder.template_id,
                reminder_id=reminder.id, scheduled_for=fire_time, status="queued"
            ))
        reminder.last_fired_at = fire_time
        if reminder.rrule:
            try:
                rule = rrulestr(reminder.rrule, dtstart=reminder.scheduled_at)
                next_time = rule.after(fire_time, inc=False)
                reminder.next_fire_at = next_time
                if next_time is None:
                    reminder.active = False
            except Exception:
                log.exception("Invalid RRULE for reminder %s", reminder.id)
                reminder.active = False
        else:
            reminder.active = False
    db.commit()

async def process_due_messages(db, now):
    due = db.scalars(select(Message).where(
        Message.status == "queued", Message.scheduled_for <= now
    ).order_by(Message.scheduled_for).limit(50)).all()
    for msg in due:
        contact = msg.contact
        if contact.unsubscribed:
            msg.status = "cancelled"
            msg.error_message = "Contact has unsubscribed"
            continue
        msg.status = "sending"
        msg.attempt_count += 1
        db.commit()
        try:
            context = {"name": contact.name, "email": contact.email,
                       "company": contact.company or "", "sender_name": "Automation Team"}
            html, plain = render_email(msg.template, context)
            # Append tracking pixel. Opens are approximate; privacy tools may prefetch images.
            html += f'<img src="{settings.base_url}/track/open/{msg.id}" width="1" height="1" alt="">'
            provider_id = await send_email(contact.email, msg.template.subject, html, plain)
            msg.provider_message_id = provider_id
            msg.status = "sent"
            msg.error_message = None
            log.info("message_id=%s status=sent recipient=%s", msg.id, contact.email)
        except Exception as exc:
            msg.status = "failed"
            msg.error_message = str(exc)[:2000]
            log.exception("message_id=%s status=failed", msg.id)
        db.commit()

async def run_worker():
    log.info("Worker started; interval=%ss dry_run=%s",
             settings.worker_interval_seconds, settings.dry_run)
    while True:
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            plan_due_reminders(db, now)
            await process_due_messages(db, now)
        except Exception:
            log.exception("Worker tick failed")
            db.rollback()
        finally:
            db.close()
        await asyncio.sleep(settings.worker_interval_seconds)

if __name__ == "__main__":
    asyncio.run(run_worker())
