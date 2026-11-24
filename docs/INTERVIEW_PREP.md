# Interview preparation

## Explain your project
I built an Email Automation & Reminder System using Python, FastAPI, SQLAlchemy and Next.js. It stores contacts and reusable templates, schedules one-off and recurring reminders using RRULE, and runs a background worker every 15 seconds. The worker renders personalized email content and sends it through asynchronous SMTP, or simulates sending in dry-run mode. Every message has a status and error record, while tracking endpoints capture approximate opens and clicks. I added CSV import/export, tests, logs and a dashboard.

## 10 interview questions and answers

1. **What problem does it solve?** It reduces repetitive manual communication and makes scheduled follow-ups consistent and auditable.
2. **Why FastAPI?** It provides typed request validation, automatic OpenAPI docs and good async support.
3. **Why SQLAlchemy?** It maps relational tables to Python objects and helps keep database operations maintainable.
4. **How do recurring reminders work?** An RRULE is parsed with dateutil. After a fire time, the worker calculates the next occurrence and queues a message.
5. **What is dry-run mode?** It creates a simulated provider ID without connecting to SMTP, allowing safe end-to-end testing.
6. **Does SMTP sent mean delivered?** No. It means the SMTP server accepted the message. Delivery and bounce events need provider feedback.
7. **How do you personalize email?** Jinja2 merges a template with a validated context such as name and company.
8. **How do you handle failures?** Exceptions are captured, message status becomes failed, the error and attempt count are stored, and logs are written. Production should add retry/backoff.
9. **What are the risks of open tracking?** Image proxies, privacy features and blocked images make open events approximate rather than definitive.
10. **How would you scale it?** Move to PostgreSQL and a durable queue such as Redis/Celery, add distributed locks, worker concurrency limits, provider webhooks, monitoring and tenant-level access control.

## HR explanation
This project demonstrates practical automation: organizing contact data, reducing repetitive work, scheduling reminders, monitoring outcomes and documenting a reliable workflow.

## Technical explanation
The API handles CRUD operations, SQLAlchemy persists domain entities, the worker expands recurrence rules and dispatches due messages, Jinja2 renders content, aiosmtplib sends asynchronously, and tracking routes update message event timestamps.
