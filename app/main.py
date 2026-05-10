from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.services.scheduler_service import start_scheduler, shutdown_scheduler
from app import models
from app.auth import hash_password, verify_password
from app.routers import (
    projects,
    team_members,
    skills,
    tasks,
    assignments,
    analytics,
    notifications,
    project_templates,
    users
)


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Allocation Assistant",
    description="A decision-support assistant for team task allocation and project management.",
    version="0.1.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.add_middleware(
    SessionMiddleware,
    secret_key="task-allocation-assistant-secret-key"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# ---------- Routers ----------

app.include_router(analytics.router)
app.include_router(assignments.router)
app.include_router(tasks.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(team_members.router)
app.include_router(notifications.router)
app.include_router(project_templates.router)
app.include_router(users.router)


# ---------- Auth Helpers ----------

def get_current_user(request: Request, db: Session):
    user_id = request.session.get("user_id")

    if not user_id:
        return None

    return db.query(models.User).filter(models.User.id == user_id).first()


def require_login(request: Request, db: Session):
    current_user = get_current_user(request, db)

    if not current_user:
        return None, RedirectResponse(url="/login", status_code=303)

    return current_user, None


def require_manager(request: Request, db: Session):
    current_user = get_current_user(request, db)

    if not current_user:
        return None, RedirectResponse(url="/login", status_code=303)

    if current_user.role != "manager":
        return None, RedirectResponse(url="/my-tasks", status_code=303)

    return current_user, None


def require_team_member_or_manager(request: Request, db: Session):
    current_user = get_current_user(request, db)

    if not current_user:
        return None, RedirectResponse(url="/login", status_code=303)

    return current_user, None


def redirect_after_login(user: models.User):
    if user.role == "manager":
        return RedirectResponse(url="/", status_code=303)

    return RedirectResponse(url="/my-tasks", status_code=303)


def calculate_employee_workload_status(active_assignments_count: int):
    if active_assignments_count == 0:
        return "underloaded"

    if active_assignments_count <= 2:
        return "balanced"

    return "overloaded"


def calculate_completion_rate(total_assignments: int, completed_assignments: int):
    if total_assignments == 0:
        return 0

    return round((completed_assignments / total_assignments) * 100, 1)


def get_assignment_score_safely(assignment):
    score_fields = ["score", "allocation_score", "matching_score"]

    for field in score_fields:
        score_value = getattr(assignment, field, None)

        if score_value is not None:
            return score_value

    return None


def release_task_from_assignment(assignment):
    if assignment.task and assignment.task.status in [
        "assigned",
        "in_progress",
        "delayed",
        "manual_review"
    ]:
        assignment.task.status = "open"


# ---------- Auth UI Routes ----------

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "title": "Register",
            "error": None,
            "current_user": None
        }
    )


@app.post("/register")
def register_user_ui(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form("team_member"),
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_user:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "title": "Register",
                "error": "User with this email already exists",
                "current_user": None
            }
        )

    user_role = "team_member"

    user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=user_role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    request.session["user_id"] = user.id
    request.session["user_role"] = user.role

    return redirect_after_login(user)


@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "title": "Login",
            "error": None,
            "current_user": None
        }
    )


@app.post("/login")
def login_user_ui(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "title": "Login",
                "error": "Invalid email or password",
                "current_user": None
            }
        )

    request.session["user_id"] = user.id
    request.session["user_role"] = user.role

    return redirect_after_login(user)


