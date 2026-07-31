from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.github_profile import GithubAnalysis
from app.schemas.github import GithubAnalyzeRequest, GithubAnalysisOut
from app.api.deps import get_current_user
from app.services.github_service import analyze_github

router = APIRouter(prefix="/api/github", tags=["GitHub"])


def _run_and_persist(github_url: str, student_id: int, db: Session) -> GithubAnalysis:
    try:
        result = analyze_github(github_url, student_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"GitHub analysis failed: {str(e)}")

    record = db.query(GithubAnalysis).filter(GithubAnalysis.student_id == student_id).first()
    if record is None:
        record = GithubAnalysis(student_id=student_id)
        db.add(record)

    record.repositories = result["repositories"]
    record.languages_summary = result["languages_summary"]
    record.total_commits = result["total_commits"]
    record.github_score = result["github_score"]
    record.project_quality_score = result["project_quality_score"]
    record.skill_confidence = result["skill_confidence"]

    db.commit()
    db.refresh(record)
    return record


@router.post("/analyze", response_model=GithubAnalysisOut)
def analyze_github_endpoint(
    body: GithubAnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = profile.id if profile else None
    if not profile or not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    github_url = body.github_url or profile.github_url
    if not github_url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No GitHub URL provided.")

    # Keep the profile's stored github_url in sync if the caller passed a new one
    if body.github_url and body.github_url != profile.github_url:
        profile.github_url = body.github_url
        db.commit()

    return _run_and_persist(github_url, student_id, db)


@router.get("/{student_id}", response_model=GithubAnalysisOut)
def get_github_analysis(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(GithubAnalysis).filter(GithubAnalysis.student_id == student_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No GitHub analysis found for this student. Run POST /api/github/analyze first."
        )
    return record