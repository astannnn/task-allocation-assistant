import time
from datetime import datetime, timedelta

from app import models
from app.services.allocation_engine import find_best_team_member_for_task


class FakeQuery:
    def __init__(self, data):
        self.data = data

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        if isinstance(self.data, list):
            return self.data[0] if self.data else None
        return self.data

    def all(self):
        if isinstance(self.data, list):
            return list(self.data)
        return [self.data]


class FakeDB:
    def __init__(self, task, team_members, policy):
        self.task = task
        self.team_members = team_members
        self.policy = policy

    def query(self, model):
        if model == models.Task:
            return FakeQuery(self.task)

        if model == models.TeamMember:
            return FakeQuery(self.team_members)

        if model == models.SchedulingPolicy:
            return FakeQuery(self.policy)

        return FakeQuery([])


def create_skill(skill_id, name, category="backend_development"):
    return models.Skill(
        id=skill_id,
        name=name,
        type="hard",
        category=category,
    )


def create_policy():
    return models.SchedulingPolicy(
        id=1,
        name="Balanced Policy",
        policy_type="balanced",
        is_active=1,
        skill_weight=0.30,
        taxonomy_weight=0.10,
        availability_weight=0.15,
        workload_weight=0.15,
        reliability_weight=0.10,
        dynamic_status_weight=0.07,
        mood_weight=0.03,
        priority_weight=0.05,
        deadline_weight=0.05,
        minimum_score_threshold=0.50,
        max_workload_allowed=0.90,
    )


def create_task():
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    task = models.Task(
        id=1,
        project_id=1,
        title="Implement backend API",
        priority="high",
        deadline=datetime.utcnow() + timedelta(days=3),
        status="open",
        estimated_effort=0.3,
    )

    task.required_skills = [
        models.TaskRequiredSkill(
            task_id=1,
            skill_id=1,
            required_level=0.7,
            skill=python_skill,
        ),
        models.TaskRequiredSkill(
            task_id=1,
            skill_id=2,
            required_level=0.6,
            skill=fastapi_skill,
        ),
    ]

    return task


def create_candidate(member_id):
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    member = models.TeamMember(
        id=member_id,
        project_id=1,
        name=f"Candidate {member_id}",
        role="Backend Developer",
        availability=0.8,
        workload=0.2,
        reliability=0.8,
        dynamic_status="normal",
        mood_state="neutral",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=member_id,
            skill_id=1,
            level=0.8,
            skill=python_skill,
        ),
        models.TeamMemberSkill(
            team_member_id=member_id,
            skill_id=2,
            level=0.8,
            skill=fastapi_skill,
        ),
    ]

    return member


def test_NFR_PERF_01_allocation_preview_for_50_candidates_under_2_seconds():
    """
    NFR-PERF-01:
    Allocation preview for a small/medium team must finish under an acceptable time limit.

    Acceptance criterion:
    Evaluating 50 candidates must take less than 2 seconds in the local academic environment.
    """

    task = create_task()
    policy = create_policy()
    candidates = [create_candidate(member_id=i) for i in range(1, 51)]

    db = FakeDB(
        task=task,
        team_members=candidates,
        policy=policy,
    )

    start_time = time.perf_counter()

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=task.id,
        db=db,
    )

    elapsed_time = time.perf_counter() - start_time

    assert best_candidate is not None
    assert len(candidate_scores) == 50
    assert elapsed_time < 2.0