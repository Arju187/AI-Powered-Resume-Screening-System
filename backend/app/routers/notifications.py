from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.application import Notification
from app.schemas.application import NotificationOut
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("/me", response_model=list[NotificationOut])
def my_notifications(limit: int = 20, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return notifs


@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, db: Session = Depends(get_db),
              current_user: User = Depends(get_current_user)):
    notif = db.query(Notification).filter(
        Notification.id == notification_id, Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    db.refresh(notif)
    return notif


@router.put("/read-all")
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(
        Notification.user_id == current_user.id, Notification.is_read == False  # noqa: E712
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
