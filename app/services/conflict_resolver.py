from sqlalchemy.orm import Session

from app import models
from app.services.allocation_engine import find_best_team_member_for_task


def detect_assignment_conflicts(project_id: int, db: Session):
    open_tasks = db.query(models.Task).filter(
        models.Task.project_id == project_id,
        models.Task.status == "open"
    ).all()

    if not open_tasks:
        return {
            "project_id": project_id,
            "message": "No open tasks found.",
            "conflicts": [],
            "task_recommendations": []
        }

    task_recommendations = []
    member_to_tasks = {}

    for task in open_tasks:
        best_candidate, candidate_scores = find_best_team_member_for_task(task.id, db)

        if not best_candidate:
            task_recommendations.append({
                "task_id": task.id,
                "task_title": task.title,
                "best_candidate": None,
                "message": "No suitable candidate found",
                "candidate_scores": candidate_scores
            })
            continue

        member_id = best_candidate["team_member_id"]

        if member_id not in member_to_tasks:
            member_to_tasks[member_id] = []

        member_to_tasks[member_id].append({
            "task_id": task.id,
            "task_title": task.title,
            "priority": task.priority,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "estimated_effort": task.estimated_effort,
            "score": best_candidate["score"]
        })

        task_recommendations.append({
            "task_id": task.id,
            "task_title": task.title,
            "best_candidate": best_candidate,
            "candidate_scores": candidate_scores
        })

    conflicts = []

    for member_id, tasks in member_to_tasks.items():
        if len(tasks) > 1:
            member = db.query(models.TeamMember).filter(
                models.TeamMember.id == member_id
            ).first()

            total_effort = sum(task["estimated_effort"] for task in tasks)

            conflicts.append({
                "team_member_id": member_id,
                "team_member_name": member.name if member else "Unknown",
                "current_workload": member.workload if member else None,
                "number_of_competing_tasks": len(tasks),
                "total_new_effort": round(total_effort, 4),
                "risk_level": "high" if total_effort >= 0.6 else "medium",
                "competing_tasks": tasks,
                "reason": "Multiple open tasks have the same best candidate"
            })

    return {
        "project_id": project_id,
        "message": "Conflict analysis completed.",
        "conflicts": conflicts,
        "task_recommendations": task_recommendations
    }


def suggest_conflict_resolution(project_id: int, db: Session):
    analysis = detect_assignment_conflicts(project_id, db)

    suggestions = []

    for conflict in analysis["conflicts"]:
        competing_tasks = conflict["competing_tasks"]

        sorted_tasks = sorted(
            competing_tasks,
            key=lambda task: (
                priority_to_number(task["priority"]),
                task["deadline"] or "9999-12-31"
            ),
            reverse=True
        )

        primary_task = sorted_tasks[0]
        secondary_tasks = sorted_tasks[1:]

        suggestions.append({
            "team_member_id": conflict["team_member_id"],
            "team_member_name": conflict["team_member_name"],
            "recommended_primary_task": primary_task,
            "tasks_for_manual_review_or_alternative_assignment": secondary_tasks,
            "reason": "Keep the highest priority or most urgent task with the best candidate and review the remaining tasks."
        })

    return {
        "project_id": project_id,
        "message": "Conflict resolution suggestions generated.",
        "suggestions": suggestions
    }


def priority_to_number(priority: str) -> int:
    priority_map = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }

    return priority_map.get(priority, 2)