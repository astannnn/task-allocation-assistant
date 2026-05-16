from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
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


class ManualAssignmentRequest(BaseModel):
    task_id: int
    team_member_id: int


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


@router.post("/manual-assign")
def manually_assign_task(
    assignment_data: ManualAssignmentRequest,
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(
        models.Task.id == assignment_data.task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == assignment_data.team_member_id
    ).first()

    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")

    if task.project_id != team_member.project_id:
        raise HTTPException(
            status_code=400,
            detail="Task and team member must belong to the same project"
        )

    task_effort = getattr(task, "estimated_effort", 0) or 0

    previous_active_assignments = db.query(models.Assignment).filter(
        models.Assignment.task_id == task.id,
        models.Assignment.status == "active"
    ).all()

    for previous_assignment in previous_active_assignments:
        previous_assignment.status = "inactive"

        if previous_assignment.team_member:
            previous_workload = previous_assignment.team_member.workload or 0
            previous_assignment.team_member.workload = max(
                0,
                previous_workload - task_effort
            )

    new_assignment = models.Assignment(
        task_id=task.id,
        team_member_id=team_member.id,
        assigned_at=datetime.utcnow(),
        status="active",
        score_at_assignment=None
    )

    current_workload = team_member.workload or 0
    team_member.workload = current_workload + task_effort

    task.status = "assigned"

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    create_task_assignment_notification(
        db=db,
        task=task,
        team_member=team_member,
    )

    return {
        "success": True,
        "message": "Task manually assigned successfully",
        "assignment_id": new_assignment.id,
        "task_id": task.id,
        "team_member_id": team_member.id,
        "team_member_name": team_member.name,
        "task_status": task.status,
        "assignment_status": new_assignment.status,
        "score_at_assignment": new_assignment.score_at_assignment
    }


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