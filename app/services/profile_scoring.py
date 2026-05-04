from typing import Dict, Any, List
from datetime import datetime

from app import models
from app.services.taxonomy import (
    calculate_task_category_match,
    explain_taxonomy_match,
)


def _safe_float(value, default: float = 0.0) -> float:
    """
    Safely convert a value to float and keep it between 0.0 and 1.0.
    """
    if value is None:
        return default

    try:
        value = float(value)
    except (TypeError, ValueError):
        return default

    return max(0.0, min(value, 1.0))


def _get_skill_name(skill_relation) -> str:
    """
    Safely extract skill name from a relationship object.

    This function is defensive because different SQLAlchemy models may name
    the skill attribute as skill_name or name.
    """
    skill = getattr(skill_relation, "skill", None)

    if skill is None:
        return f"skill_id_{getattr(skill_relation, 'skill_id', 'unknown')}"

    skill_name = getattr(skill, "skill_name", None)

    if skill_name is None:
        skill_name = getattr(skill, "name", None)

    if skill_name is None:
        return f"skill_id_{getattr(skill_relation, 'skill_id', 'unknown')}"

    return skill_name


def calculate_skill_match_score(task: models.Task, team_member: models.TeamMember) -> float:
    required_skills = task.required_skills
    member_skills = team_member.skills

    if not required_skills:
        return 0.0

    member_skill_map = {
        member_skill.skill_id: _safe_float(member_skill.level)
        for member_skill in member_skills
    }

    total_score = 0.0

    for required_skill in required_skills:
        required_level = _safe_float(required_skill.required_level)

        if required_level <= 0:
            skill_score = 1.0
        else:
            member_level = member_skill_map.get(required_skill.skill_id, 0.0)

            if member_level >= required_level:
                skill_score = 1.0
            else:
                skill_score = member_level / required_level

        total_score += skill_score

    return round(total_score / len(required_skills), 4)


def calculate_availability_score(team_member: models.TeamMember) -> float:
    return _safe_float(team_member.availability)


def calculate_workload_score(team_member: models.TeamMember) -> float:
    workload = _safe_float(team_member.workload)
    return round(max(0.0, 1.0 - workload), 4)


def calculate_reliability_score(team_member: models.TeamMember) -> float:
    return _safe_float(team_member.reliability)


def calculate_dynamic_status_score(team_member: models.TeamMember) -> float:
    status_scores = {
        "normal": 1.0,
        "busy": 0.5,
        "tired": 0.4,
        "unavailable": 0.0,
    }

    dynamic_status = getattr(team_member, "dynamic_status", None)

    if dynamic_status is None:
        return 0.5

    return status_scores.get(dynamic_status.lower(), 0.5)


def calculate_mood_score(team_member: models.TeamMember) -> float:
    mood_scores = {
        "positive": 1.0,
        "neutral": 0.7,
        "stressed": 0.4,
    }

    mood_state = getattr(team_member, "mood_state", None)

    if mood_state is None:
        return 0.6

    return mood_scores.get(mood_state.lower(), 0.6)

def calculate_taxonomy_match_score(
    task: models.Task,
    team_member: models.TeamMember
) -> float:
    """
    Calculate role-task compatibility based on predefined taxonomy/ontology.

    This checks whether the member's role is compatible with the categories
    of skills required by the task.
    """
    required_skill_names = [
        _get_skill_name(required_skill)
        for required_skill in task.required_skills
    ]

    member_role = getattr(team_member, "role", "")

    return calculate_task_category_match(
        task_required_skills=required_skill_names,
        member_role=member_role,
    )

def calculate_priority_score(task: models.Task) -> float:
    """
    Convert task priority into a numeric score.

    Higher priority tasks receive higher scores.
    This supports constraint-aware allocation.
    """
    priority_scores = {
        "low": 0.4,
        "medium": 0.6,
        "high": 0.8,
        "critical": 1.0,
    }

    priority = getattr(task, "priority", None)

    if priority is None:
        return 0.6

    return priority_scores.get(priority.lower(), 0.6)


def calculate_deadline_urgency_score(task: models.Task) -> float:
    """
    Calculate urgency based on the task deadline.

    The closer the deadline, the higher the urgency score.
    If the deadline is already passed, the score is also high because
    the task needs attention.
    """
    deadline = getattr(task, "deadline", None)

    if deadline is None:
        return 0.5

    now = datetime.utcnow()
    time_left = deadline - now
    days_left = time_left.total_seconds() / 86400

    if days_left < 0:
        return 1.0
    if days_left <= 1:
        return 1.0
    if days_left <= 3:
        return 0.8
    if days_left <= 7:
        return 0.6

    return 0.4

