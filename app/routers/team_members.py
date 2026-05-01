from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/team-members",
    tags=["Team Members"]
)


@router.post("/", response_model=schemas.TeamMemberResponse)
def create_team_member(
    team_member: schemas.TeamMemberCreate,
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(
        models.Project.id == team_member.project_id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_team_member = models.TeamMember(
        name=team_member.name,
        role=team_member.role,
        project_id=team_member.project_id,
        user_id=team_member.user_id,
        availability=team_member.availability,
        workload=team_member.workload,
        reliability=team_member.reliability,
        dynamic_status=team_member.dynamic_status,
        mood_state=team_member.mood_state,
    )

    db.add(db_team_member)
    db.commit()
    db.refresh(db_team_member)

    return db_team_member


@router.get("/", response_model=List[schemas.TeamMemberResponse])
def get_team_members(db: Session = Depends(get_db)):
    return db.query(models.TeamMember).all()


@router.get("/{team_member_id}", response_model=schemas.TeamMemberResponse)
def get_team_member(team_member_id: int, db: Session = Depends(get_db)):
    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == team_member_id
    ).first()

    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return team_member


@router.get("/project/{project_id}", response_model=List[schemas.TeamMemberResponse])
def get_team_members_by_project(project_id: int, db: Session = Depends(get_db)):
    return db.query(models.TeamMember).filter(
        models.TeamMember.project_id == project_id
    ).all()


@router.delete("/{team_member_id}")
def delete_team_member(team_member_id: int, db: Session = Depends(get_db)):
    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == team_member_id
    ).first()

    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")

    db.delete(team_member)
    db.commit()

    return {"message": "Team member deleted successfully"}

@router.post("/skills/", response_model=schemas.TeamMemberSkillResponse)
def add_skill_to_team_member(
    member_skill: schemas.TeamMemberSkillCreate,
    db: Session = Depends(get_db)
):
    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == member_skill.team_member_id
    ).first()

    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")

    skill = db.query(models.Skill).filter(
        models.Skill.id == member_skill.skill_id
    ).first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing_skill = db.query(models.TeamMemberSkill).filter(
        models.TeamMemberSkill.team_member_id == member_skill.team_member_id,
        models.TeamMemberSkill.skill_id == member_skill.skill_id
    ).first()

    if existing_skill:
        existing_skill.level = member_skill.level
        db.commit()
        db.refresh(existing_skill)
        return existing_skill

    db_member_skill = models.TeamMemberSkill(
        team_member_id=member_skill.team_member_id,
        skill_id=member_skill.skill_id,
        level=member_skill.level,
    )

    db.add(db_member_skill)
    db.commit()
    db.refresh(db_member_skill)

    return db_member_skill


@router.get("/{team_member_id}/skills", response_model=List[schemas.TeamMemberSkillResponse])
def get_team_member_skills(
    team_member_id: int,
    db: Session = Depends(get_db)
):
    team_member = db.query(models.TeamMember).filter(
        models.TeamMember.id == team_member_id
    ).first()

    if not team_member:
        raise HTTPException(status_code=404, detail="Team member not found")

    return db.query(models.TeamMemberSkill).filter(
        models.TeamMemberSkill.team_member_id == team_member_id
    ).all()