@app.get("/logout")
def logout_user(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


# ---------- Team Member UI Routes ----------

@app.get("/my-tasks")
def my_tasks_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_team_member_or_manager(request, db)

    if redirect_response:
        return redirect_response

    team_members = db.query(models.TeamMember).filter(
        models.TeamMember.user_id == current_user.id
    ).all()

    team_member_ids = [member.id for member in team_members]
    primary_team_member = team_members[0] if team_members else None

    if team_member_ids:
        assignments = db.query(models.Assignment).filter(
            models.Assignment.team_member_id.in_(team_member_ids)
        ).all()
    else:
        assignments = []

    return templates.TemplateResponse(
        "my_tasks.html",
        {
            "request": request,
            "title": "My Tasks",
            "current_user": current_user,
            "assignments": assignments,
            "primary_team_member": primary_team_member
        }
    )


@app.post("/my-tasks/{assignment_id}/status")
def update_my_task_status(
    assignment_id: int,
    new_status: str = Form(...),
    request: Request = None,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_team_member_or_manager(request, db)

    if redirect_response:
        return redirect_response

    assignment = db.query(models.Assignment).join(
        models.TeamMember,
        models.Assignment.team_member_id == models.TeamMember.id
    ).filter(
        models.Assignment.id == assignment_id,
        models.TeamMember.user_id == current_user.id
    ).first()

    if not assignment:
        return RedirectResponse(url="/my-tasks", status_code=303)

    allowed_statuses = ["in_progress", "completed"]

    if new_status not in allowed_statuses:
        return RedirectResponse(url="/my-tasks", status_code=303)

    current_task_status = assignment.task.status

    if current_task_status == "assigned" and new_status == "in_progress":
        assignment.task.status = "in_progress"
        assignment.status = "active"

    elif current_task_status == "in_progress" and new_status == "completed":
        assignment.task.status = "completed"
        assignment.status = "completed"

    else:
        return RedirectResponse(url="/my-tasks", status_code=303)

    db.commit()

    return RedirectResponse(url="/my-tasks", status_code=303)


@app.post("/my-profile/status")
def update_my_profile_status(
    request: Request,
    dynamic_status: str = Form(...),
    mood_state: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_team_member_or_manager(request, db)

    if redirect_response:
        return redirect_response

    allowed_dynamic_statuses = ["available", "busy", "focused", "blocked"]
    allowed_mood_states = ["positive", "neutral", "stressed"]

    if dynamic_status not in allowed_dynamic_statuses:
        return RedirectResponse(url="/my-tasks", status_code=303)

    if mood_state not in allowed_mood_states:
        return RedirectResponse(url="/my-tasks", status_code=303)

    team_members = db.query(models.TeamMember).filter(
        models.TeamMember.user_id == current_user.id
    ).all()

    if not team_members:
        return RedirectResponse(url="/my-tasks", status_code=303)

    for team_member in team_members:
        team_member.dynamic_status = dynamic_status
        team_member.mood_state = mood_state

    db.commit()

    return RedirectResponse(url="/my-tasks", status_code=303)


@app.get("/notifications-ui")
def notifications_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_team_member_or_manager(request, db)

    if redirect_response:
        return redirect_response

    if current_user.role == "manager":
        notifications_list = db.query(models.Notification).order_by(
            models.Notification.created_at.desc()
        ).all()
    else:
        notifications_list = db.query(models.Notification).filter(
            models.Notification.user_id == current_user.id
        ).order_by(
            models.Notification.created_at.desc()
        ).all()

    return templates.TemplateResponse(
        "notifications.html",
        {
            "request": request,
            "title": "Notifications",
            "current_user": current_user,
            "notifications": notifications_list
        }
    )


@app.post("/notifications-ui/{notification_id}/read")
def mark_notification_as_read_ui(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_team_member_or_manager(request, db)

    if redirect_response:
        return redirect_response

    if current_user.role == "manager":
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id
        ).first()
    else:
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == current_user.id
        ).first()

    if notification:
        notification.is_read = 1
        db.commit()

    return RedirectResponse(url="/notifications-ui", status_code=303)


# ---------- Main UI Routes ----------

@app.get("/")
def dashboard_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "title": "Dashboard",
            "current_user": current_user
        }
    )


@app.get("/projects-ui")
def projects_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request,
            "title": "Projects",
            "current_user": current_user
        }
    )


