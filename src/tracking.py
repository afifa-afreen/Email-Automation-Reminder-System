from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, RedirectResponse
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Message

router = APIRouter(tags=["tracking"])
PIXEL = bytes.fromhex(
    "47494638396101000100800000000000ffffff21f90401000000002c00000000010001000002024401003b"
)

@router.get("/track/open/{message_id}")
def track_open(message_id: int, db: Session = Depends(get_db)):
    msg = db.get(Message, message_id)
    if msg:
        msg.opened_at = datetime.now(timezone.utc)
        if msg.status == "sent":
            msg.status = "opened"
        db.commit()
    return Response(content=PIXEL, media_type="image/gif",
                    headers={"Cache-Control": "no-store, no-cache, must-revalidate"})

@router.get("/track/click/{message_id}")
def track_click(message_id: int, url: str, db: Session = Depends(get_db)):
    # Production: allow-list destination domains to prevent open-redirect abuse.
    if not url.startswith(("https://", "http://")):
        raise HTTPException(400, "Only HTTP(S) destinations are allowed")
    msg = db.get(Message, message_id)
    if msg:
        msg.clicked_at = datetime.now(timezone.utc)
        msg.status = "clicked"
        db.commit()
    return RedirectResponse(url, status_code=302)
