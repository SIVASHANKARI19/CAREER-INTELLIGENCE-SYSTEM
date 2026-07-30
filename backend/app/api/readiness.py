from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.readiness import ReadinessScoreOut
from app.api.deps import get_current_user
from app.services.readiness_service import get_readiness_scores_mock

router = APIRouter(prefix="/api/readiness", tags=["Readiness"])

@router.get("/{student_id}", response_model=ReadinessScoreOut)
def get_readiness(
    student_id: int,
    current_user: User = Depends(get_current_user)
):
    mock_data = get_readiness_scores_mock(student_id)
    mock_data["id"] = 1
    return mock_data
