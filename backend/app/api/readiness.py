from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.resume import ResumeAnalysis
from app.models.github_profile import GithubAnalysis
from app.models.linkedin_profile import LinkedinAnalysis
from app.models.fusion import FusionResult
from app.models.readiness import ReadinessScore
from app.schemas.readiness import ReadinessScoreOut
from app.api.deps import get_current_user
from app.services.readiness_service import compute_readiness

router = APIRouter(prefix="/api/readiness", tags=["Readiness"])


def compute_and_persist_readiness(student_id: int, db: Session) -> ReadinessScore:
    profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    resume = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == student_id).first()
    github = db.query(GithubAnalysis).filter(GithubAnalysis.student_id == student_id).first()
    linkedin = db.query(LinkedinAnalysis).filter(LinkedinAnalysis.student_id == student_id).first()
    fusion = db.query(FusionResult).filter(FusionResult.student_id == student_id).first()

    result = compute_readiness(
        resume_ats_score=resume.ats_score if resume else None,
        github_score=github.github_score if github else None,
        project_quality_score=github.project_quality_score if github else None,
        resume_credibility_score=fusion.resume_credibility_score if fusion else None,
        verified_skills_count=len(fusion.verified_skills) if fusion else 0,
        programming_languages_count=len(profile.programming_languages) if profile and profile.programming_languages else 0,
        projects_count=len(profile.projects) if profile and profile.projects else 0,
        achievements_count=len(profile.achievements) if profile and profile.achievements else 0,
        linkedin_summary_length=len(linkedin.summary) if linkedin and linkedin.summary else 0,
        student_id=student_id,
    )

    record = db.query(ReadinessScore).filter(ReadinessScore.student_id == student_id).first()
    if record is None:
        record = ReadinessScore(student_id=student_id)
        db.add(record)

    for field in ["technical_readiness", "communication_readiness", "resume_readiness",
                  "project_readiness", "github_readiness", "interview_readiness", "overall_readiness"]:
        setattr(record, field, result[field])

    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}", response_model=ReadinessScoreOut)
def get_readiness(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return compute_and_persist_readiness(student_id, db)