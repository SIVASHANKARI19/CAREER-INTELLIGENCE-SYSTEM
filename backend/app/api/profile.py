from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.profile import StudentProfileUpdate, StudentProfileOut, ProfileCompletionResponse
from app.api.deps import get_current_user
from app.services.storage_service import save_uploaded_pdf

router = APIRouter(prefix="/api/profile", tags=["Profile"])

def _calculate_completion(profile: StudentProfile) -> int:
    score = 0
    total_checks = 10
    if profile.full_name: score += 1
    if profile.phone: score += 1
    if profile.department: score += 1
    if profile.cgpa is not None: score += 1
    if profile.year_of_study: score += 1
    if profile.career_goal: score += 1
    if profile.programming_languages and len(profile.programming_languages) > 0: score += 1
    if profile.projects and len(profile.projects) > 0: score += 1
    if profile.resume_file_path: score += 1
    if profile.linkedin_pdf_path or profile.github_url: score += 1
    return int((score / total_checks) * 100)

@router.get("", response_model=StudentProfileOut)
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id, full_name=current_user.email.split("@")[0].capitalize())
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.put("", response_model=StudentProfileOut)
def update_profile(
    profile_in: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(profile, field, val)

    profile.profile_completion_pct = _calculate_completion(profile)
    db.commit()
    db.refresh(profile)
    return profile

@router.post("/resume-upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    saved_path = await save_uploaded_pdf(file, student_id=profile.id, file_prefix="resume")
    profile.resume_file_path = saved_path
    profile.profile_completion_pct = _calculate_completion(profile)
    db.commit()

    return {"message": "Resume uploaded successfully", "resume_file_path": saved_path}

@router.post("/linkedin-upload")
async def upload_linkedin(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    saved_path = await save_uploaded_pdf(file, student_id=profile.id, file_prefix="linkedin")
    profile.linkedin_pdf_path = saved_path
    profile.profile_completion_pct = _calculate_completion(profile)
    db.commit()

    return {"message": "LinkedIn profile PDF uploaded successfully", "linkedin_pdf_path": saved_path}

@router.get("/completion", response_model=ProfileCompletionResponse)
def get_profile_completion(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    if not profile:
        return ProfileCompletionResponse(student_id=0, completion_percentage=0, missing_fields=["all"])

    pct = _calculate_completion(profile)
    missing = []
    if not profile.full_name: missing.append("Full Name")
    if not profile.phone: missing.append("Phone Number")
    if not profile.department: missing.append("Department")
    if profile.cgpa is None: missing.append("CGPA")
    if not profile.career_goal: missing.append("Career Goal")
    if not profile.resume_file_path: missing.append("Resume PDF")
    if not profile.github_url: missing.append("GitHub Profile URL")

    return ProfileCompletionResponse(
        student_id=profile.id,
        completion_percentage=pct,
        missing_fields=missing
    )
