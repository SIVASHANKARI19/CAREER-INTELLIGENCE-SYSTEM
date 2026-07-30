from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.schemas.simulator import SimulatorRequest, SimulatorSessionOut
from app.api.deps import get_current_user
from app.services.simulator_service import simulate_career_impact_mock

router = APIRouter(prefix="/api/career-simulator", tags=["Career Simulator"])

@router.post("", response_model=SimulatorSessionOut)
def simulate_career_impact(
    body: SimulatorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else 1)

    changes_dict = [c.model_dump() for c in body.applied_changes]
    mock_data = simulate_career_impact_mock(student_id, changes_dict)
    return mock_data
