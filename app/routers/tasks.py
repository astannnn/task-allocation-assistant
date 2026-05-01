from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post("/", response_model=schemas.TaskResponse)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(
        models.Project.id == task.project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_task = models.Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        deadline=task.deadline,
        status=task.status,
        estimated_effort=task.estimated_effort,
        project_id=task.project_id,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@router.get("/", response_model=List[schemas.TaskResponse])
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@router.get("/{task_id}", response_model=schemas.TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.get("/project/{project_id}", response_model=List[schemas.TaskResponse])
def get_tasks_by_project(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.Task).filter(
        models.Task.project_id == project_id
    ).all()


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}

@router.post("/required-skills/", response_model=schemas.TaskRequiredSkillResponse)
def add_required_skill_to_task(
    required_skill: schemas.TaskRequiredSkillCreate,
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(
        models.Task.id == required_skill.task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    skill = db.query(models.Skill).filter(
        models.Skill.id == required_skill.skill_id
    ).first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing_requirement = db.query(models.TaskRequiredSkill).filter(
        models.TaskRequiredSkill.task_id == required_skill.task_id,
        models.TaskRequiredSkill.skill_id == required_skill.skill_id
    ).first()

    if existing_requirement:
        existing_requirement.required_level = required_skill.required_level
        db.commit()
        db.refresh(existing_requirement)
        return existing_requirement

    db_required_skill = models.TaskRequiredSkill(
        task_id=required_skill.task_id,
        skill_id=required_skill.skill_id,
        required_level=required_skill.required_level,
    )

    db.add(db_required_skill)
    db.commit()
    db.refresh(db_required_skill)

    return db_required_skill


@router.get("/{task_id}/required-skills", response_model=List[schemas.TaskRequiredSkillResponse])
def get_task_required_skills(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return db.query(models.TaskRequiredSkill).filter(
        models.TaskRequiredSkill.task_id == task_id
    ).all()

@router.patch("/{task_id}/status")
def update_task_status(
    task_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    allowed_statuses = ["open", "assigned", "in_progress", "completed", "delayed"]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid task status"
        )

    task.status = status
    db.commit()
    db.refresh(task)

    return {
        "message": "Task status updated successfully",
        "task_id": task.id,
        "new_status": task.status
    }