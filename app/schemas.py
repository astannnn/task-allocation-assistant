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


# ---------- User Schemas ----------

class UserBase(BaseModel):
    name: str
    email: str
    role: str = "team_member"


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Scheduling Policy Schemas ----------

class SchedulingPolicyBase(BaseModel):
    name: str = "Balanced Policy"
    policy_type: str = "balanced"
    is_active: int = 0

    skill_weight: float = 0.30
    taxonomy_weight: float = 0.10
    availability_weight: float = 0.15
    workload_weight: float = 0.15
    reliability_weight: float = 0.10
    dynamic_status_weight: float = 0.07
    mood_weight: float = 0.03
    priority_weight: float = 0.05
    deadline_weight: float = 0.05

    minimum_score_threshold: float = 0.50
    max_workload_allowed: float = 0.90


class SchedulingPolicyCreate(SchedulingPolicyBase):
    pass


class SchedulingPolicyUpdate(BaseModel):
    name: Optional[str] = None
    policy_type: Optional[str] = None
    is_active: Optional[int] = None

    skill_weight: Optional[float] = None
    taxonomy_weight: Optional[float] = None
    availability_weight: Optional[float] = None
    workload_weight: Optional[float] = None
    reliability_weight: Optional[float] = None
    dynamic_status_weight: Optional[float] = None
    mood_weight: Optional[float] = None
    priority_weight: Optional[float] = None
    deadline_weight: Optional[float] = None

    minimum_score_threshold: Optional[float] = None
    max_workload_allowed: Optional[float] = None


class SchedulingPolicyResponse(SchedulingPolicyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True