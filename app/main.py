from fastapi import FastAPI

from app.database import Base, engine
from app.services.scheduler_service import start_scheduler, shutdown_scheduler
from app import models
from app.routers import projects, team_members, skills, tasks, assignments, analytics, notifications
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Allocation Assistant",
    description="A decision-support assistant for team task allocation and project management.",
    version="0.1.0",
)

app.include_router(analytics.router)
app.include_router(assignments.router)
app.include_router(tasks.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(team_members.router)
app.include_router(notifications.router)

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