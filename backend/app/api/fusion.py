from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.resume import ResumeAnalysis
from app.models.github_profile import GithubAnalysis
from app.models.linkedin_profile import LinkedinAnalysis
from app.models.fusion import FusionResult
from app.schemas.fusion import FusionRequest, FusionResultOut
from app.api.deps import get_current_user
from app.services.fusion_service import run_fusion

router = APIRouter(prefix="/api/profile/fusion", tags=["Fusion"])


def _run_and_persist(student_id: int, db: Session) -> FusionResult:
    resume = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == student_id).first()
    github = db.query(GithubAnalysis).filter(GithubAnalysis.student_id == student_id).first()
    linkedin = db.query(LinkedinAnalysis).filter(LinkedinAnalysis.student_id == student_id).first()

    if not resume and not github and not linkedin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No source data available yet. Run resume, GitHub, and/or LinkedIn analysis before fusion."
        )

    resume_skills = resume.extracted_skills if resume else []
    resume_project_tech = [
        tech for project in (resume.extracted_projects if resume else [])
        for tech in project.get("tech_stack", [])
    ]
    github_languages = list((github.languages_summary if github else {}).keys())
    github_skill_confidence = github.skill_confidence if github else {}
    linkedin_skills = linkedin.extracted_skills if linkedin else []

    result = run_fusion(
        resume_skills=resume_skills,
        resume_project_tech=resume_project_tech,
        github_languages=github_languages,
        github_skill_confidence=github_skill_confidence,
        linkedin_skills=linkedin_skills,
        student_id=student_id,
    )

    record = db.query(FusionResult).filter(FusionResult.student_id == student_id).first()
    if record is None:
        record = FusionResult(student_id=student_id)
        db.add(record)

    record.verified_skills = result["verified_skills"]
    record.hidden_skills = result["hidden_skills"]
    record.unsupported_claims = result["unsupported_claims"]
    record.resume_credibility_score = result["resume_credibility_score"]
    record.suggestions = result["suggestions"]

    db.commit()
    db.refresh(record)
    return record


@router.post("", response_model=FusionResultOut)
def run_fusion_endpoint(
    body: FusionRequest = FusionRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else None)
    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    return _run_and_persist(student_id, db)


@router.get("/{student_id}", response_model=FusionResultOut)
def get_fusion_result(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(FusionResult).filter(FusionResult.student_id == student_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No fusion result found for this student. Run POST /api/profile/fusion first."
        )
    return record