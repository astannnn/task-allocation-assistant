from sqlalchemy.orm import Session

from app import models
from app.services.profile_scoring import (
    calculate_profile_score_breakdown,
    generate_profile_score_explanation,
    get_required_skill_details,
    get_member_skill_details,
)

from app.services.notification_service import (
    create_task_reassignment_notification,
    create_manual_review_notification,
)

from app.services.taxonomy import explain_taxonomy_match


MINIMUM_ACCEPTABLE_REASSIGNMENT_SCORE = 0.5


def find_current_active_assignment(task_id: int, db: Session):
    """
    Find the current active assignment for a task.
    """
    return db.query(models.Assignment).filter(
        models.Assignment.task_id == task_id,
        models.Assignment.status == "active"
    ).first()


def decrease_previous_member_workload(
    task: models.Task,
    current_assignment: models.Assignment,
    db: Session
):
    """
    Decrease workload of the previous assignee when a delayed task is reassigned.

    This makes the reassignment workflow more realistic because the previous
    team member is no longer responsible for the task.
    """
    if not current_assignment:
        return None

    previous_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == current_assignment.team_member_id
    ).first()

    if not previous_member:
        return None

    previous_member.workload = max(
        0.0,
        previous_member.workload - task.estimated_effort
    )

    return previous_member


def increase_new_member_workload(
    task: models.Task,
    new_member_id: int,
    db: Session
):
    """
    Increase workload of the new assignee after reassignment.
    """
    new_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == new_member_id
    ).first()

    if not new_member:
        return None

    new_member.workload = min(
        1.0,
        new_member.workload + task.estimated_effort
    )

    return new_member


def build_reassignment_candidate_response(
    task: models.Task,
    member: models.TeamMember,
    required_skill_details
):
    """
    Build a detailed candidate response for reassignment.

    This is similar to automatic allocation preview, but it is used
    when the system searches for a replacement for a delayed task.
    """
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

    return {
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
    }


def find_replacement_for_delayed_task(task_id: int, db: Session):
    """
    Find the best replacement for a delayed task.

    The current assignee is excluded from the candidate list.
    Unavailable members are also excluded.
    """
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
    required_skill_details = get_required_skill_details(task)

    for member in team_members:
        if member.id == current_member_id:
            continue

        if member.dynamic_status == "unavailable":
            continue

        candidate_response = build_reassignment_candidate_response(
            task=task,
            member=member,
            required_skill_details=required_skill_details,
        )

        candidate_scores.append(candidate_response)

    candidate_scores.sort(key=lambda candidate: candidate["score"], reverse=True)

    if not candidate_scores:
        return None, []

    best_candidate = candidate_scores[0]

    if best_candidate["score"] < MINIMUM_ACCEPTABLE_REASSIGNMENT_SCORE:
        return None, candidate_scores

    return best_candidate, candidate_scores


def reassign_delayed_task(task_id: int, db: Session):
    """
    Reassign a delayed task to a new suitable team member.

    Workflow:
    1. Check if task exists.
    2. Check if task is delayed.
    3. Find current active assignment.
    4. Exclude current assignee.
    5. Evaluate alternative candidates.
    6. If no replacement is found, move task to manual_review.
    7. If replacement is found, close old assignment and create new assignment.
    8. Update workload of previous and new assignee.
    """
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

    if not current_assignment:
        task.status = "manual_review"

        create_manual_review_notification(
            db=db,
            task=task,
            reason="No active assignment found for this delayed task.",
        )

        return {
            "success": False,
            "message": "No active assignment found for this delayed task. Task moved to manual review.",
            "new_assignment": None,
            "candidate_scores": []
        }

    best_candidate, candidate_scores = find_replacement_for_delayed_task(task_id, db)

    if not best_candidate:
        task.status = "manual_review"

        create_manual_review_notification(
            db=db,
            task=task,
            reason="No suitable replacement found during delayed task reassignment.",
        )

        return {
            "success": False,
            "message": "No suitable replacement found. Task moved to manual review.",
            "new_assignment": None,
            "candidate_scores": candidate_scores
        }

    previous_member = None

    if current_assignment:
        current_assignment.status = "reassigned"
        previous_member = decrease_previous_member_workload(
            task=task,
            current_assignment=current_assignment,
            db=db,
        )

    new_assignment = models.Assignment(
        task_id=task.id,
        team_member_id=best_candidate["team_member_id"],
        status="active",
        score_at_assignment=best_candidate["score"],
    )

    new_member = increase_new_member_workload(
        task=task,
        new_member_id=best_candidate["team_member_id"],
        db=db,
    )

    task.status = "assigned"

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    if new_member:
        create_task_reassignment_notification(
            db=db,
            task=task,
            previous_member=previous_member,
            new_member=new_member,
        )

    return {
        "success": True,
        "message": "Delayed task reassigned successfully",
        "previous_assignment": {
            "id": current_assignment.id if current_assignment else None,
            "team_member_id": current_assignment.team_member_id if current_assignment else None,
            "status": current_assignment.status if current_assignment else None,
        },
        "previous_member_workload_after_reassignment": {
            "team_member_id": previous_member.id if previous_member else None,
            "team_member_name": previous_member.name if previous_member else None,
            "workload": previous_member.workload if previous_member else None,
        },
        "new_assignment": {
            "id": new_assignment.id,
            "task_id": new_assignment.task_id,
            "team_member_id": new_assignment.team_member_id,
            "score_at_assignment": new_assignment.score_at_assignment,
            "status": new_assignment.status,
        },
        "new_member_workload_after_reassignment": {
            "team_member_id": new_member.id if new_member else None,
            "team_member_name": new_member.name if new_member else None,
            "workload": new_member.workload if new_member else None,
        },
        "selected_candidate_explanation": best_candidate["explanation"],
        "candidate_scores": candidate_scores
    }