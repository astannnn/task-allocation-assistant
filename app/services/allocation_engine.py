from sqlalchemy.orm import Session

from app import models
from app.services.profile_scoring import (
    calculate_profile_score_breakdown,
    generate_profile_score_explanation,
    get_required_skill_details,
    get_member_skill_details,
)

from app.services.notification_service import (
    create_task_assignment_notification,
    create_manual_review_notification,
)

from app.services.taxonomy import explain_taxonomy_match


MINIMUM_ACCEPTABLE_SCORE = 0.5

def close_existing_active_assignments(task_id: int, db: Session):
    """
    Close previous active assignments for a task before creating a new one.

    Business rule:
    one task should have only one active assignment at a time.
    """
    active_assignments = db.query(models.Assignment).filter(
        models.Assignment.task_id == task_id,
        models.Assignment.status == "active",
    ).all()

    for assignment in active_assignments:
        assignment.status = "reassigned"

    return active_assignments


def find_best_team_member_for_task(task_id: int, db: Session):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        return None, []

    team_members = db.query(models.TeamMember).filter(
        models.TeamMember.project_id == task.project_id
    ).all()

    candidate_scores = []

    required_skill_details = get_required_skill_details(task)

    for member in team_members:
        score_breakdown = calculate_profile_score_breakdown(task, member)
        explanation = generate_profile_score_explanation(task, member, score_breakdown)

        task_required_skill_names = [
            skill_detail["skill_name"]
            for skill_detail in required_skill_details
        ]

        member_skill_details = get_member_skill_details(member)
        member_skill_names = [
            skill_detail["skill_name"]
            for skill_detail in member_skill_details
        ]

        taxonomy_explanation = explain_taxonomy_match(
            task_required_skills=task_required_skill_names,
            member_role=member.role,
            member_skills=member_skill_names,
        )

        candidate_scores.append({
            "team_member_id": member.id,
            "team_member_name": member.name,
            "role": member.role,
            "score": score_breakdown["final_score"],
            "score_breakdown": score_breakdown,
            "explanation": explanation,
            "availability": member.availability,
            "workload": member.workload,
            "reliability": member.reliability,
            "dynamic_status": member.dynamic_status,
            "mood_state": member.mood_state,
            "required_skills": required_skill_details,
            "member_skills": member_skill_details,
            "taxonomy_explanation": taxonomy_explanation,
        })

    candidate_scores.sort(key=lambda candidate: candidate["score"], reverse=True)

    if not candidate_scores:
        return None, []

    best_candidate = candidate_scores[0]

    if best_candidate["score"] < MINIMUM_ACCEPTABLE_SCORE:
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
        task.status = "manual_review"

        create_manual_review_notification(
            db=db,
            task=task,
            reason="No suitable team member found during automatic allocation.",
        )

        return {
            "success": False,
            "message": "No suitable team member found. Task moved to manual review.",
            "assignment": None,
            "candidate_scores": candidate_scores
        }
    
    closed_assignments = close_existing_active_assignments(
        task_id=task.id,
        db=db,
    )

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

    if assigned_member:
        create_task_assignment_notification(
            db=db,
            task=task,
            team_member=assigned_member,
        )

    return {
        "success": True,
        "message": "Task automatically allocated successfully",
        "closed_previous_active_assignments": len(closed_assignments),
        "assignment": {
            "id": assignment.id,
            "task_id": assignment.task_id,
            "team_member_id": assignment.team_member_id,
            "score_at_assignment": assignment.score_at_assignment,
            "status": assignment.status,
        },
        "selected_candidate_explanation": best_candidate["explanation"],
        "candidate_scores": candidate_scores
    }