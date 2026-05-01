from sqlalchemy.orm import Session

from app import models


def analyze_project_workload(project_id: int, db: Session):
    team_members = db.query(models.TeamMember).filter(
        models.TeamMember.project_id == project_id
    ).all()

    if not team_members:
        return {
            "project_id": project_id,
            "average_workload": 0,
            "members": [],
            "overloaded_members": [],
            "underloaded_members": [],
            "balance_status": "no_team_members"
        }

    members_data = []
    overloaded_members = []
    underloaded_members = []

    total_workload = 0

    for member in team_members:
        workload = member.workload
        total_workload += workload

        if workload >= 0.8:
            workload_status = "overloaded"
            overloaded_members.append({
                "team_member_id": member.id,
                "name": member.name,
                "workload": workload
            })
        elif workload <= 0.3:
            workload_status = "underloaded"
            underloaded_members.append({
                "team_member_id": member.id,
                "name": member.name,
                "workload": workload
            })
        else:
            workload_status = "balanced"

        members_data.append({
            "team_member_id": member.id,
            "name": member.name,
            "role": member.role,
            "workload": workload,
            "availability": member.availability,
            "reliability": member.reliability,
            "dynamic_status": member.dynamic_status,
            "mood_state": member.mood_state,
            "workload_status": workload_status
        })

    average_workload = round(total_workload / len(team_members), 4)

    if len(overloaded_members) > 0 and len(underloaded_members) > 0:
        balance_status = "unbalanced"
    elif len(overloaded_members) > 0:
        balance_status = "high_workload_risk"
    else:
        balance_status = "balanced"

    return {
        "project_id": project_id,
        "average_workload": average_workload,
        "members": members_data,
        "overloaded_members": overloaded_members,
        "underloaded_members": underloaded_members,
        "balance_status": balance_status
    }


def suggest_workload_redistribution(project_id: int, db: Session):
    analysis = analyze_project_workload(project_id, db)

    overloaded_members = analysis["overloaded_members"]
    underloaded_members = analysis["underloaded_members"]

    suggestions = []

    if not overloaded_members:
        return {
            "project_id": project_id,
            "message": "No overloaded team members detected.",
            "suggestions": []
        }

    if not underloaded_members:
        return {
            "project_id": project_id,
            "message": "Overloaded members exist, but no clearly underloaded members are available.",
            "suggestions": []
        }

    for overloaded in overloaded_members:
        for underloaded in underloaded_members:
            suggestions.append({
                "from_team_member_id": overloaded["team_member_id"],
                "from_team_member_name": overloaded["name"],
                "to_team_member_id": underloaded["team_member_id"],
                "to_team_member_name": underloaded["name"],
                "reason": "Possible redistribution from overloaded member to underloaded member"
            })

    return {
        "project_id": project_id,
        "message": "Redistribution suggestions generated.",
        "suggestions": suggestions
    }