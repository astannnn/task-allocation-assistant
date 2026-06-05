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
from app.services.scheduling_policy_service import get_active_policy
from app.services.allocation_decision_service import record_allocation_decision


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

    active_policy = get_active_policy(db)

    team_members = db.query(models.TeamMember).filter(
        models.TeamMember.project_id == task.project_id
    ).all()

    candidate_scores = []
    required_skill_details = get_required_skill_details(task)

    for member in team_members:
        score_breakdown = calculate_profile_score_breakdown(task, member, db)
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

        workload_value = member.workload or 0.0
        max_workload_allowed = active_policy.max_workload_allowed or 0.90
        violates_workload_constraint = workload_value > max_workload_allowed

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
            "violates_workload_constraint": violates_workload_constraint,
            "policy_used": {
                "policy_id": active_policy.id,
                "policy_name": active_policy.name,
                "policy_type": active_policy.policy_type,
                "minimum_score_threshold": active_policy.minimum_score_threshold,
                "max_workload_allowed": active_policy.max_workload_allowed,
            }
        })

    candidate_scores.sort(key=lambda candidate: candidate["score"], reverse=True)

    if not candidate_scores:
        return None, []

    minimum_score_threshold = active_policy.minimum_score_threshold or 0.50

    for candidate in candidate_scores:
        score_is_acceptable = candidate["score"] >= minimum_score_threshold
        workload_is_acceptable = not candidate["violates_workload_constraint"]

        if score_is_acceptable and workload_is_acceptable:
            return candidate, candidate_scores

    return None, candidate_scores


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

        top_candidate = candidate_scores[0] if candidate_scores else None

        record_allocation_decision(
            db=db,
            task_id=task.id,
            decision_type="manual_review",
            selected_team_member_id=None,
            final_score=top_candidate["score"] if top_candidate else None,
            score_breakdown={
                "candidate_scores": candidate_scores,
                "top_candidate": top_candidate,
            },
            reason="No suitable team member found during automatic allocation.",
            policy_name=(
                top_candidate["policy_used"]["policy_name"]
                if top_candidate and "policy_used" in top_candidate
                else None
            ),
        )

        create_manual_review_notification(
            db=db,
            task=task,
            reason="No suitable team member found during automatic allocation.",
        )

        db.commit()

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

    record_allocation_decision(
        db=db,
        task_id=task.id,
        decision_type="automatic_assignment",
        selected_team_member_id=best_candidate["team_member_id"],
        final_score=best_candidate["score"],
        score_breakdown=best_candidate.get("score_breakdown"),
        reason=best_candidate.get("explanation"),
        policy_name=best_candidate.get("policy_used", {}).get("policy_name"),
    )

    assigned_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == best_candidate["team_member_id"]
    ).first()

    task.status = "assigned"

    if assigned_member:
        assigned_member.workload = min(
            1.0,
            (assigned_member.workload or 0.0) + (task.estimated_effort or 0.0)
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
        db.commit()

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