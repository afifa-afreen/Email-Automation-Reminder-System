import pandas as pd
from sqlalchemy import select
from src.database import SessionLocal
from src.models import Message

def export_messages(path="outputs/messages_report.csv"):
    db = SessionLocal()
    try:
        rows = db.scalars(select(Message).order_by(Message.id)).all()
        data = [{
            "message_id": m.id, "recipient": m.contact.email,
            "subject": m.template.subject, "scheduled_for": m.scheduled_for,
            "status": m.status, "attempts": m.attempt_count,
            "provider_message_id": m.provider_message_id,
            "error": m.error_message, "opened_at": m.opened_at,
            "clicked_at": m.clicked_at
        } for m in rows]
        pd.DataFrame(data).to_csv(path, index=False)
        return len(data)
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Exported {export_messages()} messages")
