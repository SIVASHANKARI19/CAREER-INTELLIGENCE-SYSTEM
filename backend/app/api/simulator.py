from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.simulator import SimulatorSession
from app.schemas.simulator import SimulatorRequest, SimulatorSessionOut
from app.api.deps import get_current_user
from app.services.simulator_service import simulate_career_impact

router = APIRouter(prefix="/api/career-simulator", tags=["Career Simulator"])


@router.post("", response_model=SimulatorSessionOut)
def simulate_career_impact_endpoint(
    body: SimulatorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = body.student_id or (profile.id if profile else None)
    if not student_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    changes_dict = [c.model_dump() for c in body.applied_changes]

    try:
        result = simulate_career_impact(student_id, changes_dict, db)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    record = SimulatorSession(
        student_id=student_id,
        baseline_probability=result["baseline_probability"],
        applied_changes=result["applied_changes"],
        simulated_probability=result["simulated_probability"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "student_id": record.student_id,
        "baseline_probability": record.baseline_probability,
        "applied_changes": record.applied_changes,
        "simulated_probability": record.simulated_probability,
        "delta": result["delta"],
        "created_at": record.created_at,
    }


@router.get("/{student_id}/history", response_model=list[SimulatorSessionOut])
def get_simulation_history(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = (
        db.query(SimulatorSession)
        .filter(SimulatorSession.student_id == student_id)
        .order_by(SimulatorSession.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "baseline_probability": r.baseline_probability,
            "applied_changes": r.applied_changes,
            "simulated_probability": r.simulated_probability,
            "delta": round(r.simulated_probability - r.baseline_probability, 4),
            "created_at": r.created_at,
        }
        for r in records
    ]