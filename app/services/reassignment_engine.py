from sqlalchemy.orm import Session

from app import models
from app.services.profile_scoring import calculate_final_profile_score


def find_current_active_assignment(task_id: int, db: Session):
    return db.query(models.Assignment).filter(
        models.Assignment.task_id == task_id,
        models.Assignment.status == "active"
    ).first()


def find_replacement_for_delayed_task(task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        return None, []

    current_assignment = find_current_active_assignment(task_id, db)

    current_member_id = None
    if current_assignment:
        current_member_id = current_assignment.team_member_id

    team_members = db.query(models.TeamMember).filter(
        models.TeamMember.project_id == task.project_id
    ).all()

    candidate_scores = []

    for member in team_members:
        if member.id == current_member_id:
            continue

        if member.dynamic_status == "unavailable":
            continue

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


def reassign_delayed_task(task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        return {
            "success": False,
            "message": "Task not found",
            "new_assignment": None,
            "candidate_scores": []
        }

    if task.status != "delayed":
        return {
            "success": False,
            "message": "Task is not marked as delayed",
            "new_assignment": None,
            "candidate_scores": []
        }

    current_assignment = find_current_active_assignment(task_id, db)

    best_candidate, candidate_scores = find_replacement_for_delayed_task(task_id, db)

    if not best_candidate:
        return {
            "success": False,
            "message": "No suitable replacement found. Task requires manual review.",
            "new_assignment": None,
            "candidate_scores": candidate_scores
        }

    if current_assignment:
        current_assignment.status = "reassigned"

    new_assignment = models.Assignment(
        task_id=task.id,
        team_member_id=best_candidate["team_member_id"],
        status="active",
        score_at_assignment=best_candidate["score"],
    )

    new_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == best_candidate["team_member_id"]
    ).first()

    if new_member:
        new_member.workload = min(
            1.0,
            new_member.workload + task.estimated_effort
        )

    task.status = "assigned"

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return {
        "success": True,
        "message": "Delayed task reassigned successfully",
        "new_assignment": {
            "id": new_assignment.id,
            "task_id": new_assignment.task_id,
            "team_member_id": new_assignment.team_member_id,
            "score_at_assignment": new_assignment.score_at_assignment,
            "status": new_assignment.status,
        },
        "candidate_scores": candidate_scores
    }