from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.resume import ResumeAnalyzeRequest, ResumeAnalysisOut
from app.api.deps import get_current_user
from app.services.resume_service import analyze_resume_mock

router = APIRouter(prefix="/api/resume", tags=["Resume"])

@router.post("/analyze", response_model=ResumeAnalysisOut)
def analyze_resume(
    body: ResumeAnalyzeRequest = ResumeAnalyzeRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else 1)
    
    mock_data = analyze_resume_mock(student_id)
    # mock_data contains id placeholder or generated fields
    mock_data["id"] = 1
    return mock_data

@router.get("/{student_id}", response_model=ResumeAnalysisOut)
def get_resume_analysis(
    student_id: int,
    current_user: User = Depends(get_current_user)
):
    mock_data = analyze_resume_mock(student_id)
    mock_data["id"] = 1
    return mock_data
