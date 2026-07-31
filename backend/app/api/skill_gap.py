from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.resume import ResumeAnalysis
from app.models.fusion import FusionResult
from app.models.company_requirement import CompanyRequirement
from app.models.skill_gap import SkillGapResult
from app.schemas.skill_gap import SkillGapRequest, SkillGapResultOut
from app.api.deps import get_current_user
from app.services.skill_gap_service import analyze_skill_gap

router = APIRouter(prefix="/api/skill-gap", tags=["SkillGap"])


def _gather_student_skills(student_id: int, db: Session) -> list:
    fusion = db.query(FusionResult).filter(FusionResult.student_id == student_id).first()
    if fusion:
        # Union of everything the student has any evidence of (resume-verified + hidden)
        return sorted(set(fusion.verified_skills or []) | set(fusion.hidden_skills or []))
    resume = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == student_id).first()
    return resume.extracted_skills if resume else []


def _run_and_persist(student_id: int, target_role: str, db: Session) -> SkillGapResult:
    student_skills = _gather_student_skills(student_id, db)

    matching_companies = (
        db.query(CompanyRequirement)
        .filter(CompanyRequirement.role.ilike(f"%{target_role}%"))
        .all()
    )
    company_requirements = [
        {"company_name": c.company_name, "role": c.role, "required_skills": c.required_skills or []}
        for c in matching_companies
    ] if matching_companies else None

    result = analyze_skill_gap(student_skills, target_role, company_requirements, student_id)

    record = db.query(SkillGapResult).filter(
        SkillGapResult.student_id == student_id,
        SkillGapResult.target_role == target_role,
    ).first()
    if record is None:
        record = SkillGapResult(student_id=student_id, target_role=target_role)
        db.add(record)

    record.matched_skills = result["matched_skills"]
    record.missing_skills = result["missing_skills"]
    record.priority_map = result["priority_map"]
    record.estimated_learning_time = result["estimated_learning_time"]

    db.commit()
    db.refresh(record)
    return record


@router.post("", response_model=SkillGapResultOut)
def analyze_skill_gap_endpoint(
    body: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else None)
    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return _run_and_persist(student_id, body.target_role, db)


@router.get("/{student_id}", response_model=SkillGapResultOut)
def get_skill_gap(
    student_id: int,
    target_role: str = "SDE",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(SkillGapResult).filter(
        SkillGapResult.student_id == student_id,
        SkillGapResult.target_role == target_role,
    ).first()
    if not record:
        # Compute on first read for this role rather than 404ing — same
        # "compute and cache" pattern used in Module 9's readiness endpoint.
        return _run_and_persist(student_id, target_role, db)
    return record