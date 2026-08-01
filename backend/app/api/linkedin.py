from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.linkedin_profile import LinkedinAnalysis
from app.schemas.linkedin import LinkedinAnalyzeRequest, LinkedinAnalysisOut
from app.api.deps import get_current_user
from app.services.linkedin_service import analyze_linkedin

router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn"])


@router.post("/analyze", response_model=LinkedinAnalysisOut)
def analyze_linkedin_endpoint(
    body: LinkedinAnalyzeRequest = LinkedinAnalyzeRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else None)
    if not profile or not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")
    if not profile.linkedin_pdf_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No LinkedIn PDF uploaded yet. Upload via /api/profile/linkedin-upload first."
        )

    try:
        result = analyze_linkedin(profile.linkedin_pdf_path, student_id)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LinkedIn PDF missing on server. Please re-upload.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"LinkedIn analysis failed: {str(e)}")

    record = db.query(LinkedinAnalysis).filter(LinkedinAnalysis.student_id == student_id).first()
    if record is None:
        record = LinkedinAnalysis(student_id=student_id)
        db.add(record)

    record.headline = result["headline"]
    record.summary = result["summary"]
    record.extracted_skills = result["extracted_skills"]
    record.extracted_experience = result["extracted_experience"]
    record.extracted_education = result["extracted_education"]
    record.extracted_certificates = result["extracted_certificates"]
    record.extracted_posts = result["extracted_posts"]

    db.commit()
    db.refresh(record)
    return record


@router.get("/{student_id}", response_model=LinkedinAnalysisOut)
def get_linkedin_analysis(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(LinkedinAnalysis).filter(LinkedinAnalysis.student_id == student_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No LinkedIn analysis found for this student. Run POST /api/linkedin/analyze first."
        )
    return record