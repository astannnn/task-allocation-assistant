from datetime import datetime, timedelta

from app import models
from app.services.allocation_engine import find_best_team_member_for_task


class FakeQuery:
    """
    Small fake query object to simulate SQLAlchemy query/filter/first/all.
    This allows us to test allocation logic without a real database.
    """

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
    """
    Fake database session for unit testing.
    """

    def __init__(self, task, team_members):
        self.task = task
        self.team_members = team_members

    def query(self, model):
        if model == models.Task:
            return FakeQuery(self.task)

        if model == models.TeamMember:
            return FakeQuery(self.team_members)

        return FakeQuery([])


def create_skill(skill_id, name, skill_type="hard", category="backend_development"):
    return models.Skill(
        id=skill_id,
        name=name,
        type=skill_type,
        category=category,
    )


def create_task():
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    task = models.Task(
        id=1,
        project_id=1,
        title="Create backend API",
        description="Backend task",
        priority="critical",
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


def create_strong_candidate():
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")
    problem_solving_skill = create_skill(
        5,
        "Problem Solving",
        skill_type="soft",
        category="soft_skills",
    )

    member = models.TeamMember(
        id=1,
        project_id=1,
        name="Ali",
        role="Backend Developer",
        availability=0.9,
        workload=0.2,
        reliability=0.9,
        dynamic_status="normal",
        mood_state="positive",
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
            level=0.85,
            skill=fastapi_skill,
        ),
        models.TeamMemberSkill(
            team_member_id=1,
            skill_id=5,
            level=0.8,
            skill=problem_solving_skill,
        ),
    ]

    return member


def create_weak_candidate():
    javascript_skill = create_skill(
        3,
        "JavaScript",
        category="frontend_development",
    )

    member = models.TeamMember(
        id=2,
        project_id=1,
        name="Maria",
        role="Frontend Developer",
        availability=0.6,
        workload=0.4,
        reliability=0.7,
        dynamic_status="normal",
        mood_state="neutral",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=2,
            skill_id=3,
            level=0.9,
            skill=javascript_skill,
        ),
    ]

    return member


def create_unavailable_candidate():
    python_skill = create_skill(1, "Python")

    member = models.TeamMember(
        id=3,
        project_id=1,
        name="John",
        role="Backend Developer",
        availability=0.1,
        workload=1.0,
        reliability=0.3,
        dynamic_status="unavailable",
        mood_state="stressed",
    )

    member.skills = [
        models.TeamMemberSkill(
            team_member_id=3,
            skill_id=1,
            level=0.4,
            skill=python_skill,
        ),
    ]

    return member


def test_find_best_team_member_returns_strongest_candidate():
    task = create_task()
    strong_candidate = create_strong_candidate()
    weak_candidate = create_weak_candidate()

    db = FakeDB(
        task=task,
        team_members=[weak_candidate, strong_candidate],
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=1,
        db=db,
    )

    assert best_candidate is not None
    assert best_candidate["team_member_id"] == strong_candidate.id
    assert best_candidate["team_member_name"] == "Ali"
    assert best_candidate["score"] > 0.8
    assert len(candidate_scores) == 2


def test_candidate_scores_are_sorted_descending():
    task = create_task()
    strong_candidate = create_strong_candidate()
    weak_candidate = create_weak_candidate()

    db = FakeDB(
        task=task,
        team_members=[weak_candidate, strong_candidate],
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=1,
        db=db,
    )

    assert candidate_scores[0]["score"] >= candidate_scores[1]["score"]
    assert candidate_scores[0]["team_member_name"] == "Ali"


def test_candidate_response_contains_explanation_and_breakdown():
    task = create_task()
    strong_candidate = create_strong_candidate()

    db = FakeDB(
        task=task,
        team_members=[strong_candidate],
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=1,
        db=db,
    )

    candidate = candidate_scores[0]

    assert "score_breakdown" in candidate
    assert "explanation" in candidate
    assert "taxonomy_explanation" in candidate
    assert "required_skills" in candidate
    assert "member_skills" in candidate

    assert "skill_match" in candidate["score_breakdown"]
    assert "taxonomy_match" in candidate["score_breakdown"]
    assert "priority_score" in candidate["score_breakdown"]
    assert "deadline_urgency_score" in candidate["score_breakdown"]


def test_returns_none_when_no_candidate_reaches_threshold():
    task = create_task()
    unavailable_candidate = create_unavailable_candidate()

    db = FakeDB(
        task=task,
        team_members=[unavailable_candidate],
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=1,
        db=db,
    )

    assert best_candidate is None
    assert len(candidate_scores) == 1
    assert candidate_scores[0]["score"] < 0.5


def test_returns_none_when_task_not_found():
    db = FakeDB(
        task=None,
        team_members=[],
    )

    best_candidate, candidate_scores = find_best_team_member_for_task(
        task_id=999,
        db=db,
    )

    assert best_candidate is None
    assert candidate_scores == []