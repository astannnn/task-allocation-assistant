from types import SimpleNamespace

from sqlalchemy.orm import Session

from app import models


DEFAULT_POLICY_VALUES = {
    "id": None,
    "name": "Balanced Policy",
    "policy_type": "balanced",
    "is_active": 1,

    "skill_weight": 0.30,
    "taxonomy_weight": 0.10,
    "availability_weight": 0.15,
    "workload_weight": 0.15,
    "reliability_weight": 0.10,
    "dynamic_status_weight": 0.07,
    "mood_weight": 0.03,
    "priority_weight": 0.05,
    "deadline_weight": 0.05,

    "minimum_score_threshold": 0.50,
    "max_workload_allowed": 0.90,
}


def get_default_policy_object():
    """
    Return default policy as an in-memory object.

    This is useful for tests with FakeDB objects that do not support
    db.add(), db.commit(), or real table operations.
    """
    return SimpleNamespace(**DEFAULT_POLICY_VALUES)


def create_default_policy(db: Session):
    """
    Create the default balanced scheduling policy in the real database.
    """
    policy_data = DEFAULT_POLICY_VALUES.copy()
    policy_data.pop("id", None)

    policy = models.SchedulingPolicy(**policy_data)

    db.add(policy)
    db.commit()
    db.refresh(policy)

    return policy


def get_active_policy(db: Session):
    """
    Return the currently active scheduling policy.

    If no active policy exists:
    - in a real database session, create the default policy;
    - in tests with FakeDB, return an in-memory default policy.
    """
    try:
        policy = db.query(models.SchedulingPolicy).filter(
            models.SchedulingPolicy.is_active == 1
        ).first()

        if policy:
            return policy

        if hasattr(db, "add") and hasattr(db, "commit") and hasattr(db, "refresh"):
            return create_default_policy(db)

        return get_default_policy_object()

    except Exception:
        return get_default_policy_object()


def deactivate_all_policies(db: Session):
    """
    Make all scheduling policies inactive.
    """
    policies = db.query(models.SchedulingPolicy).all()

    for policy in policies:
        policy.is_active = 0

    db.commit()


def activate_policy(policy_id: int, db: Session):
    """
    Activate one policy and deactivate all others.
    """
    policy = db.query(models.SchedulingPolicy).filter(
        models.SchedulingPolicy.id == policy_id
    ).first()

    if not policy:
        return None

    deactivate_all_policies(db)

    policy.is_active = 1
    db.commit()
    db.refresh(policy)

    return policy


def normalize_policy_weights(policy):
    """
    Normalize weights if their sum is greater than 0.
    """
    weight_fields = [
        "skill_weight",
        "taxonomy_weight",
        "availability_weight",
        "workload_weight",
        "reliability_weight",
        "dynamic_status_weight",
        "mood_weight",
        "priority_weight",
        "deadline_weight",
    ]

    total = sum(float(getattr(policy, field) or 0.0) for field in weight_fields)

    if total <= 0:
        return policy

    for field in weight_fields:
        current_value = float(getattr(policy, field) or 0.0)
        setattr(policy, field, round(current_value / total, 4))

    return policy