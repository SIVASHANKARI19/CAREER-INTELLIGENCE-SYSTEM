from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.linkedin import LinkedinAnalyzeRequest, LinkedinAnalysisOut
from app.api.deps import get_current_user
from app.services.linkedin_service import analyze_linkedin_mock

router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn"])

@router.post("/analyze", response_model=LinkedinAnalysisOut)
def analyze_linkedin(
    body: LinkedinAnalyzeRequest = LinkedinAnalyzeRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else 1)

    mock_data = analyze_linkedin_mock(student_id)
    mock_data["id"] = 1
    return mock_data

@router.get("/{student_id}", response_model=LinkedinAnalysisOut)
def get_linkedin_analysis(
    student_id: int,
    current_user: User = Depends(get_current_user)
):
    mock_data = analyze_linkedin_mock(student_id)
    mock_data["id"] = 1
    return mock_data
