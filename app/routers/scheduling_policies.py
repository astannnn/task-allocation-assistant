from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services.scheduling_policy_service import (
    get_active_policy,
    activate_policy,
    normalize_policy_weights,
)


router = APIRouter(
    prefix="/scheduling-policies",
    tags=["Scheduling Policies"]
)


@router.get("/", response_model=List[schemas.SchedulingPolicyResponse])
def get_scheduling_policies(db: Session = Depends(get_db)):
    """
    Get all scheduling policies.
    """
    return db.query(models.SchedulingPolicy).all()


@router.get("/active", response_model=schemas.SchedulingPolicyResponse)
def get_current_active_policy(db: Session = Depends(get_db)):
    """
    Get the active scheduling policy.

    If no policy exists, the default balanced policy is created automatically.
    """
    return get_active_policy(db)


@router.post("/", response_model=schemas.SchedulingPolicyResponse)
def create_scheduling_policy(
    policy_data: schemas.SchedulingPolicyCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new scheduling policy.
    """
    policy = models.SchedulingPolicy(**policy_data.dict())

    policy = normalize_policy_weights(policy)

    if policy.is_active == 1:
        existing_policies = db.query(models.SchedulingPolicy).all()
        for existing_policy in existing_policies:
            existing_policy.is_active = 0

    db.add(policy)
    db.commit()
    db.refresh(policy)

    return policy


@router.get("/{policy_id}", response_model=schemas.SchedulingPolicyResponse)
def get_scheduling_policy(policy_id: int, db: Session = Depends(get_db)):
    """
    Get one scheduling policy by ID.
    """
    policy = db.query(models.SchedulingPolicy).filter(
        models.SchedulingPolicy.id == policy_id
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail="Scheduling policy not found")

    return policy


@router.put("/{policy_id}", response_model=schemas.SchedulingPolicyResponse)
def update_scheduling_policy(
    policy_id: int,
    policy_data: schemas.SchedulingPolicyUpdate,
    db: Session = Depends(get_db)
):
    """
    Update scheduling policy parameters.

    The manager/admin can change weights, thresholds and policy type.
    """
    policy = db.query(models.SchedulingPolicy).filter(
        models.SchedulingPolicy.id == policy_id
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail="Scheduling policy not found")

    update_data = policy_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(policy, field, value)

    policy = normalize_policy_weights(policy)

    if policy.is_active == 1:
        existing_policies = db.query(models.SchedulingPolicy).filter(
            models.SchedulingPolicy.id != policy.id
        ).all()

        for existing_policy in existing_policies:
            existing_policy.is_active = 0

    db.commit()
    db.refresh(policy)

    return policy


@router.post("/{policy_id}/activate", response_model=schemas.SchedulingPolicyResponse)
def activate_scheduling_policy(policy_id: int, db: Session = Depends(get_db)):
    """
    Activate selected scheduling policy and deactivate all others.
    """
    policy = activate_policy(policy_id, db)

    if not policy:
        raise HTTPException(status_code=404, detail="Scheduling policy not found")

    return policy


@router.delete("/{policy_id}")
def delete_scheduling_policy(policy_id: int, db: Session = Depends(get_db)):
    """
    Delete scheduling policy.

    The active policy cannot be deleted to avoid leaving the scheduler
    without configuration.
    """
    policy = db.query(models.SchedulingPolicy).filter(
        models.SchedulingPolicy.id == policy_id
    ).first()

    if not policy:
        raise HTTPException(status_code=404, detail="Scheduling policy not found")

    if policy.is_active == 1:
        raise HTTPException(
            status_code=400,
            detail="Active scheduling policy cannot be deleted"
        )

    db.delete(policy)
    db.commit()

    return {
        "success": True,
        "message": "Scheduling policy deleted successfully"
    }


@router.post("/seed-defaults")
def seed_default_scheduling_policies(db: Session = Depends(get_db)):
    """
    Create predefined scheduling policies for demo and admin configuration.

    This creates:
    - Balanced Policy
    - Skill-Oriented Policy
    - Workload-Balanced Policy
    - Deadline-Oriented Policy
    """
    existing_count = db.query(models.SchedulingPolicy).count()

    if existing_count > 0:
        return {
            "success": False,
            "message": "Scheduling policies already exist. Defaults were not created."
        }

    policies = [
        models.SchedulingPolicy(
            name="Balanced Policy",
            policy_type="balanced",
            is_active=1,
            skill_weight=0.30,
            taxonomy_weight=0.10,
            availability_weight=0.15,
            workload_weight=0.15,
            reliability_weight=0.10,
            dynamic_status_weight=0.07,
            mood_weight=0.03,
            priority_weight=0.05,
            deadline_weight=0.05,
            minimum_score_threshold=0.50,
            max_workload_allowed=0.90,
        ),
        models.SchedulingPolicy(
            name="Skill-Oriented Policy",
            policy_type="skill_oriented",
            is_active=0,
            skill_weight=0.45,
            taxonomy_weight=0.15,
            availability_weight=0.10,
            workload_weight=0.10,
            reliability_weight=0.08,
            dynamic_status_weight=0.04,
            mood_weight=0.03,
            priority_weight=0.03,
            deadline_weight=0.02,
            minimum_score_threshold=0.55,
            max_workload_allowed=0.95,
        ),
        models.SchedulingPolicy(
            name="Workload-Balanced Policy",
            policy_type="workload_balanced",
            is_active=0,
            skill_weight=0.25,
            taxonomy_weight=0.10,
            availability_weight=0.15,
            workload_weight=0.25,
            reliability_weight=0.08,
            dynamic_status_weight=0.07,
            mood_weight=0.03,
            priority_weight=0.04,
            deadline_weight=0.03,
            minimum_score_threshold=0.50,
            max_workload_allowed=0.75,
        ),
        models.SchedulingPolicy(
            name="Deadline-Oriented Policy",
            policy_type="deadline_oriented",
            is_active=0,
            skill_weight=0.25,
            taxonomy_weight=0.08,
            availability_weight=0.15,
            workload_weight=0.10,
            reliability_weight=0.08,
            dynamic_status_weight=0.05,
            mood_weight=0.02,
            priority_weight=0.12,
            deadline_weight=0.15,
            minimum_score_threshold=0.50,
            max_workload_allowed=0.90,
        ),
    ]

    for policy in policies:
        db.add(policy)

    db.commit()

    return {
        "success": True,
        "message": "Default scheduling policies created successfully",
        "created_policies": len(policies)
    }