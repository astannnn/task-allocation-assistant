import json
from datetime import datetime, timedelta

from app import models
from app.services.allocation_decision_service import record_allocation_decision
from app.services.allocation_engine import automatically_allocate_task


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
    def __init__(self, task=None, team_members=None, assignments=None, policy=None):
        self.task = task
        self.team_members = team_members or []
        self.assignments = assignments or []
        self.policy = policy
        self.added_objects = []
        self.committed = False

    def query(self, model):
        if model == models.Task:
            return FakeQuery(self.task)

        if model == models.TeamMember:
            return FakeQuery(self.team_members)

        if model == models.Assignment:
            return FakeQuery(self.assignments)

        if model == models.SchedulingPolicy:
            return FakeQuery(self.policy)

        if model == models.AllocationDecision:
            decisions = [
                obj for obj in self.added_objects
                if isinstance(obj, models.AllocationDecision)
            ]
            return FakeQuery(decisions)

        return FakeQuery([])

    def add(self, obj):
        self.added_objects.append(obj)

        if isinstance(obj, models.Assignment):
            if obj.id is None:
                obj.id = len(self.assignments) + 1
            self.assignments.append(obj)

        if isinstance(obj, models.AllocationDecision):
            if obj.id is None:
                obj.id = len([
                    item for item in self.added_objects
                    if isinstance(item, models.AllocationDecision)
                ])

    def commit(self):
        self.committed = True

    def refresh(self, obj):
        return obj


def create_skill(skill_id, name, category="backend_development"):
    return models.Skill(
        id=skill_id,
        name=name,
        type="hard",
        category=category,
    )


def create_policy(minimum_score_threshold=0.50, max_workload_allowed=0.90):
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


def create_task():
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


def create_candidate(member_id=1, workload=0.2):
    python_skill = create_skill(1, "Python")
    fastapi_skill = create_skill(2, "FastAPI")

    member = models.TeamMember(
        id=member_id,
        project_id=1,
        name="Ali",
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
            level=0.8,
            skill=fastapi_skill,
        ),
    ]

    return member


def test_CCL_AUDIT_01_record_allocation_decision_stores_score_breakdown_as_json():
    """
    CCL-AUDIT-01:
    Allocation decision evidence must be stored as JSON.
    """

    task = create_task()
    policy = create_policy()

    db = FakeDB(
        task=task,
        team_members=[],
        policy=policy,
    )

    decision = record_allocation_decision(
        db=db,
        task_id=task.id,
        decision_type="automatic_assignment",
        selected_team_member_id=1,
        final_score=0.87,
        score_breakdown={
            "skill_match": 1.0,
            "workload_score": 0.8,
            "final_score": 0.87,
        },
        reason="Best candidate selected because of strong skill match.",
        policy_name="Balanced Policy",
    )

    saved_json = json.loads(decision.score_breakdown_json)

    assert decision.task_id == task.id
    assert decision.selected_team_member_id == 1
    assert decision.decision_type == "automatic_assignment"
    assert decision.final_score == 0.87
    assert saved_json["skill_match"] == 1.0
    assert saved_json["workload_score"] == 0.8
    assert decision.policy_name == "Balanced Policy"


def test_CCL_AUDIT_02_successful_automatic_allocation_creates_decision_log():
    """
    CCL-AUDIT-02:
    Successful automatic allocation must create an audit decision record.
    """

    task = create_task()
    candidate = create_candidate()
    policy = create_policy()

    db = FakeDB(
        task=task,
        team_members=[candidate],
        assignments=[],
        policy=policy,
    )

    result = automatically_allocate_task(
        task_id=task.id,
        db=db,
    )

    decisions = [
        obj for obj in db.added_objects
        if isinstance(obj, models.AllocationDecision)
    ]

    assert result["success"] is True
    assert len(decisions) == 1

    decision = decisions[0]

    assert decision.task_id == task.id
    assert decision.selected_team_member_id == candidate.id
    assert decision.decision_type == "automatic_assignment"
    assert decision.final_score is not None
    assert decision.policy_name == "Balanced Policy"
    assert decision.reason is not None


def test_CCL_AUDIT_03_manual_review_fallback_creates_decision_log():
    """
    CCL-AUDIT-03:
    Manual review fallback must also create an audit decision record.
    """

    task = create_task()
    overloaded_candidate = create_candidate(workload=1.0)
    policy = create_policy(max_workload_allowed=0.90)

    db = FakeDB(
        task=task,
        team_members=[overloaded_candidate],
        assignments=[],
        policy=policy,
    )

    result = automatically_allocate_task(
        task_id=task.id,
        db=db,
    )

    decisions = [
        obj for obj in db.added_objects
        if isinstance(obj, models.AllocationDecision)
    ]

    assert result["success"] is False
    assert task.status == "manual_review"
    assert len(decisions) == 1

    decision = decisions[0]

    assert decision.task_id == task.id
    assert decision.selected_team_member_id is None
    assert decision.decision_type == "manual_review"
    assert decision.reason == "No suitable team member found during automatic allocation."