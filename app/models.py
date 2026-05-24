from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # manager or team_member

    projects = relationship("Project", back_populates="creator")
    notifications = relationship("Notification", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    created_by = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="projects")
    team_members = relationship("TeamMember", back_populates="project")
    tasks = relationship("Task", back_populates="project")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    name = Column(String, nullable=False)
    role = Column(String, nullable=True)

    availability = Column(Float, default=1.0)      # 0.0 - 1.0
    workload = Column(Float, default=0.0)          # 0.0 - 1.0
    reliability = Column(Float, default=0.7)       # 0.0 - 1.0
    dynamic_status = Column(String, default="normal")  # normal, busy, tired, unavailable
    mood_state = Column(String, default="neutral")     # positive, neutral, stressed

    project = relationship("Project", back_populates="team_members")
    skills = relationship("TeamMemberSkill", back_populates="team_member")
    assignments = relationship("Assignment", back_populates="team_member")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # hard or soft
    category = Column(String, nullable=True)

    team_members = relationship("TeamMemberSkill", back_populates="skill")
    task_requirements = relationship("TaskRequiredSkill", back_populates="skill")


class TeamMemberSkill(Base):
    __tablename__ = "team_member_skills"

    id = Column(Integer, primary_key=True, index=True)

    team_member_id = Column(Integer, ForeignKey("team_members.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))

    level = Column(Float, default=0.5)  # 0.0 - 1.0

    team_member = relationship("TeamMember", back_populates="skills")
    skill = relationship("Skill", back_populates="team_members")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("projects.id"))

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, default="medium")  # low, medium, high, critical
    deadline = Column(DateTime, nullable=True)
    status = Column(String, default="open")  # open, assigned, in_progress, completed, delayed, manual_review
    estimated_effort = Column(Float, default=0.2)  # 0.0 - 1.0

    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="tasks")
    required_skills = relationship("TaskRequiredSkill", back_populates="task")
    assignments = relationship("Assignment", back_populates="task")


class TaskRequiredSkill(Base):
    __tablename__ = "task_required_skills"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("tasks.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))

    required_level = Column(Float, default=0.5)  # 0.0 - 1.0

    task = relationship("Task", back_populates="required_skills")
    skill = relationship("Skill", back_populates="task_requirements")


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)

    task_id = Column(Integer, ForeignKey("tasks.id"))
    team_member_id = Column(Integer, ForeignKey("team_members.id"))

    assigned_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="active")  # active, completed, reassigned
    score_at_assignment = Column(Float, nullable=True)

    task = relationship("Task", back_populates="assignments")
    team_member = relationship("TeamMember", back_populates="assignments")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    message = Column(Text, nullable=False)
    type = Column(String, default="info")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Integer, default=0)

    user = relationship("User", back_populates="notifications")

class SchedulingPolicy(Base):
    __tablename__ = "scheduling_policies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, default="Balanced Policy")
    policy_type = Column(String, default="balanced")
    is_active = Column(Integer, default=0)

    skill_weight = Column(Float, default=0.30)
    taxonomy_weight = Column(Float, default=0.10)
    availability_weight = Column(Float, default=0.15)
    workload_weight = Column(Float, default=0.15)
    reliability_weight = Column(Float, default=0.10)
    dynamic_status_weight = Column(Float, default=0.07)
    mood_weight = Column(Float, default=0.03)
    priority_weight = Column(Float, default=0.05)
    deadline_weight = Column(Float, default=0.05)

    minimum_score_threshold = Column(Float, default=0.50)
    max_workload_allowed = Column(Float, default=0.90)

    created_at = Column(DateTime, default=datetime.utcnow)