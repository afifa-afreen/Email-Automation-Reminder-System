# Logical SQL schema

- contacts(id PK, name, email UNIQUE, company, unsubscribed, created_at)
- templates(id PK, name UNIQUE, subject, html_body, markdown_body, created_at)
- campaigns(id PK, name, template_id FK, status, created_at)
- reminders(id PK, title, contact_id FK, template_id FK, scheduled_at, rrule, next_fire_at, last_fired_at, active)
- messages(id PK, contact_id FK, template_id FK, campaign_id FK NULL, reminder_id FK NULL, scheduled_for, status, provider_message_id, error_message, attempt_count, opened_at, clicked_at, created_at)

A unique constraint on (reminder_id, scheduled_for) prevents duplicate message creation for the same reminder occurrence.
