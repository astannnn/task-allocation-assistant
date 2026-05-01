from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ---------- Project Schemas ----------

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class ProjectCreate(ProjectBase):
    created_by: Optional[int] = None


class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


# ---------- Team Member Schemas ----------

class TeamMemberBase(BaseModel):
    name: str
    role: Optional[str] = None
    availability: float = 1.0
    workload: float = 0.0
    reliability: float = 0.7
    dynamic_status: str = "normal"
    mood_state: str = "neutral"


class TeamMemberCreate(TeamMemberBase):
    project_id: int
    user_id: Optional[int] = None


class TeamMemberResponse(TeamMemberBase):
    id: int
    project_id: int
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


# ---------- Skill Schemas ----------

class SkillBase(BaseModel):
    name: str
    type: str
    category: Optional[str] = None


class SkillCreate(SkillBase):
    pass


class SkillResponse(SkillBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Task Schemas ----------

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    deadline: Optional[datetime] = None
    status: str = "open"
    estimated_effort: float = 0.2


class TaskCreate(TaskBase):
    project_id: int


class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Team Member Skill Schemas ----------

class TeamMemberSkillCreate(BaseModel):
    team_member_id: int
    skill_id: int
    level: float = 0.5


class TeamMemberSkillResponse(BaseModel):
    id: int
    team_member_id: int
    skill_id: int
    level: float

    class Config:
        from_attributes = True

# ---------- Task Required Skill Schemas ----------

class TaskRequiredSkillCreate(BaseModel):
    task_id: int
    skill_id: int
    required_level: float = 0.5


class TaskRequiredSkillResponse(BaseModel):
    id: int
    task_id: int
    skill_id: int
    required_level: float

    class Config:
        from_attributes = True

# ---------- Assignment Schemas ----------

class AssignmentResponse(BaseModel):
    id: int
    task_id: int
    team_member_id: int
    status: str
    score_at_assignment: Optional[float] = None

    class Config:
        from_attributes = True