from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Project, Task, Notification
from app.services.reminder_service import run_deadline_check


@pytest.fixture
def test_db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def create_test_project(db):
    project = Project(
        title="Test Project",
        description="Project for reminder service tests",
        deadline=datetime.utcnow() + timedelta(days=10),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def test_approaching_deadline_creates_reminder(test_db_session):
    project = create_test_project(test_db_session)

    task = Task(
        title="Develop backend API",
        description="Create backend endpoints",
        priority="high",
        deadline=datetime.utcnow() + timedelta(days=2),
        status="assigned",
        estimated_effort=0.3,
        project_id=project.id,
    )

    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)

    result = run_deadline_check(test_db_session)

    notifications = test_db_session.query(Notification).all()

    assert result["reminders_created"] == 1
    assert len(notifications) == 1
    assert notifications[0].type == "deadline_reminder"
    assert "Develop backend API" in notifications[0].message


def test_overdue_task_becomes_delayed(test_db_session):
    project = create_test_project(test_db_session)

    task = Task(
        title="Implement authentication",
        description="Create login and registration",
        priority="critical",
        deadline=datetime.utcnow() - timedelta(days=1),
        status="assigned",
        estimated_effort=0.4,
        project_id=project.id,
    )

    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)

    result = run_deadline_check(test_db_session)

    updated_task = test_db_session.query(Task).filter(
        Task.id == task.id
    ).first()

    notifications = test_db_session.query(Notification).all()

    assert result["overdue_tasks_updated"] == 1
    assert updated_task.status == "delayed"
    assert len(notifications) == 1
    assert notifications[0].type == "task_delayed"
    assert "Implement authentication" in notifications[0].message


def test_duplicate_deadline_reminders_are_not_created(test_db_session):
    project = create_test_project(test_db_session)

    task = Task(
        title="Build dashboard page",
        description="Create dashboard UI",
        priority="medium",
        deadline=datetime.utcnow() + timedelta(days=2),
        status="assigned",
        estimated_effort=0.2,
        project_id=project.id,
    )

    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)

    first_result = run_deadline_check(test_db_session)
    second_result = run_deadline_check(test_db_session)

    notifications = test_db_session.query(Notification).all()

    assert first_result["reminders_created"] == 1
    assert second_result["reminders_created"] == 0
    assert len(notifications) == 1
    assert notifications[0].type == "deadline_reminder"


def test_completed_tasks_are_ignored_by_deadline_check(test_db_session):
    project = create_test_project(test_db_session)

    task = Task(
        title="Completed task",
        description="This task is already completed",
        priority="low",
        deadline=datetime.utcnow() - timedelta(days=1),
        status="completed",
        estimated_effort=0.1,
        project_id=project.id,
    )

    test_db_session.add(task)
    test_db_session.commit()
    test_db_session.refresh(task)

    result = run_deadline_check(test_db_session)

    updated_task = test_db_session.query(Task).filter(
        Task.id == task.id
    ).first()

    notifications = test_db_session.query(Notification).all()

    assert result["reminders_created"] == 0
    assert result["overdue_tasks_updated"] == 0
    assert updated_task.status == "completed"
    assert len(notifications) == 0
