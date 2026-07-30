from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.github import GithubAnalyzeRequest, GithubAnalysisOut
from app.api.deps import get_current_user
from app.services.github_service import analyze_github_mock

router = APIRouter(prefix="/api/github", tags=["GitHub"])

@router.post("/analyze", response_model=GithubAnalysisOut)
def analyze_github(
    body: GithubAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = profile.id if profile else 1
    
    mock_data = analyze_github_mock(body.github_url, student_id)
    mock_data["id"] = 1
    return mock_data

@router.get("/{student_id}", response_model=GithubAnalysisOut)
def get_github_analysis(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.id == student_id).first()
    github_url = profile.github_url if profile else ""
    
    mock_data = analyze_github_mock(github_url, student_id)
    mock_data["id"] = 1
    return mock_data
