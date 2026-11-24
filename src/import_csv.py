import csv
from sqlalchemy import select
from src.database import SessionLocal
from src.models import Contact

def import_contacts(path="data/contacts.csv"):
    db = SessionLocal()
    created = 0
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if not row.get("email"): continue
                exists = db.scalar(select(Contact).where(Contact.email == row["email"]))
                if not exists:
                    db.add(Contact(name=row["name"], email=row["email"],
                                   company=row.get("company") or None))
                    created += 1
        db.commit()
        return created
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Imported {import_contacts()} new contacts")
