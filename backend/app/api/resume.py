from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.orm import Session

from app.core.database import get_db

from app.models.user import User

from app.models.student_profile import StudentProfile

from app.models.resume import ResumeAnalysis

from app.schemas.resume import ResumeAnalyzeRequest, ResumeAnalysisOut

from app.api.deps import get_current_user

from app.services.resume_service import analyze_resume



router = APIRouter(prefix="/api/resume", tags=["Resume"])





@router.post("/analyze", response_model=ResumeAnalysisOut)

def analyze_resume_endpoint(

    body: ResumeAnalyzeRequest = ResumeAnalyzeRequest(),

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()

    student_id = body.student_id or (profile.id if profile else None)

    if not profile or not student_id:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    if not profile.resume_file_path:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="No resume uploaded yet. Upload a PDF via /api/profile/resume-upload first."

        )



    try:

        result = analyze_resume(profile.resume_file_path, student_id)

    except FileNotFoundError:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file missing on server. Please re-upload.")

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Resume analysis failed: {str(e)}")



    # Upsert: one resume_analysis row per student, refreshed on each re-analysis

    record = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == student_id).first()

    if record is None:

        record = ResumeAnalysis(student_id=student_id)

        db.add(record)



    record.raw_text = result["raw_text"]

    record.extracted_skills = result["extracted_skills"]

    record.extracted_projects = result["extracted_projects"]

    record.extracted_certifications = result["extracted_certifications"]

    record.extracted_experience = result["extracted_experience"]

    record.extracted_education = result["extracted_education"]

    record.ats_score = result["ats_score"]

    record.suggestions = result["suggestions"]



    db.commit()

    db.refresh(record)

    return record





@router.get("/{student_id}", response_model=ResumeAnalysisOut)

def get_resume_analysis(

    student_id: int,

    current_user: User = Depends(get_current_user),

    db: Session = Depends(get_db)

):

    record = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == student_id).first()

    if not record:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="No resume analysis found for this student. Run POST /api/resume/analyze first."

        )

    return record