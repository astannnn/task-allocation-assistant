from datetime import datetime, timedelta

from app import models
from app.services.profile_scoring import (
    calculate_skill_match_score,
    calculate_availability_score,
    calculate_workload_score,
    calculate_reliability_score,
    calculate_dynamic_status_score,
    calculate_mood_score,
    calculate_taxonomy_match_score,
    calculate_priority_score,
    calculate_deadline_urgency_score,
    calculate_profile_score_breakdown,
)


def create_test_task():
    python_skill = models.Skill(
        id=1,
        name="Python",
        type="hard",
        category="backend_development",
    )

    fastapi_skill = models.Skill(
        id=2,
        name="FastAPI",
        type="hard",
        category="backend_development",
    )

    task = models.Task(
        id=1,
        project_id=1,
        title="Create authentication module",
        description="Backend authentication task",
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


def create_test_team_member():
    python_skill = models.Skill(
        id=1,
        name="Python",
        type="hard",
        category="backend_development",
    )

    fastapi_skill = models.Skill(
        id=2,
        name="FastAPI",
        type="hard",
        category="backend_development",
    )

    member = models.TeamMember(
        id=1,
        project_id=1,
        name="Ali",
        role="Backend Developer",
        availability=0.9,
        workload=0.2,
        reliability=0.85,
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
    ]

    return member


def test_skill_match_score_for_strong_candidate():
    task = create_test_task()
    member = create_test_team_member()

    score = calculate_skill_match_score(task, member)

    assert score == 1.0


def test_availability_score():
    member = create_test_team_member()

    score = calculate_availability_score(member)

    assert score == 0.9


def test_workload_score():
    member = create_test_team_member()

    score = calculate_workload_score(member)

    assert score == 0.8


def test_reliability_score():
    member = create_test_team_member()

    score = calculate_reliability_score(member)

    assert score == 0.85


def test_dynamic_status_score():
    member = create_test_team_member()

    score = calculate_dynamic_status_score(member)

    assert score == 1.0


def test_mood_score():
    member = create_test_team_member()

    score = calculate_mood_score(member)

    assert score == 1.0


def test_taxonomy_match_score_for_backend_task_and_backend_developer():
    task = create_test_task()
    member = create_test_team_member()

    score = calculate_taxonomy_match_score(task, member)

    assert score == 1.0


def test_priority_score_for_critical_task():
    task = create_test_task()

    score = calculate_priority_score(task)

    assert score == 1.0


def test_deadline_urgency_score_for_close_deadline():
    task = create_test_task()

    score = calculate_deadline_urgency_score(task)

    assert score == 0.8


def test_profile_score_breakdown_contains_all_expected_fields():
    task = create_test_task()
    member = create_test_team_member()

    breakdown = calculate_profile_score_breakdown(task, member)

    assert "skill_match" in breakdown
    assert "taxonomy_match" in breakdown
    assert "availability" in breakdown
    assert "workload_score" in breakdown
    assert "reliability" in breakdown
    assert "dynamic_status_score" in breakdown
    assert "mood_score" in breakdown
    assert "priority_score" in breakdown
    assert "deadline_urgency_score" in breakdown
    assert "weights" in breakdown
    assert "final_score" in breakdown

    assert breakdown["skill_match"] == 1.0
    assert breakdown["taxonomy_match"] == 1.0
    assert breakdown["priority_score"] == 1.0
    assert breakdown["deadline_urgency_score"] == 0.8
    assert breakdown["final_score"] > 0.8