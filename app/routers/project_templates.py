from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

from app.services.project_template_service import (
    get_available_project_templates,
    generate_tasks_from_template,
    generate_project_decomposition_summary,
)

from app.services.allocation_engine import automatically_allocate_task

router = APIRouter(
    prefix="/project-templates",
    tags=["Project Templates"],
)


class SelectedComponentRequest(BaseModel):
    component_key: str
    complexity: str


class GenerateTemplateTasksRequest(BaseModel):
    template_key: str
    selected_components: List[SelectedComponentRequest]
    allow_duplicates: bool = False


@router.get("/")
def get_project_templates():
    return get_available_project_templates()


@router.post("/generate-tasks")
def generate_template_tasks(request: GenerateTemplateTasksRequest):
    selected_components = [
        component.model_dump()
        for component in request.selected_components
    ]

    return {
        "template_key": request.template_key,
        "generated_tasks": generate_tasks_from_template(
            template_key=request.template_key,
            selected_components=selected_components,
        ),
    }


@router.post("/generate-summary")
def generate_template_summary(request: GenerateTemplateTasksRequest):
    selected_components = [
        component.model_dump()
        for component in request.selected_components
    ]

    return generate_project_decomposition_summary(
        template_key=request.template_key,
        selected_components=selected_components,
    )


def get_or_create_skill(db: Session, skill_name: str):
    """
    Get an existing skill by name or create it if it does not exist.
    This supports template-based task generation because required skills
    may already exist in the database or may need to be created automatically.
    """
    skill = db.query(models.Skill).filter(
        models.Skill.name == skill_name
    ).first()

    if skill:
        return skill

    skill = models.Skill(
        name=skill_name,
        type="hard",
        category=None,
    )

    db.add(skill)
    db.commit()
    db.refresh(skill)

    return skill


@router.post("/projects/{project_id}/generate-template-tasks")
def generate_template_tasks_for_project(
    project_id: int,
    request: GenerateTemplateTasksRequest,
    db: Session = Depends(get_db),
):
    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    selected_components = [
        component.model_dump()
        for component in request.selected_components
    ]

    generated_tasks = generate_tasks_from_template(
        template_key=request.template_key,
        selected_components=selected_components,
    )

    created_tasks = []
    skipped_tasks = []

    for generated_task in generated_tasks:
        if not request.allow_duplicates:
            existing_task = db.query(models.Task).filter(
                models.Task.project_id == project_id,
                models.Task.title == generated_task["title"],
            ).first()

            if existing_task:
                skipped_tasks.append(
                    {
                        "task_id": existing_task.id,
                        "project_id": existing_task.project_id,
                        "component_key": generated_task["component_key"],
                        "title": existing_task.title,
                        "reason": "Task already exists in this project",
                    }
                )
                continue
        task = models.Task(
            project_id=project_id,
            title=generated_task["title"],
            description=generated_task["description"],
            priority=generated_task["priority"],
            status="open",
            estimated_effort=generated_task["estimated_effort"],
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        created_required_skills = []

        for skill_name in generated_task["required_skills"]:
            skill = get_or_create_skill(
                db=db,
                skill_name=skill_name,
            )

            task_required_skill = models.TaskRequiredSkill(
                task_id=task.id,
                skill_id=skill.id,
                required_level=0.6,
            )

            db.add(task_required_skill)
            db.commit()
            db.refresh(task_required_skill)

            created_required_skills.append(
                {
                    "skill_id": skill.id,
                    "skill_name": skill.name,
                    "required_level": task_required_skill.required_level,
                }
            )

        created_tasks.append(
            {
                "task_id": task.id,
                "project_id": task.project_id,
                "component_key": generated_task["component_key"],
                "title": task.title,
                "description": task.description,
                "priority": task.priority,
                "status": task.status,
                "estimated_effort": task.estimated_effort,
                "complexity": generated_task["complexity"],
                "required_skills": created_required_skills,
            }
        )

    return {
        "project_id": project_id,
        "project_title": project.title,
        "template_key": request.template_key,
        "allow_duplicates": request.allow_duplicates,
        "total_created_tasks": len(created_tasks),
        "total_skipped_tasks": len(skipped_tasks),
        "created_tasks": created_tasks,
        "skipped_tasks": skipped_tasks,
    }

@router.post("/projects/{project_id}/generate-and-allocate")
def generate_and_allocate_template_tasks(
    project_id: int,
    request: GenerateTemplateTasksRequest,
    db: Session = Depends(get_db),
):
    """
    Generate tasks from a project template and automatically allocate each task.

    This endpoint combines:
    1. template-based project decomposition;
    2. required skill creation;
    3. multi-task generation;
    4. heuristic task allocation for every generated task.
    """
    generation_result = generate_template_tasks_for_project(
        project_id=project_id,
        request=request,
        db=db,
    )

    allocation_results = []

    for created_task in generation_result["created_tasks"]:
        allocation_result = automatically_allocate_task(
            task_id=created_task["task_id"],
            db=db,
        )

        allocation_results.append(
            {
                "task_id": created_task["task_id"],
                "title": created_task["title"],
                "component_key": created_task["component_key"],
                "priority": created_task["priority"],
                "estimated_effort": created_task["estimated_effort"],
                "required_skills": created_task["required_skills"],
                "allocation_result": allocation_result,
            }
        )

    return {
        "project_id": project_id,
        "project_title": generation_result["project_title"],
        "template_key": request.template_key,
        "total_generated_tasks": generation_result["total_created_tasks"],
        "allocation_summary": allocation_results,
    }