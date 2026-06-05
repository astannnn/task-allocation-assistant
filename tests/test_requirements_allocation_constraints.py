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


def create_policy(max_workload_allowed=0.90, minimum_score_threshold=0.50):
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
        minimum_score_threshold=minimum_score_threshold,
        max_workload_allowed=max_workload_allowed,
    )


def create_backend_task():
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    task = models.Task(
        id=1,
        project_id=1,
        title="Implement backend API",
        priority="high",
        deadline=datetime.utcnow() + timedelta(days=2),
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


def create_backend_candidate(member_id, name, workload):
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    member = models.TeamMember(
        id=member_id,
        project_id=1,
        name=name,
        role="Backend Developer",
        availability=0.9,
        workload=workload,
        reliability=0.9,
        dynamic_status="normal",
        mood_state="positive",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=member_id,
            skill_id=1,
            level=0.9,
            skill=python_skill,
        ),
        models.TeamMemberSkill(
            team_member_id=member_id,
            skill_id=2,
            level=0.85,
            skill=fastapi_skill,
        ),
    ]

    return member


def test_SYS_ALLOC_04_overloaded_best_candidate_is_not_selected():
    """
    SYS-ALLOC-04:
    A candidate whose workload is above max_workload_allowed must not be selected
    automatically, even if the candidate has a strong score.
    """

    task = create_backend_task()
    policy = create_policy(max_workload_allowed=0.90)

    overloaded_candidate = create_backend_candidate(
        member_id=1,
        name="Overloaded Backend Developer",
        workload=0.95,
    )

    available_candidate = create_backend_candidate(
        member_id=2,
        name="Available Backend Developer",
        workload=0.30,
    )

    db = FakeDB(
        task=task,
        team_members=[overloaded_candidate, available_candidate],
        policy=policy,
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=task.id,
        db=db,
    )

    assert best_candidate is not None
    assert best_candidate["team_member_id"] == available_candidate.id
    assert best_candidate["team_member_name"] == "Available Backend Developer"

    overloaded_result = [
        candidate
        for candidate in candidate_scores
        if candidate["team_member_id"] == overloaded_candidate.id
    ][0]

    assert overloaded_result["violates_workload_constraint"] is True


def test_SYS_ALLOC_04_no_candidate_selected_when_all_candidates_overloaded():
    """
    SYS-ALLOC-04:
    If all candidates violate the workload constraint, the system must not
    select a candidate for automatic allocation.
    """

    task = create_backend_task()
    policy = create_policy(max_workload_allowed=0.90)

    overloaded_candidate_1 = create_backend_candidate(
        member_id=1,
        name="Overloaded Backend Developer 1",
        workload=0.95,
    )

    overloaded_candidate_2 = create_backend_candidate(
        member_id=2,
        name="Overloaded Backend Developer 2",
        workload=1.00,
    )

    db = FakeDB(
        task=task,
        team_members=[overloaded_candidate_1, overloaded_candidate_2],
        policy=policy,
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=task.id,
        db=db,
    )

    assert best_candidate is None
    assert len(candidate_scores) == 2
    assert all(
        candidate["violates_workload_constraint"] is True
        for candidate in candidate_scores
    )


def test_SYS_ALLOC_03_no_candidate_selected_when_score_below_threshold():
    """
    SYS-ALLOC-03:
    If candidate score is below minimum_score_threshold, the system must not
    select a candidate for automatic allocation.
    """

    task = create_backend_task()
    policy = create_policy(minimum_score_threshold=0.95)

    weak_candidate = create_backend_candidate(
        member_id=1,
        name="Weak Candidate",
        workload=0.20,
    )

    weak_candidate.availability = 0.2
    weak_candidate.reliability = 0.2
    weak_candidate.dynamic_status = "tired"
    weak_candidate.mood_state = "stressed"

    db = FakeDB(
        task=task,
        team_members=[weak_candidate],
        policy=policy,
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=task.id,
        db=db,
    )

    assert best_candidate is None
    assert len(candidate_scores) == 1
    assert candidate_scores[0]["score"] < policy.minimum_score_threshold