@app.post("/projects-ui/{project_id}/delete")
def delete_project_ui(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    project = db.query(models.Project).filter(
        models.Project.id == project_id
    ).first()

    if not project:
        return RedirectResponse(url="/projects-ui", status_code=303)

    project_tasks = db.query(models.Task).filter(
        models.Task.project_id == project_id
    ).all()

    project_task_ids = [task.id for task in project_tasks]

    if project_task_ids:
        db.query(models.Assignment).filter(
            models.Assignment.task_id.in_(project_task_ids)
        ).delete(synchronize_session=False)

        db.query(models.TaskRequiredSkill).filter(
            models.TaskRequiredSkill.task_id.in_(project_task_ids)
        ).delete(synchronize_session=False)

    project_members = db.query(models.TeamMember).filter(
        models.TeamMember.project_id == project_id
    ).all()

    project_member_ids = [member.id for member in project_members]

    if project_member_ids:
        db.query(models.TeamMemberSkill).filter(
            models.TeamMemberSkill.team_member_id.in_(project_member_ids)
        ).delete(synchronize_session=False)

    db.query(models.Task).filter(
        models.Task.project_id == project_id
    ).delete(synchronize_session=False)

    db.query(models.TeamMember).filter(
        models.TeamMember.project_id == project_id
    ).delete(synchronize_session=False)

    db.delete(project)
    db.commit()

    return RedirectResponse(url="/projects-ui", status_code=303)


@app.get("/team-members-ui")
def team_members_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return templates.TemplateResponse(
        "team_members.html",
        {
            "request": request,
            "title": "Team Members",
            "current_user": current_user
        }
    )


@app.post("/team-members-ui/{team_member_id}/delete")
def delete_team_member_ui(
    team_member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == team_member_id
    ).first()

    if not team_member:
        return RedirectResponse(url="/team-members-ui", status_code=303)

    member_assignments = db.query(models.Assignment).filter(
        models.Assignment.team_member_id == team_member_id
    ).all()

    for assignment in member_assignments:
        release_task_from_assignment(assignment)
        db.delete(assignment)

    db.query(models.TeamMemberSkill).filter(
        models.TeamMemberSkill.team_member_id == team_member_id
    ).delete(synchronize_session=False)

    db.delete(team_member)
    db.commit()

    return RedirectResponse(url="/team-members-ui", status_code=303)


@app.post("/team-members-ui/{team_member_id}/create-user-account")
def create_team_member_user_account_ui(
    team_member_id: int,
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == team_member_id
    ).first()

    if not team_member:
        return RedirectResponse(url="/team-members-ui", status_code=303)

    if team_member.user_id:
        return RedirectResponse(
            url=f"/team-members-ui/{team_member_id}",
            status_code=303
        )

    existing_user = db.query(models.User).filter(
        models.User.email == email
    ).first()

    if existing_user:
        team_member.user_id = existing_user.id
        db.commit()

        return RedirectResponse(
            url=f"/team-members-ui/{team_member_id}",
            status_code=303
        )

    new_user = models.User(
        name=team_member.name,
        email=email,
        password_hash=hash_password(password),
        role="team_member"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    team_member.user_id = new_user.id
    db.commit()

    return RedirectResponse(
        url=f"/team-members-ui/{team_member_id}",
        status_code=303
    )


@app.get("/team-members-ui/{team_member_id}")
def team_member_profile_ui(
    team_member_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == team_member_id
    ).first()

    if not team_member:
        return RedirectResponse(url="/team-members-ui", status_code=303)

    project = db.query(models.Project).filter(
        models.Project.id == team_member.project_id
    ).first()

    linked_user = None

    if team_member.user_id:
        linked_user = db.query(models.User).filter(
            models.User.id == team_member.user_id
        ).first()

    team_member_skills = db.query(models.TeamMemberSkill).filter(
        models.TeamMemberSkill.team_member_id == team_member.id
    ).all()

    skills_list = []

    for team_member_skill in team_member_skills:
        skill = db.query(models.Skill).filter(
            models.Skill.id == team_member_skill.skill_id
        ).first()

        if skill:
            skills_list.append(skill)

    assignments_list = db.query(models.Assignment).filter(
        models.Assignment.team_member_id == team_member.id
    ).all()

    total_assignments = len(assignments_list)

    active_assignments = [
        assignment for assignment in assignments_list
        if assignment.status == "active"
    ]

    completed_assignments = [
        assignment for assignment in assignments_list
        if assignment.status == "completed"
    ]

    delayed_assignments = [
        assignment for assignment in assignments_list
        if assignment.task and assignment.task.status == "delayed"
    ]

    in_progress_assignments = [
        assignment for assignment in assignments_list
        if assignment.task and assignment.task.status == "in_progress"
    ]

    active_assignments_count = len(active_assignments)
    completed_assignments_count = len(completed_assignments)
    delayed_assignments_count = len(delayed_assignments)
    in_progress_assignments_count = len(in_progress_assignments)

    workload_status = calculate_employee_workload_status(active_assignments_count)

    completion_rate = calculate_completion_rate(
        total_assignments,
        completed_assignments_count
    )

    assignment_scores = []

    for assignment in assignments_list:
        assignment_score = get_assignment_score_safely(assignment)

        if assignment_score is not None:
            assignment_scores.append(assignment_score)

    if assignment_scores:
        average_assignment_score = round(
            sum(assignment_scores) / len(assignment_scores),
            2
        )
    else:
        average_assignment_score = None

    profile_summary = {
        "total_assignments": total_assignments,
        "active_assignments": active_assignments_count,
        "completed_assignments": completed_assignments_count,
        "delayed_assignments": delayed_assignments_count,
        "in_progress_assignments": in_progress_assignments_count,
        "completion_rate": completion_rate,
        "workload_status": workload_status,
        "average_assignment_score": average_assignment_score
    }

    return templates.TemplateResponse(
        "team_member_profile.html",
        {
            "request": request,
            "title": f"{team_member.name} Profile",
            "current_user": current_user,
            "team_member": team_member,
            "project": project,
            "linked_user": linked_user,
            "skills": skills_list,
            "assignments": assignments_list,
            "profile_summary": profile_summary
        }
    )


@app.get("/skills-ui")
def skills_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return templates.TemplateResponse(
        "skills.html",
        {
            "request": request,
            "title": "Skills",
            "current_user": current_user
        }
    )


@app.post("/skills-ui/team-members/{team_member_id}/skills/{skill_id}/remove")
def remove_team_member_skill_ui(
    team_member_id: int,
    skill_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    team_member_skill = db.query(models.TeamMemberSkill).filter(
        models.TeamMemberSkill.team_member_id == team_member_id,
        models.TeamMemberSkill.skill_id == skill_id
    ).first()

    if team_member_skill:
        db.delete(team_member_skill)
        db.commit()

    return RedirectResponse(url="/skills-ui", status_code=303)


@app.get("/tasks-ui")
def tasks_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "title": "Tasks",
            "current_user": current_user
        }
    )


@app.post("/tasks-ui/{task_id}/delete")
def delete_task_ui(
    task_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    task = db.query(models.Task).filter(
        models.Task.id == task_id
    ).first()

    if not task:
        return RedirectResponse(url="/tasks-ui", status_code=303)

    db.query(models.Assignment).filter(
        models.Assignment.task_id == task_id
    ).delete(synchronize_session=False)

    db.query(models.TaskRequiredSkill).filter(
        models.TaskRequiredSkill.task_id == task_id
    ).delete(synchronize_session=False)

    db.delete(task)
    db.commit()

    return RedirectResponse(url="/tasks-ui", status_code=303)


@app.get("/analytics-ui")
def analytics_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "title": "Analytics",
            "current_user": current_user
        }
    )


# ---------- Protected Swagger Routes ----------

@app.get("/docs", include_in_schema=False)
def protected_swagger_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Task Allocation Assistant - Swagger UI"
    )


@app.get("/openapi.json", include_in_schema=False)
def protected_openapi_schema(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_manager(request, db)

    if redirect_response:
        return redirect_response

    return app.openapi()


# ---------- API Utility Routes ----------

@app.get("/api")
def api_root():
    return {
        "message": "Task Allocation Assistant API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected"
    }


# ---------- Scheduler Events ----------

@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()