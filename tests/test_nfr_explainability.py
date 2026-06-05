from datetime import datetime, timedelta

from app.models import TeamMember, Task, Skill, TeamMemberSkill, TaskRequiredSkill
from app.services.profile_scoring import (
    calculate_profile_score_breakdown,
    generate_profile_score_explanation,
)


def _build_task_and_member():
    python_skill = Skill(id=1, name="Python", type="hard", category="backend")
    fastapi_skill = Skill(id=2, name="FastAPI", type="hard", category="backend")

    task = Task(
        id=1,
        project_id=1,
        title="Implement allocation endpoint",
        priority="high",
        deadline=datetime.utcnow() + timedelta(days=2),
        status="open",
        estimated_effort=0.5,
    )

    task.required_skills = [
        TaskRequiredSkill(
            task_id=1,
            skill_id=1,
            skill=python_skill,
            required_level=0.8,
        ),
        TaskRequiredSkill(
            task_id=1,
            skill_id=2,
            skill=fastapi_skill,
            required_level=0.7,
        ),
    ]

    member = TeamMember(
        id=1,
        project_id=1,
        name="Ali Karimov",
        role="Backend Developer",
        availability=0.9,
        workload=0.2,
        reliability=0.85,
        dynamic_status="normal",
        mood_state="positive",
    )

    member.skills = [
        TeamMemberSkill(
            team_member_id=1,
            skill_id=1,
            skill=python_skill,
            level=0.9,
        ),
        TeamMemberSkill(
            team_member_id=1,
            skill_id=2,
            skill=fastapi_skill,
            level=0.8,
        ),
    ]

    return task, member


def test_NFR_EXP_01_score_breakdown_contains_all_scoring_factors():
    """
    NFR-EXP-01:
    Allocation decisions must be explainable.
    The scoring result must contain all scoring factors used in the final decision.
    """

    task, member = _build_task_and_member()

    breakdown = calculate_profile_score_breakdown(task, member)

    required_keys = {
        "skill_match",
        "taxonomy_match",
        "availability",
        "workload_score",
        "reliability",
        "dynamic_status_score",
        "mood_score",
        "priority_score",
        "deadline_urgency_score",
        "weights",
        "policy",
        "final_score",
    }

    assert required_keys.issubset(breakdown.keys())


def test_NFR_EXP_01_score_breakdown_values_are_normalized():
    """
    NFR-EXP-01:
    All scoring components must be normalized between 0.0 and 1.0.
    """

    task, member = _build_task_and_member()

    breakdown = calculate_profile_score_breakdown(task, member)

    scoring_keys = [
        "skill_match",
        "taxonomy_match",
        "availability",
        "workload_score",
        "reliability",
        "dynamic_status_score",
        "mood_score",
        "priority_score",
        "deadline_urgency_score",
        "final_score",
    ]

    for key in scoring_keys:
        assert 0.0 <= breakdown[key] <= 1.0


def test_NFR_EXP_01_policy_information_is_included_in_breakdown():
    """
    NFR-EXP-01:
    The explanation must include the policy information used by the scoring logic.
    """

    task, member = _build_task_and_member()

    breakdown = calculate_profile_score_breakdown(task, member)

    assert "policy_name" in breakdown["policy"]
    assert "policy_type" in breakdown["policy"]
    assert "minimum_score_threshold" in breakdown["policy"]
    assert "max_workload_allowed" in breakdown["policy"]

    assert "skill_match" in breakdown["weights"]
    assert "workload_score" in breakdown["weights"]
    assert "deadline_urgency_score" in breakdown["weights"]


def test_NFR_EXP_01_human_readable_explanation_is_generated():
    """
    NFR-EXP-01:
    The system must generate a human-readable explanation of the allocation score.
    """

    task, member = _build_task_and_member()

    breakdown = calculate_profile_score_breakdown(task, member)
    explanation = generate_profile_score_explanation(task, member, breakdown)

    assert isinstance(explanation, str)
    assert member.name in explanation
    assert task.title in explanation
    assert "final score" in explanation
    assert "Positive factors" in explanation
    assert "Risk factors" in explanation