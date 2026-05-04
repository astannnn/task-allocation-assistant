from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.notification_service import (
    get_all_notifications,
    get_notifications_by_user,
    mark_notification_as_read,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


def serialize_notification(notification):
    """
    Convert SQLAlchemy Notification object to dictionary.
    """
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "message": notification.message,
        "type": notification.type,
        "created_at": notification.created_at,
        "is_read": notification.is_read,
    }


@router.get("/")
def list_notifications(db: Session = Depends(get_db)):
    notifications = get_all_notifications(db)

    return [
        serialize_notification(notification)
        for notification in notifications
    ]


@router.get("/user/{user_id}")
def list_user_notifications(
    user_id: int,
    db: Session = Depends(get_db)
):
    notifications = get_notifications_by_user(
        db=db,
        user_id=user_id,
    )

    return [
        serialize_notification(notification)
        for notification in notifications
    ]


@router.patch("/{notification_id}/read")
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    notification = mark_notification_as_read(
        db=db,
        notification_id=notification_id,
    )

    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found"
        )

    return serialize_notification(notification)