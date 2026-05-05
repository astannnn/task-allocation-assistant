from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app import models
from app.routers.project_templates import (
    GenerateTemplateTasksRequest,
    SelectedComponentRequest,
    generate_template_tasks_for_project,
)


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    return engine, TestingSessionLocal()


def create_project(db):
    user = models.User(
        name="Manager",
        email="manager@example.com",
        password_hash="hashed-password",
        role="manager",
    )

    project = models.Project(
        title="Website Development Project",
        description="Test project",
        deadline=datetime.utcnow(),
        creator=user,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def test_generate_template_tasks_skips_duplicates_by_default():
    engine, db = create_test_db()

    try:
        project = create_project(db)

        request = GenerateTemplateTasksRequest(
            template_key="website_development",
            selected_components=[
                SelectedComponentRequest(
                    component_key="backend_api",
                    complexity="high",
                ),
                SelectedComponentRequest(
                    component_key="frontend_pages",
                    complexity="medium",
                ),
            ],
        )

        first_result = generate_template_tasks_for_project(
            project_id=project.id,
            request=request,
            db=db,
        )

        second_result = generate_template_tasks_for_project(
            project_id=project.id,
            request=request,
            db=db,
        )

        all_tasks = db.query(models.Task).filter(
            models.Task.project_id == project.id
        ).all()

        assert first_result["total_created_tasks"] == 2
        assert first_result["total_skipped_tasks"] == 0

        assert second_result["total_created_tasks"] == 0
        assert second_result["total_skipped_tasks"] == 2

        assert len(all_tasks) == 2
        assert second_result["skipped_tasks"][0]["reason"] == "Task already exists in this project"

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_generate_template_tasks_allows_duplicates_when_enabled():
    engine, db = create_test_db()

    try:
        project = create_project(db)

        request = GenerateTemplateTasksRequest(
            template_key="website_development",
            allow_duplicates=True,
            selected_components=[
                SelectedComponentRequest(
                    component_key="backend_api",
                    complexity="high",
                ),
            ],
        )

        first_result = generate_template_tasks_for_project(
            project_id=project.id,
            request=request,
            db=db,
        )

        second_result = generate_template_tasks_for_project(
            project_id=project.id,
            request=request,
            db=db,
        )

        all_tasks = db.query(models.Task).filter(
            models.Task.project_id == project.id
        ).all()

        assert first_result["total_created_tasks"] == 1
        assert second_result["total_created_tasks"] == 1
        assert second_result["total_skipped_tasks"] == 0

        assert len(all_tasks) == 2

    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)