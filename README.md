# Email Automation & Reminder System

A portfolio-ready Python project demonstrating scheduled email workflows, recurring reminders, REST APIs, database persistence, SMTP integration, tracking events and a Next.js dashboard.

## Problem statement
Teams repeatedly send interview, training, meeting, payment and follow-up reminders. This project centralizes contacts and templates, schedules one-off or recurring reminders, dispatches due messages and records outcomes.

## Architecture
Next.js dashboard → FastAPI → SQLAlchemy database. A separate async worker checks due reminders every 15 seconds, creates queued messages, renders Jinja2 templates and sends via SMTP. Tracking endpoints record approximate opens and clicks.

## Features
- Contact, template, campaign and reminder APIs
- One-off reminders and RRULE recurrence
- Jinja2 personalization and Markdown-to-HTML rendering
- Async SMTP sending and dry-run simulation
- Queued/sending/sent/failed/cancelled status tracking
- Open pixel and click redirect endpoints
- CSV contact import and message report export
- Worker logs and pytest tests
- Next.js dashboard

## Stack
Python 3.11+, FastAPI, SQLAlchemy, SQLite, aiosmtplib, Jinja2, python-dateutil, Pandas, pytest, Next.js and React.

## Folder structure
```text
data/       sample CSV inputs
templates/  reusable email templates
src/        API, models, renderer, provider, worker and reports
tests/      automated tests
frontend/   Next.js dashboard
logs/       runtime logs (not committed)
outputs/    generated reports (not committed)
docs/       project documentation
images/     portfolio screenshots
```

## Setup (Windows PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python main.py --seed-demo
```

## Setup (macOS/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py --seed-demo
```

## Run locally
Terminal 1 — API:
```bash
uvicorn src.api:app --reload
```
Terminal 2 — worker:
```bash
python -m src.worker
```
The default `DRY_RUN=true` simulates sends and never contacts an SMTP server. The demo reminder is scheduled about 20 seconds after seeding.

## Actual SMTP sending
Only after testing, set `DRY_RUN=false` and configure SMTP values in your local `.env`. For Gmail, enable 2-Step Verification and create an app password if your account supports it. Never use your normal account password. Do not commit `.env`.

## Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:3000. Start the API first. Set `NEXT_PUBLIC_API_URL` if the API is hosted elsewhere.

## API documentation
Open http://localhost:8000/docs.

## Useful commands
```bash
python -m src.import_csv
python -m src.report
pytest -q
```

## Sample output
```text
Worker started; interval=15s dry_run=True
message_id=1 status=sent recipient=aarav@example.com
```
A dry-run `sent` status means simulated provider acceptance, not a real email delivery.

## Safety and limitations
- Use only contacts who have consented to receive the messages.
- Provide unsubscribe handling and honor suppression before dispatch.
- Add authentication, authorization, CSRF protection and API rate limits before public deployment.
- Restrict click redirect domains in production.
- Open tracking is approximate: privacy tools can prefetch images or block them.
- SMTP acceptance is not proof of inbox delivery. Use provider webhooks for delivered/bounced events.
- The starter worker is intended for a single local process. Production deployments need distributed locking, retry/backoff, idempotency, queue isolation and robust timezone handling.
- Do not upload `.env`, SMTP credentials, real contact data or private logs.

## Screenshots
Save screenshots in `images/`: folder tree, CSV sample, template, dry-run terminal, dashboard, message report and GitHub repository.

## Learning outcomes
Python modules, async I/O, REST API design, relational modeling, template rendering, scheduling, recurrence rules, logging, CSV reporting, tests, frontend/API integration and Git/GitHub workflow.
