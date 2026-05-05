from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Project, Task, TeamMember, Notification
from app.services.notification_service import (
    create_notification,
    get_all_notifications,
    get_notifications_by_user,
    mark_notification_as_read,
    create_task_assignment_notification,
    create_task_reassignment_notification,
    create_manual_review_notification,
)


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
        title="Notification Test Project",
        description="Project for notification service tests",
        deadline=datetime.utcnow() + timedelta(days=10),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def create_test_task(db, project):
    task = Task(
        title="Develop backend API",
        description="Create backend endpoints",
        priority="high",
        deadline=datetime.utcnow() + timedelta(days=5),
        status="assigned",
        estimated_effort=0.3,
        project_id=project.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def create_test_member(db, project, name="Ali"):
    member = TeamMember(
        name=name,
        role="Backend Developer",
        availability=0.8,
        workload=0.2,
        reliability=0.9,
        dynamic_status="available",
        mood_state="focused",
        project_id=project.id,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def test_create_notification(test_db_session):
    notification = create_notification(
        db=test_db_session,
        message="Test notification",
        notification_type="info",
        user_id=1,
    )

    saved_notification = test_db_session.query(Notification).first()

    assert notification.id is not None
    assert saved_notification.message == "Test notification"
    assert saved_notification.type == "info"
    assert saved_notification.user_id == 1
    assert saved_notification.is_read == 0


def test_get_all_notifications_returns_notifications_in_desc_order(test_db_session):
    first = create_notification(
        db=test_db_session,
        message="First notification",
        notification_type="info",
    )

    second = create_notification(
        db=test_db_session,
        message="Second notification",
        notification_type="warning",
    )

    notifications = get_all_notifications(test_db_session)

    assert len(notifications) == 2
    assert notifications[0].id == second.id
    assert notifications[1].id == first.id


def test_get_notifications_by_user(test_db_session):
    create_notification(
        db=test_db_session,
        message="User 1 notification",
        notification_type="info",
        user_id=1,
    )

    create_notification(
        db=test_db_session,
        message="User 2 notification",
        notification_type="info",
        user_id=2,
    )

    user_notifications = get_notifications_by_user(
        db=test_db_session,
        user_id=1,
    )

    assert len(user_notifications) == 1
    assert user_notifications[0].user_id == 1
    assert user_notifications[0].message == "User 1 notification"


def test_mark_notification_as_read(test_db_session):
    notification = create_notification(
        db=test_db_session,
        message="Unread notification",
        notification_type="info",
    )

    updated_notification = mark_notification_as_read(
        db=test_db_session,
        notification_id=notification.id,
    )

    assert updated_notification is not None
    assert updated_notification.is_read == 1


def test_mark_notification_as_read_returns_none_for_missing_notification(test_db_session):
    result = mark_notification_as_read(
        db=test_db_session,
        notification_id=999,
    )

    assert result is None


def test_create_task_assignment_notification(test_db_session):
    project = create_test_project(test_db_session)
    task = create_test_task(test_db_session, project)
    member = create_test_member(test_db_session, project, name="Ali")

    notification = create_task_assignment_notification(
        db=test_db_session,
        task=task,
        team_member=member,
    )

    assert notification.type == "task_assigned"
    assert "Develop backend API" in notification.message
    assert "Ali" in notification.message


def test_create_task_reassignment_notification(test_db_session):
    project = create_test_project(test_db_session)
    task = create_test_task(test_db_session, project)
    previous_member = create_test_member(test_db_session, project, name="Ali")
    new_member = create_test_member(test_db_session, project, name="Maria")

    notification = create_task_reassignment_notification(
        db=test_db_session,
        task=task,
        previous_member=previous_member,
        new_member=new_member,
    )

    assert notification.type == "task_reassigned"
    assert "Develop backend API" in notification.message
    assert "Ali" in notification.message
    assert "Maria" in notification.message


def test_create_task_reassignment_notification_without_previous_member(test_db_session):
    project = create_test_project(test_db_session)
    task = create_test_task(test_db_session, project)
    new_member = create_test_member(test_db_session, project, name="Maria")

    notification = create_task_reassignment_notification(
        db=test_db_session,
        task=task,
        previous_member=None,
        new_member=new_member,
    )

    assert notification.type == "task_reassigned"
    assert "previous assignee" in notification.message
    assert "Maria" in notification.message


def test_create_manual_review_notification(test_db_session):
    project = create_test_project(test_db_session)
    task = create_test_task(test_db_session, project)

    notification = create_manual_review_notification(
        db=test_db_session,
        task=task,
        reason="No suitable candidate found",
    )

    assert notification.type == "manual_review"
    assert "Develop backend API" in notification.message
    assert "No suitable candidate found" in notification.message
