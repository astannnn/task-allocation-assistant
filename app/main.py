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
    role: str = Form(...),
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

    if role not in ["manager", "team_member"]:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "title": "Register",
                "error": "Invalid role",
                "current_user": None
            }
        )

    user = models.User(
        name=name,
        email=email,
        password_hash=hash_password(password),
        role=role
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
            "assignments": assignments
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


@app.get("/notifications-ui")
def notifications_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user, redirect_response = require_team_member_or_manager(request, db)

    if redirect_response:
        return redirect_response

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