from typing import Optional, List

from sqlalchemy.orm import Session

from app import models


def create_notification(
    db: Session,
    message: str,
    notification_type: str = "info",
    user_id: Optional[int] = None,
) -> models.Notification:
    """
    Create a notification record in the database.

    Notifications are used to inform the manager or user about important
    allocation events, such as automatic assignment, reassignment,
    conflicts, or manual review cases.
    """
    notification = models.Notification(
        user_id=user_id,
        message=message,
        type=notification_type,
        is_read=0,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification


def get_all_notifications(db: Session) -> List[models.Notification]:
    """
    Return all notifications.
    """
    return db.query(models.Notification).order_by(
        models.Notification.created_at.desc()
    ).all()


def get_notifications_by_user(
    db: Session,
    user_id: int
) -> List[models.Notification]:
    """
    Return notifications for a specific user.
    """
    return db.query(models.Notification).filter(
        models.Notification.user_id == user_id
    ).order_by(
        models.Notification.created_at.desc()
    ).all()


def mark_notification_as_read(
    db: Session,
    notification_id: int
) -> Optional[models.Notification]:
    """
    Mark a notification as read.
    """
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id
    ).first()

    if not notification:
        return None

    notification.is_read = 1
    db.commit()
    db.refresh(notification)

    return notification


def create_task_assignment_notification(
    db: Session,
    task: models.Task,
    team_member: models.TeamMember,
):
    """
    Create notification when a task is automatically assigned.
    """
    message = (
        f"Task '{task.title}' was automatically assigned to "
        f"{team_member.name}."
    )

    return create_notification(
        db=db,
        message=message,
        notification_type="task_assigned",
    )


def create_task_reassignment_notification(
    db: Session,
    task: models.Task,
    previous_member: Optional[models.TeamMember],
    new_member: models.TeamMember,
):
    """
    Create notification when a delayed task is reassigned.
    """
    previous_name = previous_member.name if previous_member else "previous assignee"

    message = (
        f"Delayed task '{task.title}' was reassigned from "
        f"{previous_name} to {new_member.name}."
    )

    return create_notification(
        db=db,
        message=message,
        notification_type="task_reassigned",
    )


def create_manual_review_notification(
    db: Session,
    task: models.Task,
    reason: str,
):
    """
    Create notification when a task requires manual review.
    """
    message = (
        f"Task '{task.title}' requires manual review. Reason: {reason}"
    )

    return create_notification(
        db=db,
        message=message,
        notification_type="manual_review",
    )