from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.fusion import FusionResult
from app.models.skill_gap import SkillGapResult
from app.models.roadmap import LearningRoadmap
from app.schemas.roadmap import RoadmapRequest, LearningRoadmapOut
from app.api.deps import get_current_user
from app.services.roadmap_service import generate_roadmap

router = APIRouter(prefix="/api/roadmap", tags=["Roadmap"])


@router.post("", response_model=LearningRoadmapOut)
def generate_roadmap_endpoint(
    body: RoadmapRequest = RoadmapRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else None)
    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    target_role = (profile.career_goal if profile else None) or "Software Development Engineer"
    fusion = db.query(FusionResult).filter(FusionResult.student_id == student_id).first()
    skill_gap = (
        db.query(SkillGapResult)
        .filter(SkillGapResult.student_id == student_id, SkillGapResult.target_role == target_role)
        .first()
    )

    result = generate_roadmap(
        target_role=target_role,
        missing_skills=skill_gap.missing_skills if skill_gap else [],
        priority_map=skill_gap.priority_map if skill_gap else {},
        verified_skills=fusion.verified_skills if fusion else [],
        cgpa=float(profile.cgpa) if profile and profile.cgpa else None,
        student_id=student_id,
    )

    record = db.query(LearningRoadmap).filter(LearningRoadmap.student_id == student_id).first()
    if record is None:
        record = LearningRoadmap(student_id=student_id)
        db.add(record)

    record.weekly_plan = result["weekly_plan"]
    record.monthly_plan = result["monthly_plan"]
    record.recommended_projects = result["recommended_projects"]
    record.recommended_courses = result["recommended_courses"]
    record.interview_questions = result["interview_questions"]
    record.resources = result["resources"]

    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}", response_model=LearningRoadmapOut)
def get_roadmap(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(LearningRoadmap).filter(LearningRoadmap.student_id == student_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roadmap found for this student. Run POST /api/roadmap first."
        )
    return record