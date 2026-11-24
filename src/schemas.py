from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class ContactCreate(BaseModel):
    name: str
    email: str
    company: str | None = None

class TemplateCreate(BaseModel):
    name: str
    subject: str
    html_body: str
    markdown_body: str | None = None

class CampaignCreate(BaseModel):
    name: str
    template_id: int

class ReminderCreate(BaseModel):
    title: str
    contact_id: int
    template_id: int
    scheduled_at: datetime
    rrule: str | None = None

class Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)
