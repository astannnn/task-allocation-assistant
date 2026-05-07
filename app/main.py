from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import RedirectResponse
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
            "error": None
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
                "error": "User with this email already exists"
            }
        )

    if role not in ["manager", "team_member"]:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "title": "Register",
                "error": "Invalid role"
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
            "error": None
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
                "error": "Invalid email or password"
            }
        )

    request.session["user_id"] = user.id
    request.session["user_role"] = user.role

    return redirect_after_login(user)


@app.get("/logout")
def logout_user(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)


@app.get("/my-tasks")
def my_tasks_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

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

@app.get("/notifications-ui")
def notifications_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    notifications = db.query(models.Notification).filter(
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
            "notifications": notifications
        }
    )


# ---------- Main UI Routes ----------

@app.get("/")
def dashboard_ui(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

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
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

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
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

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
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

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
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

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
    current_user = get_current_user(request, db)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "title": "Analytics",
            "current_user": current_user
        }
    )


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