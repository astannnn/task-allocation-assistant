from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas


router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)


@router.post("/", response_model=schemas.SkillResponse)
def create_skill(skill: schemas.SkillCreate, db: Session = Depends(get_db)):
    db_skill = models.Skill(
        name=skill.name,
        type=skill.type,
        category=skill.category,
    )

    db.add(db_skill)
    db.commit()
    db.refresh(db_skill)

    return db_skill


@router.get("/", response_model=List[schemas.SkillResponse])
def get_skills(db: Session = Depends(get_db)):
    return db.query(models.Skill).all()


@router.get("/{skill_id}", response_model=schemas.SkillResponse)
def get_skill(skill_id: int, db: Session = Depends(get_db)):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return skill


def remove_skill_and_related_links(skill_id: int, db: Session):
    skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()

    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.query(models.TeamMemberSkill).filter(
        models.TeamMemberSkill.skill_id == skill_id
    ).delete(synchronize_session=False)

    db.query(models.TaskRequiredSkill).filter(
        models.TaskRequiredSkill.skill_id == skill_id
    ).delete(synchronize_session=False)

    db.delete(skill)
    db.commit()

    return skill


@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):
    remove_skill_and_related_links(skill_id, db)

    return {"message": "Skill deleted successfully"}


@router.post("/{skill_id}/delete")
def delete_skill_from_ui(skill_id: int, db: Session = Depends(get_db)):
    remove_skill_and_related_links(skill_id, db)

    return RedirectResponse(url="/skills", status_code=303)