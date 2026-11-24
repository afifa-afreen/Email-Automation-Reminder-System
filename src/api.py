from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from src.database import Base, engine, get_db
from src.models import Contact, EmailTemplate, Campaign, Reminder, Message
from src.schemas import ContactCreate, TemplateCreate, CampaignCreate, ReminderCreate
from src.tracking import router as tracking_router

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Email Automation & Reminder System", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tracking_router)

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.post("/contacts", status_code=201)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Contact).where(Contact.email == payload.email)):
        raise HTTPException(409, "Contact email already exists")
    item = Contact(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@app.get("/contacts")
def list_contacts(db: Session = Depends(get_db)):
    return db.scalars(select(Contact).order_by(Contact.id.desc())).all()

@app.patch("/contacts/{contact_id}/unsubscribe")
def unsubscribe(contact_id: int, db: Session = Depends(get_db)):
    item = db.get(Contact, contact_id)
    if not item: raise HTTPException(404, "Contact not found")
    item.unsubscribed = True; db.commit()
    return {"id": item.id, "unsubscribed": True}

@app.post("/templates", status_code=201)
def create_template(payload: TemplateCreate, db: Session = Depends(get_db)):
    if db.scalar(select(EmailTemplate).where(EmailTemplate.name == payload.name)):
        raise HTTPException(409, "Template name already exists")
    item = EmailTemplate(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@app.get("/templates")
def list_templates(db: Session = Depends(get_db)):
    return db.scalars(select(EmailTemplate)).all()

@app.post("/campaigns", status_code=201)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    if not db.get(EmailTemplate, payload.template_id):
        raise HTTPException(404, "Template not found")
    item = Campaign(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@app.get("/campaigns")
def list_campaigns(db: Session = Depends(get_db)):
    return db.scalars(select(Campaign)).all()

@app.post("/reminders", status_code=201)
def create_reminder(payload: ReminderCreate, db: Session = Depends(get_db)):
    if not db.get(Contact, payload.contact_id): raise HTTPException(404, "Contact not found")
    if not db.get(EmailTemplate, payload.template_id): raise HTTPException(404, "Template not found")
    item = Reminder(**payload.model_dump(), next_fire_at=payload.scheduled_at)
    db.add(item); db.commit(); db.refresh(item)
    return item

@app.get("/reminders")
def list_reminders(db: Session = Depends(get_db)):
    return db.scalars(select(Reminder).order_by(Reminder.scheduled_at)).all()

@app.get("/messages")
def list_messages(status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Message).order_by(Message.created_at.desc())
    if status: stmt = stmt.where(Message.status == status)
    return db.scalars(stmt.limit(500)).all()


# Read/update/delete routes complete the basic CRUD surface.
@app.get("/contacts/{contact_id}")
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    item = db.get(Contact, contact_id)
    if not item: raise HTTPException(404, "Contact not found")
    return item

@app.patch("/contacts/{contact_id}")
def update_contact(contact_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.get(Contact, contact_id)
    if not item: raise HTTPException(404, "Contact not found")
    for key in ("name", "email", "company", "unsubscribed"):
        if key in payload: setattr(item, key, payload[key])
    db.commit(); db.refresh(item)
    return item

@app.delete("/contacts/{contact_id}", status_code=204)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    item = db.get(Contact, contact_id)
    if not item: raise HTTPException(404, "Contact not found")
    db.delete(item); db.commit()

@app.get("/templates/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    item = db.get(EmailTemplate, template_id)
    if not item: raise HTTPException(404, "Template not found")
    return item

@app.patch("/templates/{template_id}")
def update_template(template_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.get(EmailTemplate, template_id)
    if not item: raise HTTPException(404, "Template not found")
    for key in ("name", "subject", "html_body", "markdown_body"):
        if key in payload: setattr(item, key, payload[key])
    db.commit(); db.refresh(item)
    return item

@app.delete("/templates/{template_id}", status_code=204)
def delete_template(template_id: int, db: Session = Depends(get_db)):
    item = db.get(EmailTemplate, template_id)
    if not item: raise HTTPException(404, "Template not found")
    db.delete(item); db.commit()

@app.get("/campaigns/{campaign_id}")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    item = db.get(Campaign, campaign_id)
    if not item: raise HTTPException(404, "Campaign not found")
    return item

@app.patch("/campaigns/{campaign_id}")
def update_campaign(campaign_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.get(Campaign, campaign_id)
    if not item: raise HTTPException(404, "Campaign not found")
    for key in ("name", "template_id", "status"):
        if key in payload: setattr(item, key, payload[key])
    db.commit(); db.refresh(item)
    return item

@app.delete("/campaigns/{campaign_id}", status_code=204)
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    item = db.get(Campaign, campaign_id)
    if not item: raise HTTPException(404, "Campaign not found")
    db.delete(item); db.commit()

@app.post("/campaigns/{campaign_id}/send-all", status_code=202)
def queue_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    if not campaign: raise HTTPException(404, "Campaign not found")
    contacts = db.scalars(select(Contact).where(Contact.unsubscribed == False)).all()
    now = datetime.now(timezone.utc)
    created = 0
    for contact in contacts:
        db.add(Message(contact_id=contact.id, template_id=campaign.template_id,
                       campaign_id=campaign.id, scheduled_for=now, status="queued"))
        created += 1
    campaign.status = "queued"
    db.commit()
    return {"campaign_id": campaign.id, "queued_messages": created}

@app.get("/reminders/{reminder_id}")
def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    item = db.get(Reminder, reminder_id)
    if not item: raise HTTPException(404, "Reminder not found")
    return item

@app.patch("/reminders/{reminder_id}")
def update_reminder(reminder_id: int, payload: dict, db: Session = Depends(get_db)):
    item = db.get(Reminder, reminder_id)
    if not item: raise HTTPException(404, "Reminder not found")
    for key in ("title", "contact_id", "template_id", "scheduled_at", "rrule", "next_fire_at", "active"):
        if key in payload: setattr(item, key, payload[key])
    db.commit(); db.refresh(item)
    return item

@app.delete("/reminders/{reminder_id}", status_code=204)
def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    item = db.get(Reminder, reminder_id)
    if not item: raise HTTPException(404, "Reminder not found")
    item.active = False
    db.commit()
