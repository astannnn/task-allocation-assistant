import json
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session

from app import models


def _to_json(data: Any) -> str:
    """
    Safely serialize allocation decision evidence to JSON.
    """
    return json.dumps(data, default=str, ensure_ascii=False)


def record_allocation_decision(
    db: Session,
    task_id: int,
    decision_type: str,
    selected_team_member_id: Optional[int] = None,
    final_score: Optional[float] = None,
    score_breakdown: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    policy_name: Optional[str] = None,
) -> models.AllocationDecision:
    """
    CCL / NFR-EXP evidence:
    Store the decision evidence produced by the allocation engine.

    This makes allocation decisions auditable and explainable.
    """

    decision = models.AllocationDecision(
        task_id=task_id,
        selected_team_member_id=selected_team_member_id,
        decision_type=decision_type,
        final_score=final_score,
        score_breakdown_json=_to_json(score_breakdown or {}),
        reason=reason,
        policy_name=policy_name,
    )

    db.add(decision)

    return decision


def get_decisions_for_task(
    db: Session,
    task_id: int,
) -> List[models.AllocationDecision]:
    """
    Return allocation decision history for a task.
    """

    return db.query(models.AllocationDecision).filter(
        models.AllocationDecision.task_id == task_id
    ).all()