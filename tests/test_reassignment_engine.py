from datetime import datetime, timedelta

from app import models
from app.services.reassignment_engine import (
    find_current_active_assignment,
    find_replacement_for_delayed_task,
)


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
            return self.data
        return [self.data]


class FakeDB:
    def __init__(self, task, team_members, active_assignment=None):
        self.task = task
        self.team_members = team_members
        self.active_assignment = active_assignment

    def query(self, model):
        if model == models.Task:
            return FakeQuery(self.task)

        if model == models.TeamMember:
            return FakeQuery(self.team_members)

        if model == models.Assignment:
            return FakeQuery(self.active_assignment)

        return FakeQuery([])


def create_skill(skill_id, name, skill_type="hard", category="backend_development"):
    return models.Skill(
        id=skill_id,
        name=name,
        type=skill_type,
        category=category,
    )


def create_delayed_task():
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    task = models.Task(
        id=1,
        project_id=1,
        title="Fix delayed backend API task",
        description="Delayed backend task",
        priority="critical",
        deadline=datetime.utcnow() + timedelta(days=1),
        status="delayed",
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
            required_level=0.7,
            skill=fastapi_skill,
        ),
    ]

    return task


def create_current_assignee():
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    member = models.TeamMember(
        id=1,
        project_id=1,
        name="Ali",
        role="Backend Developer",
        availability=0.8,
        workload=0.6,
        reliability=0.8,
        dynamic_status="normal",
        mood_state="neutral",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=1,
            skill_id=1,
            level=0.9,
            skill=python_skill,
        ),
        models.TeamMemberSkill(
            team_member_id=1,
            skill_id=2,
            level=0.8,
            skill=fastapi_skill,
        ),
    ]

    return member


def create_strong_replacement():
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    member = models.TeamMember(
        id=2,
        project_id=1,
        name="Maria",
        role="Backend Developer",
        availability=0.95,
        workload=0.1,
        reliability=0.95,
        dynamic_status="normal",
        mood_state="positive",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=2,
            skill_id=1,
            level=0.95,
            skill=python_skill,
        ),
        models.TeamMemberSkill(
            team_member_id=2,
            skill_id=2,
            level=0.9,
            skill=fastapi_skill,
        ),
    ]

    return member


def create_weak_replacement():
    javascript_skill = create_skill(
        3,
        "JavaScript",
        category="frontend_development",
    )

    member = models.TeamMember(
        id=3,
        project_id=1,
        name="John",
        role="Frontend Developer",
        availability=0.5,
        workload=0.8,
        reliability=0.5,
        dynamic_status="normal",
        mood_state="stressed",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=3,
            skill_id=3,
            level=0.8,
            skill=javascript_skill,
        ),
    ]

    return member


def create_unavailable_replacement():
    python_skill = create_skill(1, "Python")

    member = models.TeamMember(
        id=4,
        project_id=1,
        name="Sara",
        role="Backend Developer",
        availability=0.9,
        workload=0.1,
        reliability=0.9,
        dynamic_status="unavailable",
        mood_state="positive",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=4,
            skill_id=1,
            level=0.9,
            skill=python_skill,
        ),
    ]

    return member


def create_active_assignment():
    return models.Assignment(
        id=1,
        task_id=1,
        team_member_id=1,
        status="active",
        score_at_assignment=0.85,
    )


def test_find_current_active_assignment_returns_assignment():
    task = create_delayed_task()
    current_assignee = create_current_assignee()
    active_assignment = create_active_assignment()

    db = FakeDB(
        task=task,
        team_members=[current_assignee],
        active_assignment=active_assignment,
    )

    result = find_current_active_assignment(task_id=1, db=db)

    assert result is not None
    assert result.id == 1
    assert result.status == "active"
    assert result.team_member_id == current_assignee.id


def test_replacement_search_excludes_current_assignee():
    task = create_delayed_task()
    current_assignee = create_current_assignee()
    strong_replacement = create_strong_replacement()
    active_assignment = create_active_assignment()

    db = FakeDB(
        task=task,
        team_members=[current_assignee, strong_replacement],
        active_assignment=active_assignment,
    )

    best_candidate, candidate_scores = find_replacement_for_delayed_task(
        task_id=1,
        db=db,
    )

    candidate_ids = [candidate["team_member_id"] for candidate in candidate_scores]

    assert current_assignee.id not in candidate_ids
    assert strong_replacement.id in candidate_ids
    assert best_candidate["team_member_id"] == strong_replacement.id


def test_replacement_search_excludes_unavailable_members():
    task = create_delayed_task()
    current_assignee = create_current_assignee()
    strong_replacement = create_strong_replacement()
    unavailable_replacement = create_unavailable_replacement()
    active_assignment = create_active_assignment()

    db = FakeDB(
        task=task,
        team_members=[
            current_assignee,
            strong_replacement,
            unavailable_replacement,
        ],
        active_assignment=active_assignment,
    )

    best_candidate, candidate_scores = find_replacement_for_delayed_task(
        task_id=1,
        db=db,
    )

    candidate_ids = [candidate["team_member_id"] for candidate in candidate_scores]

    assert unavailable_replacement.id not in candidate_ids
    assert strong_replacement.id in candidate_ids
    assert best_candidate["team_member_id"] == strong_replacement.id


def test_replacement_candidates_are_sorted_by_score():
    task = create_delayed_task()
    current_assignee = create_current_assignee()
    strong_replacement = create_strong_replacement()
    weak_replacement = create_weak_replacement()
    active_assignment = create_active_assignment()

    db = FakeDB(
        task=task,
        team_members=[
            current_assignee,
            weak_replacement,
            strong_replacement,
        ],
        active_assignment=active_assignment,
    )

    best_candidate, candidate_scores = find_replacement_for_delayed_task(
        task_id=1,
        db=db,
    )

    assert best_candidate["team_member_name"] == "Maria"
    assert candidate_scores[0]["score"] >= candidate_scores[1]["score"]


def test_replacement_candidate_contains_explanation_and_breakdown():
    task = create_delayed_task()
    current_assignee = create_current_assignee()
    strong_replacement = create_strong_replacement()
    active_assignment = create_active_assignment()

    db = FakeDB(
        task=task,
        team_members=[current_assignee, strong_replacement],
        active_assignment=active_assignment,
    )

    best_candidate, candidate_scores = find_replacement_for_delayed_task(
        task_id=1,
        db=db,
    )

    candidate = candidate_scores[0]

    assert best_candidate is not None
    assert "score_breakdown" in candidate
    assert "explanation" in candidate
    assert "taxonomy_explanation" in candidate
    assert "required_skills" in candidate
    assert "member_skills" in candidate
    assert "skill_match" in candidate["score_breakdown"]
    assert "final_score" in candidate["score_breakdown"]


def test_returns_none_when_task_not_found():
    db = FakeDB(
        task=None,
        team_members=[],
        active_assignment=None,
    )

    best_candidate, candidate_scores = find_replacement_for_delayed_task(
        task_id=999,
        db=db,
    )

    assert best_candidate is None
    assert candidate_scores == []