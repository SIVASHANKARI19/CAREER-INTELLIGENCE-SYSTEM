from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.placement_prediction import PlacementPrediction
from app.schemas.prediction import PredictionRequest, PlacementPredictionOut
from app.api.deps import get_current_user
from app.services.prediction_service import predict_placement, gather_features_from_db

router = APIRouter(prefix="/api/predict-placement", tags=["Prediction"])


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

    features = gather_features_from_db(student_id, db)
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