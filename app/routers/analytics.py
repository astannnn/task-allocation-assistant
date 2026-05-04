from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.taxonomy import get_taxonomy_summary
from app.services.reminder_service import run_deadline_check

from app.database import get_db
from app import models
from app.services.workload_balancer import (
    analyze_project_workload,
    suggest_workload_redistribution,
)
from app.services.conflict_resolver import (
    detect_assignment_conflicts,
    suggest_conflict_resolution,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("/project/{project_id}/workload")
def get_project_workload_analysis(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return analyze_project_workload(project_id, db)


@router.get("/project/{project_id}/redistribution-suggestions")
def get_redistribution_suggestions(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return suggest_workload_redistribution(project_id, db)

@router.get("/project/{project_id}/conflicts")
def get_assignment_conflicts(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return detect_assignment_conflicts(project_id, db)


@router.get("/project/{project_id}/conflict-suggestions")
def get_conflict_resolution_suggestions(
    project_id: int,
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return suggest_conflict_resolution(project_id, db)

@router.get("/taxonomy")
def get_taxonomy():
    """
    Return the skill taxonomy and role ontology used by the allocation logic.
    This endpoint supports the explainability of the complex functionality.
    """
    return get_taxonomy_summary()

@router.post("/deadline-check")
def run_deadline_check_manually(db: Session = Depends(get_db)):
    """
    Manually run the deadline reminder and overdue task check.

    This endpoint is useful for testing the third-party APScheduler-based
    reminder functionality through Swagger.
    """
    return run_deadline_check(db)