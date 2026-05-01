from app import models


def calculate_skill_match_score(task: models.Task, team_member: models.TeamMember) -> float:
    required_skills = task.required_skills
    member_skills = team_member.skills

    if not required_skills:
        return 0.0

    member_skill_map = {
        member_skill.skill_id: member_skill.level
        for member_skill in member_skills
    }

    total_score = 0.0

    for required_skill in required_skills:
        member_level = member_skill_map.get(required_skill.skill_id, 0.0)

        if member_level >= required_skill.required_level:
            skill_score = 1.0
        else:
            skill_score = member_level / required_skill.required_level

        total_score += skill_score

    return total_score / len(required_skills)


def calculate_availability_score(team_member: models.TeamMember) -> float:
    return max(0.0, min(team_member.availability, 1.0))


def calculate_workload_score(team_member: models.TeamMember) -> float:
    return max(0.0, 1.0 - team_member.workload)


def calculate_reliability_score(team_member: models.TeamMember) -> float:
    return max(0.0, min(team_member.reliability, 1.0))


def calculate_dynamic_status_score(team_member: models.TeamMember) -> float:
    status_scores = {
        "normal": 1.0,
        "busy": 0.5,
        "tired": 0.4,
        "unavailable": 0.0,
    }

    return status_scores.get(team_member.dynamic_status, 0.5)


def calculate_mood_score(team_member: models.TeamMember) -> float:
    mood_scores = {
        "positive": 1.0,
        "neutral": 0.7,
        "stressed": 0.4,
    }

    return mood_scores.get(team_member.mood_state, 0.6)


def calculate_final_profile_score(task: models.Task, team_member: models.TeamMember) -> float:
    skill_match = calculate_skill_match_score(task, team_member)
    availability = calculate_availability_score(team_member)
    workload = calculate_workload_score(team_member)
    reliability = calculate_reliability_score(team_member)
    dynamic_status = calculate_dynamic_status_score(team_member)
    mood = calculate_mood_score(team_member)

    final_score = (
        skill_match * 0.40 +
        availability * 0.15 +
        workload * 0.15 +
        reliability * 0.15 +
        dynamic_status * 0.10 +
        mood * 0.05
    )

    return round(final_score, 4)