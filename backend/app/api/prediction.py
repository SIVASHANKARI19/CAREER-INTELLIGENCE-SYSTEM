from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.prediction import PredictionRequest, PlacementPredictionOut
from app.api.deps import get_current_user
from app.services.prediction_service import predict_placement_mock

router = APIRouter(prefix="/api/predict-placement", tags=["Prediction"])

@router.post("", response_model=PlacementPredictionOut)
def predict_placement(
    body: PredictionRequest = PredictionRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else 1)

    mock_data = predict_placement_mock(student_id)
    mock_data["id"] = 1
    return mock_data

@router.get("/{student_id}", response_model=PlacementPredictionOut)
def get_placement_prediction(
    student_id: int,
    current_user: User = Depends(get_current_user)
):
    mock_data = predict_placement_mock(student_id)
    mock_data["id"] = 1
    return mock_data
