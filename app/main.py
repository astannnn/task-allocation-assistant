from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import Base, engine
from app.services.scheduler_service import start_scheduler, shutdown_scheduler
from app import models
from app.routers import projects, team_members, skills, tasks, assignments, analytics, notifications, project_templates
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Allocation Assistant",
    description="A decision-support assistant for team task allocation and project management.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.include_router(analytics.router)
app.include_router(assignments.router)
app.include_router(tasks.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(team_members.router)
app.include_router(notifications.router)
app.include_router(project_templates.router)

@app.get("/")
def dashboard_ui(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "title": "Dashboard"}
    )

@app.get("/projects-ui")
def projects_ui(request: Request):
    return templates.TemplateResponse(
        "projects.html",
        {"request": request, "title": "Projects"}
    )


@app.get("/team-members-ui")
def team_members_ui(request: Request):
    return templates.TemplateResponse(
        "team_members.html",
        {"request": request, "title": "Team Members"}
    )


@app.get("/tasks-ui")
def tasks_ui(request: Request):
    return templates.TemplateResponse(
        "tasks.html",
        {"request": request, "title": "Tasks"}
    )


@app.get("/analytics-ui")
def analytics_ui(request: Request):
    return templates.TemplateResponse(
        "analytics.html",
        {"request": request, "title": "Analytics"}
    )

@app.get("/")
def root():
    return {
        "message": "Task Allocation Assistant is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "database": "connected"
    }

@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()