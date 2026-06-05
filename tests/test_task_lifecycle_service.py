import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Task
from app.services.task_lifecycle_service import (
    is_valid_task_status_transition,
    change_task_status,
    InvalidTaskStatusTransitionError,
)


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_allowed_task_status_transitions():
    assert is_valid_task_status_transition("open", "assigned") is True
    assert is_valid_task_status_transition("open", "manual_review") is True

    assert is_valid_task_status_transition("assigned", "in_progress") is True
    assert is_valid_task_status_transition("assigned", "delayed") is True

    assert is_valid_task_status_transition("in_progress", "completed") is True
    assert is_valid_task_status_transition("in_progress", "delayed") is True

    assert is_valid_task_status_transition("delayed", "manual_review") is True
    assert is_valid_task_status_transition("delayed", "assigned") is True

    assert is_valid_task_status_transition("manual_review", "assigned") is True


def test_invalid_task_status_transitions_are_rejected():
    assert is_valid_task_status_transition("open", "completed") is False
    assert is_valid_task_status_transition("completed", "in_progress") is False
    assert is_valid_task_status_transition("completed", "assigned") is False
    assert is_valid_task_status_transition("completed", "delayed") is False


def test_change_task_status_accepts_valid_transition(db_session):
    task = Task(
        title="Test task lifecycle",
        description="Testing valid lifecycle transition",
        status="open",
        priority="medium",
        project_id=1,
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    updated_task = change_task_status(db_session, task.id, "assigned")

    assert updated_task is not None
    assert updated_task.status == "assigned"


def test_change_task_status_rejects_invalid_transition(db_session):
    task = Task(
        title="Invalid lifecycle task",
        description="Testing invalid lifecycle transition",
        status="open",
        priority="medium",
        project_id=1,
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    with pytest.raises(InvalidTaskStatusTransitionError):
        change_task_status(db_session, task.id, "completed")


def test_completed_task_cannot_be_reopened_or_reassigned(db_session):
    task = Task(
        title="Completed task",
        description="Completed task must remain stable",
        status="completed",
        priority="medium",
        project_id=1,
    )

    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)

    with pytest.raises(InvalidTaskStatusTransitionError):
        change_task_status(db_session, task.id, "assigned")

    with pytest.raises(InvalidTaskStatusTransitionError):
        change_task_status(db_session, task.id, "in_progress")


def test_missing_task_returns_none(db_session):
    result = change_task_status(db_session, 999999, "assigned")

    assert result is None