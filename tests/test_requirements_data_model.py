from app.models import TeamMember, Task, Assignment, SchedulingPolicy


def test_SYS_PROFILE_01_team_member_profile_contains_all_scoring_fields():
    """
    SYS-PROFILE-01:
    Team member profile must contain all attributes required by the scoring logic.
    """

    columns = set(TeamMember.__table__.columns.keys())

    required_columns = {
        "role",
        "availability",
        "workload",
        "reliability",
        "dynamic_status",
        "mood_state",
        "project_id",
        "user_id",
    }

    assert required_columns.issubset(columns)


def test_SYS_TASK_01_task_contains_all_allocation_input_fields():
    """
    SYS-TASK-01:
    Task model must contain fields used by allocation and monitoring logic.
    """

    columns = set(Task.__table__.columns.keys())

    required_columns = {
        "project_id",
        "title",
        "priority",
        "deadline",
        "status",
        "estimated_effort",
    }

    assert required_columns.issubset(columns)


def test_SYS_ASSIGN_01_assignment_stores_score_at_assignment():
    """
    SYS-ASSIGN-01:
    Assignment must store score_at_assignment to keep evidence of the allocation decision.
    """

    columns = set(Assignment.__table__.columns.keys())

    assert "task_id" in columns
    assert "team_member_id" in columns
    assert "score_at_assignment" in columns
    assert "status" in columns


def test_SYS_POLICY_01_scheduling_policy_contains_configurable_weights_and_constraints():
    """
    SYS-POLICY-01:
    Scheduling policy must contain configurable weights, minimum threshold,
    and maximum workload constraint.
    """

    columns = set(SchedulingPolicy.__table__.columns.keys())

    required_columns = {
        "skill_weight",
        "taxonomy_weight",
        "availability_weight",
        "workload_weight",
        "reliability_weight",
        "dynamic_status_weight",
        "mood_weight",
        "priority_weight",
        "deadline_weight",
        "minimum_score_threshold",
        "max_workload_allowed",
        "is_active",
    }

    assert required_columns.issubset(columns)