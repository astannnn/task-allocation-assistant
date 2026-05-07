from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.allocation_engine import automatically_allocate_task
from app.services.reassignment_engine import reassign_delayed_task
from app.services.notification_service import (
    create_task_assignment_notification,
    create_task_reassignment_notification,
    create_manual_review_notification,
)


router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


@router.get("/preview/{task_id}")
def preview_task_allocation(task_id: int, db: Session = Depends(get_db)):
    from app.services.allocation_engine import find_best_team_member_for_task

    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    best_candidate, candidate_scores = find_best_team_member_for_task(task_id, db)

    return {
        "task_id": task_id,
        "task_title": task.title,
        "best_candidate": best_candidate,
        "candidate_scores": candidate_scores
    }


@router.post("/auto-allocate/{task_id}")
def auto_allocate_task(task_id: int, db: Session = Depends(get_db)):
    result = automatically_allocate_task(task_id, db)

    if not result["success"] and result["message"] == "Task not found":
        raise HTTPException(status_code=404, detail="Task not found")

    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if result.get("success") and task:
        assignment_id = result.get("assignment_id")

        if assignment_id:
            assignment = db.query(models.Assignment).filter(
                models.Assignment.id == assignment_id
            ).first()

            if assignment and assignment.team_member:
                create_task_assignment_notification(
                    db=db,
                    task=task,
                    team_member=assignment.team_member,
                )

    if not result.get("success") and task:
        if task.status == "manual_review":
            create_manual_review_notification(
                db=db,
                task=task,
                reason=result.get("message", "No suitable candidate found")
            )

    return result


@router.get("/", response_model=List[schemas.AssignmentResponse])
def get_assignments(db: Session = Depends(get_db)):
    return db.query(models.Assignment).all()


@router.get("/task/{task_id}", response_model=List[schemas.AssignmentResponse])
def get_assignments_by_task(task_id: int, db: Session = Depends(get_db)):
    return db.query(models.Assignment).filter(
        models.Assignment.task_id == task_id
    ).all()


@router.get("/member/{team_member_id}", response_model=List[schemas.AssignmentResponse])
def get_assignments_by_team_member(
    team_member_id: int,
    db: Session = Depends(get_db)
):
    return db.query(models.Assignment).filter(
        models.Assignment.team_member_id == team_member_id
    ).all()


@router.post("/reassign-delayed/{task_id}")
def reassign_delayed(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    previous_assignment = db.query(models.Assignment).filter(
        models.Assignment.task_id == task_id,
        models.Assignment.status == "active"
    ).first()

    previous_member = previous_assignment.team_member if previous_assignment else None

    result = reassign_delayed_task(task_id, db)

    if not result["success"] and result["message"] == "Task not found":
        raise HTTPException(status_code=404, detail="Task not found")

    if result.get("success"):
        assignment_id = result.get("assignment_id")

        if assignment_id:
            new_assignment = db.query(models.Assignment).filter(
                models.Assignment.id == assignment_id
            ).first()

            if new_assignment and new_assignment.team_member:
                create_task_reassignment_notification(
                    db=db,
                    task=task,
                    previous_member=previous_member,
                    new_member=new_assignment.team_member,
                )

    if not result.get("success") and task.status == "manual_review":
        create_manual_review_notification(
            db=db,
            task=task,
            reason=result.get("message", "No suitable candidate found for reassignment")
        )

    return result