import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from src.database import Base, engine, SessionLocal
from src.models import Contact, EmailTemplate, Reminder
from src.import_csv import import_contacts

def seed_demo():
    Base.metadata.create_all(bind=engine)
    import_contacts()
    db = SessionLocal()
    try:
        template = db.query(EmailTemplate).filter_by(name="follow_up").first()
        if not template:
            template = EmailTemplate(
                name="follow_up", subject="A friendly follow-up",
                html_body="<h2>Hello {{ name }},</h2><p>Following up from {{ company }}.</p>",
                markdown_body="## Hello {{ name }}\n\nFollowing up from **{{ company }}**."
            )
            db.add(template); db.commit(); db.refresh(template)
        contact = db.query(Contact).filter_by(email="aarav@example.com").first()
        if contact and not db.query(Reminder).filter_by(title="Demo reminder").first():
            scheduled = datetime.now(timezone.utc) + timedelta(seconds=20)
            db.add(Reminder(title="Demo reminder", contact_id=contact.id,
                            template_id=template.id, scheduled_at=scheduled,
                            next_fire_at=scheduled))
            db.commit()
            print("Created demo reminder for about 20 seconds from now.")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email Automation System")
    parser.add_argument("--seed-demo", action="store_true", help="Create sample data")
    args = parser.parse_args()
    Path("logs").mkdir(exist_ok=True); Path("outputs").mkdir(exist_ok=True)
    Base.metadata.create_all(bind=engine)
    if args.seed_demo: seed_demo()
    else: print("Database ready. Run API and worker in separate terminals.")
