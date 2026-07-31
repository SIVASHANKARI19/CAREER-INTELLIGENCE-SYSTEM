from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.resume import ResumeAnalysis
from app.models.github_profile import GithubAnalysis
from app.models.fusion import FusionResult
from app.models.placement_prediction import PlacementPrediction
from app.schemas.prediction import PredictionRequest, PlacementPredictionOut
from app.api.deps import get_current_user
from app.services.prediction_service import build_feature_vector, predict_placement

router = APIRouter(prefix="/api/predict-placement", tags=["Prediction"])


def _gather_features(student_id: int, db: Session) -> dict:
    profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    resume = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == student_id).first()
    github = db.query(GithubAnalysis).filter(GithubAnalysis.student_id == student_id).first()
    fusion = db.query(FusionResult).filter(FusionResult.student_id == student_id).first()

    return build_feature_vector(
        cgpa=float(profile.cgpa) if profile and profile.cgpa else 6.5,
        ats_score=resume.ats_score if resume else 40.0,
        github_score=github.github_score if github else 20.0,
        project_quality_score=github.project_quality_score if github else 20.0,
        resume_credibility_score=fusion.resume_credibility_score if fusion else 40.0,
        verified_skills_count=len(fusion.verified_skills) if fusion else 0,
        hidden_skills_count=len(fusion.hidden_skills) if fusion else 0,
        unsupported_claims_count=len(fusion.unsupported_claims) if fusion else 0,
        projects_count=len(profile.projects) if profile and profile.projects else 0,
        certifications_count=len(profile.certifications) if profile and profile.certifications else 0,
        internships_count=len(profile.internships) if profile and profile.internships else 0,
        programming_languages_count=len(profile.programming_languages) if profile and profile.programming_languages else 0,
        total_commits=github.total_commits if github else 0,
    )


@router.post("", response_model=PlacementPredictionOut)
def predict_placement_endpoint(
    body: PredictionRequest = PredictionRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else None)
    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    features = _gather_features(student_id, db)
    try:
        result = predict_placement(features, student_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    record = db.query(PlacementPrediction).filter(PlacementPrediction.student_id == student_id).first()
    if record is None:
        record = PlacementPrediction(student_id=student_id)
        db.add(record)

    record.placement_probability = result["placement_probability"]
    record.expected_salary_range = result["expected_salary_range"]
    record.confidence = result["confidence"]
    record.readiness_level = result["readiness_level"]
    record.model_version = result["model_version"]
    record.feature_snapshot = result["feature_snapshot"]

    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}", response_model=PlacementPredictionOut)
def get_placement_prediction(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(PlacementPrediction).filter(PlacementPrediction.student_id == student_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No prediction found for this student. Run POST /api/predict-placement first."
        )
    return record