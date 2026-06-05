from app import models
from app.services.team_member_lifecycle_service import delete_team_member_safely


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
    def __init__(self, team_member=None, tasks=None, assignments=None, skill_links=None):
        self.team_member = team_member
        self.tasks = tasks or []
        self.assignments = assignments or []
        self.skill_links = skill_links or []
        self.deleted_objects = []
        self.committed = False

    def query(self, model):
        if model == models.TeamMember:
            return FakeQuery(self.team_member)

        if model == models.Task:
            return FakeQuery(self.tasks)

        if model == models.Assignment:
            return FakeQuery(self.assignments)

        if model == models.TeamMemberSkill:
            return FakeQuery(self.skill_links)

        return FakeQuery([])

    def delete(self, obj):
        self.deleted_objects.append(obj)

        if isinstance(obj, models.TeamMemberSkill) and obj in self.skill_links:
            self.skill_links.remove(obj)

        if isinstance(obj, models.TeamMember):
            self.team_member = None

    def commit(self):
        self.committed = True


def test_NFR_REL_01_delete_team_member_releases_active_task_and_closes_assignment():
    """
    NFR-REL-01:
    Deleting a team member with active assignment must not leave inconsistent data.
    Assigned task must be moved to manual_review, and assignment must be closed.
    """

    team_member = models.TeamMember(
        id=1,
        project_id=1,
        name="Ali",
        role="Backend Developer",
    )

    task = models.Task(
        id=10,
        project_id=1,
        title="Implement API",
        status="assigned",
    )

    assignment = models.Assignment(
        id=100,
        task_id=task.id,
        team_member_id=team_member.id,
        status="active",
        score_at_assignment=0.85,
    )

    skill_link = models.TeamMemberSkill(
        id=200,
        team_member_id=team_member.id,
        skill_id=1,
        level=0.9,
    )

    db = FakeDB(
        team_member=team_member,
        tasks=[task],
        assignments=[assignment],
        skill_links=[skill_link],
    )

    result = delete_team_member_safely(
        team_member_id=team_member.id,
        db=db,
    )

    assert result is not None
    assert result["deleted_team_member_id"] == team_member.id
    assert task.status == "manual_review"
    assert assignment.status == "reassigned"
    assert assignment.team_member_id is None
    assert skill_link in db.deleted_objects
    assert team_member in db.deleted_objects
    assert db.committed is True


def test_NFR_REL_01_completed_task_status_is_not_changed_when_member_deleted():
    """
    NFR-REL-01:
    Completed tasks should not be moved back to manual review.
    """

    team_member = models.TeamMember(
        id=1,
        project_id=1,
        name="Ali",
        role="Backend Developer",
    )

    completed_task = models.Task(
        id=11,
        project_id=1,
        title="Completed task",
        status="completed",
    )

    assignment = models.Assignment(
        id=101,
        task_id=completed_task.id,
        team_member_id=team_member.id,
        status="completed",
        score_at_assignment=0.80,
    )

    db = FakeDB(
        team_member=team_member,
        tasks=[completed_task],
        assignments=[assignment],
        skill_links=[],
    )

    result = delete_team_member_safely(
        team_member_id=team_member.id,
        db=db,
    )

    assert result is not None
    assert completed_task.status == "completed"
    assert assignment.status == "reassigned"
    assert assignment.team_member_id is None
    assert db.committed is True


def test_NFR_REL_01_delete_missing_team_member_returns_none():
    """
    NFR-REL-01:
    If the team member does not exist, the safe delete service returns None.
    """

    db = FakeDB(
        team_member=None,
        tasks=[],
        assignments=[],
        skill_links=[],
    )

    result = delete_team_member_safely(
        team_member_id=999,
        db=db,
    )

    assert result is None
    assert db.committed is False