def calculate_profile_score_breakdown(
    task: models.Task,
    team_member: models.TeamMember
) -> Dict[str, Any]:
    """
    Calculate detailed scoring components for a team member.

    This function makes the allocation algorithm explainable.
    Instead of returning only one final number, it returns all criteria
    used in the decision-making process.
    """
    skill_match = calculate_skill_match_score(task, team_member)
    taxonomy_match = calculate_taxonomy_match_score(task, team_member)
    availability = calculate_availability_score(team_member)
    workload_score = calculate_workload_score(team_member)
    reliability = calculate_reliability_score(team_member)
    dynamic_status_score = calculate_dynamic_status_score(team_member)
    mood_score = calculate_mood_score(team_member)
    priority_score = calculate_priority_score(task)
    deadline_urgency_score = calculate_deadline_urgency_score(task)

    weighted_score = (
        skill_match * 0.30 +
        taxonomy_match * 0.10 +
        availability * 0.15 +
        workload_score * 0.15 +
        reliability * 0.10 +
        dynamic_status_score * 0.07 +
        mood_score * 0.03 +
        priority_score * 0.05 +
        deadline_urgency_score * 0.05
    )

    return {
        "skill_match": round(skill_match, 4),
        "taxonomy_match": round(taxonomy_match, 4),
        "availability": round(availability, 4),
        "workload_score": round(workload_score, 4),
        "reliability": round(reliability, 4),
        "dynamic_status_score": round(dynamic_status_score, 4),
        "mood_score": round(mood_score, 4),
        "priority_score": round(priority_score, 4),
        "deadline_urgency_score": round(deadline_urgency_score, 4),
        "weights": {
            "skill_match": 0.30,
            "taxonomy_match": 0.10,
            "availability": 0.15,
            "workload_score": 0.15,
            "reliability": 0.10,
            "dynamic_status_score": 0.07,
            "mood_score": 0.03,
            "priority_score": 0.05,
            "deadline_urgency_score": 0.05,
        },
        "final_score": round(weighted_score, 4),
    }


def generate_profile_score_explanation(
    task: models.Task,
    team_member: models.TeamMember,
    breakdown: Dict[str, Any]
) -> str:
    """
    Generate a human-readable explanation of the score.

    The explanation separates positive factors from risk factors.
    This makes the decision-support logic clearer and more suitable
    for the Software Engineering report.
    """
    positive_factors: List[str] = []
    risk_factors: List[str] = []

    if breakdown["skill_match"] >= 0.8:
        positive_factors.append("strong match with the required skills")
    elif breakdown["skill_match"] >= 0.5:
        positive_factors.append("partial match with the required skills")
    else:
        risk_factors.append("weak match with the required skills")

    if breakdown["taxonomy_match"] >= 0.8:
        positive_factors.append("strong role-task taxonomy compatibility")
    elif breakdown["taxonomy_match"] >= 0.5:
        positive_factors.append("partial role-task taxonomy compatibility")
    else:
        risk_factors.append("weak role-task taxonomy compatibility")

    if breakdown["priority_score"] >= 0.8:
        positive_factors.append("high task priority")
    elif breakdown["priority_score"] <= 0.4:
        risk_factors.append("low task priority")

    if breakdown["deadline_urgency_score"] >= 0.8:
        positive_factors.append("urgent deadline")
    elif breakdown["deadline_urgency_score"] <= 0.4:
        risk_factors.append("non-urgent deadline")

    if breakdown["availability"] >= 0.8:
        positive_factors.append("high availability")
    elif breakdown["availability"] >= 0.5:
        positive_factors.append("medium availability")
    else:
        risk_factors.append("low availability")

    if breakdown["workload_score"] >= 0.8:
        positive_factors.append("low current workload")
    elif breakdown["workload_score"] >= 0.5:
        positive_factors.append("acceptable workload")
    else:
        risk_factors.append("high current workload")

    if breakdown["reliability"] >= 0.8:
        positive_factors.append("high reliability")
    elif breakdown["reliability"] >= 0.5:
        positive_factors.append("acceptable reliability")
    else:
        risk_factors.append("low reliability")

    if breakdown["dynamic_status_score"] >= 0.8:
        positive_factors.append("good dynamic status")
    elif breakdown["dynamic_status_score"] <= 0.5:
        risk_factors.append("dynamic status may reduce suitability")

    if breakdown["mood_score"] >= 0.8:
        positive_factors.append("positive mood state")
    elif breakdown["mood_score"] <= 0.5:
        risk_factors.append("current mood state may reduce suitability")

    member_name = getattr(team_member, "name", "This team member")
    task_title = getattr(task, "title", "this task")

    positive_text = ", ".join(positive_factors) if positive_factors else "no strong positive factors"
    risk_text = ", ".join(risk_factors) if risk_factors else "no major risk factors"

    return (
        f"{member_name} received a final score of {breakdown['final_score']} "
        f"for task '{task_title}'. "
        f"Positive factors: {positive_text}. "
        f"Risk factors: {risk_text}."
    )


def calculate_final_profile_score(task: models.Task, team_member: models.TeamMember) -> float:
    """
    Backward-compatible function.

    Other services can still call calculate_final_profile_score(),
    but internally the score now comes from the detailed breakdown.
    """
    breakdown = calculate_profile_score_breakdown(task, team_member)
    return breakdown["final_score"]


def get_required_skill_details(task: models.Task) -> List[Dict[str, Any]]:
    """
    Return required skills with levels for better explanation in API responses.
    """
    result = []

    for required_skill in task.required_skills:
        result.append({
            "skill_id": required_skill.skill_id,
            "skill_name": _get_skill_name(required_skill),
            "required_level": required_skill.required_level,
        })

    return result


def get_member_skill_details(team_member: models.TeamMember) -> List[Dict[str, Any]]:
    """
    Return member skills with levels for better explanation in API responses.
    """
    result = []

    for member_skill in team_member.skills:
        result.append({
            "skill_id": member_skill.skill_id,
            "skill_name": _get_skill_name(member_skill),
            "level": member_skill.level,
        })

    return result