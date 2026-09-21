from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.models import Notification, User
from app.schemas.schemas import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.timestamp.desc())
        .all()
    )


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    notification = db.query(Notification).get(notification_id)
    if not notification or notification.user_id != user.id:
        raise HTTPException(404, "Notification not found")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification
