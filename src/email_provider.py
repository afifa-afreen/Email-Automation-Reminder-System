from email.message import EmailMessage
from uuid import uuid4
import aiosmtplib
from src.config import settings

async def send_email(to_email: str, subject: str, html: str, plain: str) -> str:
    """Send one message. In dry-run mode, return a simulated provider ID."""
    if settings.dry_run:
        return f"dry-run-{uuid4().hex[:12]}"
    if not all([settings.smtp_host, settings.smtp_username, settings.smtp_password,
                settings.smtp_from_email]):
        raise RuntimeError("SMTP credentials are incomplete; configure your .env file.")

    msg = EmailMessage()
    msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    await aiosmtplib.send(
        msg, hostname=settings.smtp_host, port=settings.smtp_port,
        start_tls=True, username=settings.smtp_username,
        password=settings.smtp_password, timeout=30
    )
    # SMTP does not universally return a durable provider message ID.
    return msg.get("Message-ID") or f"smtp-{uuid4().hex}"
