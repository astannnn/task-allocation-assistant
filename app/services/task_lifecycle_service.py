from app.models import Task


ALLOWED_TASK_STATUS_TRANSITIONS = {
    "open": {"assigned", "manual_review"},
    "assigned": {"in_progress", "delayed"},
    "in_progress": {"completed", "delayed"},
    "delayed": {"manual_review", "assigned"},
    "manual_review": {"assigned"},
    "completed": set(),
}


class InvalidTaskStatusTransitionError(Exception):
    pass


def is_valid_task_status_transition(current_status: str, new_status: str) -> bool:
    """
    Checks whether a task status transition is allowed.

    This function supports NFR-REL-02: task status consistency.
    It prevents impossible lifecycle changes such as open -> completed
    or completed -> assigned.
    """
    allowed_next_statuses = ALLOWED_TASK_STATUS_TRANSITIONS.get(current_status, set())
    return new_status in allowed_next_statuses


def change_task_status(db, task_id: int, new_status: str):
    """
    Changes task status only if the transition is valid.

    Args:
        db: SQLAlchemy database session
        task_id: ID of the task
        new_status: target status

    Returns:
        Updated Task object, or None if task does not exist.

    Raises:
        InvalidTaskStatusTransitionError if transition is not allowed.
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        return None

    current_status = task.status

    if current_status == new_status:
        return task

    if not is_valid_task_status_transition(current_status, new_status):
        raise InvalidTaskStatusTransitionError(
            f"Invalid task status transition: {current_status} -> {new_status}"
        )

    task.status = new_status
    db.commit()
    db.refresh(task)

    return task