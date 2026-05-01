from sqlalchemy.orm import Session

from app import models
from app.services.profile_scoring import calculate_final_profile_score


def find_best_team_member_for_task(task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        return None, []

    team_members = db.query(models.TeamMember).filter(
        models.TeamMember.project_id == task.project_id
    ).all()

    candidate_scores = []

    for member in team_members:
        score = calculate_final_profile_score(task, member)

        candidate_scores.append({
            "team_member_id": member.id,
            "team_member_name": member.name,
            "score": score,
            "availability": member.availability,
            "workload": member.workload,
            "reliability": member.reliability,
            "dynamic_status": member.dynamic_status,
            "mood_state": member.mood_state,
        })

    candidate_scores.sort(key=lambda candidate: candidate["score"], reverse=True)

    if not candidate_scores:
        return None, []

    best_candidate = candidate_scores[0]

    if best_candidate["score"] < 0.5:
        return None, candidate_scores

    return best_candidate, candidate_scores


def automatically_allocate_task(task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        return {
            "success": False,
            "message": "Task not found",
            "assignment": None,
            "candidate_scores": []
        }

    best_candidate, candidate_scores = find_best_team_member_for_task(task_id, db)

    if not best_candidate:
        task.status = "open"
        db.commit()

        return {
            "success": False,
            "message": "No suitable team member found. Task requires manual review.",
            "assignment": None,
            "candidate_scores": candidate_scores
        }

    assignment = models.Assignment(
        task_id=task.id,
        team_member_id=best_candidate["team_member_id"],
        status="active",
        score_at_assignment=best_candidate["score"],
    )

    assigned_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == best_candidate["team_member_id"]
    ).first()

    task.status = "assigned"

    if assigned_member:
        assigned_member.workload = min(
            1.0,
            assigned_member.workload + task.estimated_effort
        )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "success": True,
        "message": "Task automatically allocated successfully",
        "assignment": {
            "id": assignment.id,
            "task_id": assignment.task_id,
            "team_member_id": assignment.team_member_id,
            "score_at_assignment": assignment.score_at_assignment,
            "status": assignment.status,
        },
        "candidate_scores": candidate_scores
    }