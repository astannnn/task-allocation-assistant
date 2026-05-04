from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app import models
from app.services.notification_service import create_notification


def find_tasks_with_approaching_deadlines(
    db: Session,
    days_before_deadline: int = 3
) -> List[models.Task]:
    """
    Find tasks whose deadlines are approaching.

    The function returns tasks that:
    - are not completed;
    - have a deadline;
    - have a deadline within the next N days.
    """
    now = datetime.utcnow()
    deadline_limit = now + timedelta(days=days_before_deadline)

    return db.query(models.Task).filter(
        models.Task.deadline.isnot(None),
        models.Task.status != "completed",
        models.Task.deadline >= now,
        models.Task.deadline <= deadline_limit,
    ).all()


def create_deadline_reminders(
    db: Session,
    days_before_deadline: int = 3
) -> int:
    """
    Create reminder notifications for tasks with approaching deadlines.

    The function avoids creating duplicate reminders for the same task
    if the same reminder message already exists.
    """
    tasks = find_tasks_with_approaching_deadlines(
        db=db,
        days_before_deadline=days_before_deadline,
    )

    created_count = 0

    for task in tasks:
        days_left = (task.deadline - datetime.utcnow()).days

        message = (
            f"Reminder: task '{task.title}' has an approaching deadline. "
            f"Days left: {days_left}."
        )

        existing_notification = db.query(models.Notification).filter(
            models.Notification.message == message,
            models.Notification.type == "deadline_reminder",
        ).first()

        if existing_notification:
            continue

        create_notification(
            db=db,
            message=message,
            notification_type="deadline_reminder",
        )

        created_count += 1

    return created_count


def check_overdue_tasks(db: Session) -> int:
    """
    Check tasks whose deadlines have already passed.

    If a task is overdue and not completed, its status is changed to delayed
    and a notification is created. Duplicate overdue notifications are avoided.
    """
    now = datetime.utcnow()

    overdue_tasks = db.query(models.Task).filter(
        models.Task.deadline.isnot(None),
        models.Task.status != "completed",
        models.Task.status != "delayed",
        models.Task.deadline < now,
    ).all()

    updated_count = 0

    for task in overdue_tasks:
        task.status = "delayed"

        message = f"Task '{task.title}' is overdue and was marked as delayed."

        existing_notification = db.query(models.Notification).filter(
            models.Notification.message == message,
            models.Notification.type == "task_delayed",
        ).first()

        if not existing_notification:
            create_notification(
                db=db,
                message=message,
                notification_type="task_delayed",
            )

        updated_count += 1

    db.commit()

    return updated_count


def run_deadline_check(db: Session) -> dict:
    """
    Run the full deadline check workflow.

    This function can be called manually from an API endpoint or automatically
    by APScheduler.
    """
    reminders_created = create_deadline_reminders(db=db)
    overdue_tasks_updated = check_overdue_tasks(db=db)

    return {
        "reminders_created": reminders_created,
        "overdue_tasks_updated": overdue_tasks_updated,
    }