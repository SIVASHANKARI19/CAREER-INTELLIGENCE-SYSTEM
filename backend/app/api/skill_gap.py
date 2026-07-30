from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.skill_gap import SkillGapRequest, SkillGapResultOut
from app.api.deps import get_current_user
from app.services.skill_gap_service import analyze_skill_gap_mock

router = APIRouter(prefix="/api/skill-gap", tags=["SkillGap"])

@router.post("", response_model=SkillGapResultOut)
def analyze_skill_gap(
    body: SkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else 1)

    mock_data = analyze_skill_gap_mock(student_id, body.target_role)
    mock_data["id"] = 1
    return mock_data

@router.get("/{student_id}", response_model=SkillGapResultOut)
def get_skill_gap(
    student_id: int,
    target_role: str = "SDE",
    current_user: User = Depends(get_current_user)
):
    mock_data = analyze_skill_gap_mock(student_id, target_role)
    mock_data["id"] = 1
    return mock_data
