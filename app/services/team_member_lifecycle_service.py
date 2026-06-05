from typing import Optional, Dict, Any, List

from sqlalchemy.orm import Session

from app import models


def delete_team_member_safely(
    team_member_id: int,
    db: Session,
) -> Optional[Dict[str, Any]]:
    """
    NFR-REL-01:
    Delete a team member without leaving inconsistent assignment/task data.

    Business rules:
    - A deleted team member must not remain connected to active assignments.
    - Active/in-progress/delayed tasks assigned to this member are moved to manual_review.
    - Assignment records are closed by setting status to reassigned.
    - The assignment team_member_id is cleared to avoid orphan references.
    - Team member skill links are removed before deleting the member.
    """

    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == team_member_id
    ).first()

    if not team_member:
        return None

    assignments = db.query(models.Assignment).filter(
        models.Assignment.team_member_id == team_member_id
    ).all()

    released_task_ids: List[int] = []
    closed_assignment_ids: List[int] = []

    for assignment in assignments:
        task = db.query(models.Task).filter(
            models.Task.id == assignment.task_id
        ).first()

        if task and task.status in ["assigned", "in_progress", "delayed"]:
            task.status = "manual_review"
            released_task_ids.append(task.id)

        assignment.status = "reassigned"
        assignment.team_member_id = None
        closed_assignment_ids.append(assignment.id)

    skill_links = db.query(models.TeamMemberSkill).filter(
        models.TeamMemberSkill.team_member_id == team_member_id
    ).all()

    removed_skill_links = len(skill_links)

    for skill_link in skill_links:
        db.delete(skill_link)

    db.delete(team_member)
    db.commit()

    return {
        "message": "Team member deleted safely",
        "deleted_team_member_id": team_member_id,
        "released_task_ids": released_task_ids,
        "closed_assignment_ids": closed_assignment_ids,
        "removed_skill_links": removed_skill_links,
    }