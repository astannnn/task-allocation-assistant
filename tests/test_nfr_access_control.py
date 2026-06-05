import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.main import (
    get_current_user,
    require_manager,
    require_team_member_or_manager,
    redirect_after_login,
)


class FakeRequest:
    def __init__(self, user_id=None):
        self.session = {}

        if user_id is not None:
            self.session["user_id"] = user_id


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


def create_test_user(db, name, email, role):
    user = models.User(
        name=name,
        email=email,
        password_hash="hashed-password-for-test",
        role=role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def test_get_current_user_returns_logged_in_user(db_session):
    manager = create_test_user(
        db_session,
        name="Manager User",
        email="manager@test.com",
        role="manager"
    )

    request = FakeRequest(user_id=manager.id)

    current_user = get_current_user(request, db_session)

    assert current_user is not None
    assert current_user.id == manager.id
    assert current_user.role == "manager"


def test_get_current_user_returns_none_without_session(db_session):
    request = FakeRequest()

    current_user = get_current_user(request, db_session)

    assert current_user is None


def test_require_manager_allows_manager_user(db_session):
    manager = create_test_user(
        db_session,
        name="Manager User",
        email="manager-access@test.com",
        role="manager"
    )

    request = FakeRequest(user_id=manager.id)

    current_user, redirect_response = require_manager(request, db_session)

    assert current_user is not None
    assert current_user.role == "manager"
    assert redirect_response is None


def test_require_manager_rejects_team_member_user(db_session):
    team_member = create_test_user(
        db_session,
        name="Team Member User",
        email="member-access@test.com",
        role="team_member"
    )

    request = FakeRequest(user_id=team_member.id)

    current_user, redirect_response = require_manager(request, db_session)

    assert current_user is None
    assert redirect_response is not None
    assert redirect_response.status_code == 303
    assert redirect_response.headers["location"] == "/my-tasks"


def test_require_manager_redirects_anonymous_user_to_login(db_session):
    request = FakeRequest()

    current_user, redirect_response = require_manager(request, db_session)

    assert current_user is None
    assert redirect_response is not None
    assert redirect_response.status_code == 303
    assert redirect_response.headers["location"] == "/login"


def test_require_team_member_or_manager_allows_team_member(db_session):
    team_member = create_test_user(
        db_session,
        name="Team Member User",
        email="member-allowed@test.com",
        role="team_member"
    )

    request = FakeRequest(user_id=team_member.id)

    current_user, redirect_response = require_team_member_or_manager(
        request,
        db_session
    )

    assert current_user is not None
    assert current_user.role == "team_member"
    assert redirect_response is None


def test_require_team_member_or_manager_allows_manager(db_session):
    manager = create_test_user(
        db_session,
        name="Manager User",
        email="manager-allowed@test.com",
        role="manager"
    )

    request = FakeRequest(user_id=manager.id)

    current_user, redirect_response = require_team_member_or_manager(
        request,
        db_session
    )

    assert current_user is not None
    assert current_user.role == "manager"
    assert redirect_response is None


def test_require_team_member_or_manager_redirects_anonymous_user(db_session):
    request = FakeRequest()

    current_user, redirect_response = require_team_member_or_manager(
        request,
        db_session
    )

    assert current_user is None
    assert redirect_response is not None
    assert redirect_response.status_code == 303
    assert redirect_response.headers["location"] == "/login"


def test_redirect_after_login_sends_manager_to_dashboard():
    manager = models.User(
        name="Manager User",
        email="manager-redirect@test.com",
        password_hash="hashed-password-for-test",
        role="manager"
    )

    response = redirect_after_login(manager)

    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_redirect_after_login_sends_team_member_to_my_tasks():
    team_member = models.User(
        name="Team Member User",
        email="member-redirect@test.com",
        password_hash="hashed-password-for-test",
        role="team_member"
    )

    response = redirect_after_login(team_member)

    assert response.status_code == 303
    assert response.headers["location"] == "/my-tasks"