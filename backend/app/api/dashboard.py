from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.api.deps import get_current_user
from app.services.readiness_service import get_readiness_scores_mock
from app.services.resume_service import analyze_resume_mock
from app.services.github_service import analyze_github_mock

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/summary")
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = profile.id if profile else 1

    readiness = get_readiness_scores_mock(student_id)
    resume = analyze_resume_mock(student_id)
    github = analyze_github_mock(profile.github_url if profile else "", student_id)

    return {
        "student_id": student_id,
        "full_name": profile.full_name if profile else current_user.email,
        "career_goal": profile.career_goal if profile else "Software Development Engineer",
        "overall_readiness": readiness["overall_readiness"],
        "ats_score": resume["ats_score"],
        "github_score": github["github_score"],
        "resume_score": resume["ats_score"],
        "skill_gap_count": 5,
        "profile_completion": profile.profile_completion_pct if profile else 50,
        "recent_activity": [
            {"id": 1, "type": "resume_analyzed", "description": "Resume ATS score computed: 84.5%", "time": "2 hours ago"},
            {"id": 2, "type": "github_synced", "description": "GitHub profile synced with 3 repos", "time": "1 day ago"},
            {"id": 3, "type": "roadmap_generated", "description": "Weekly learning roadmap updated", "time": "3 days ago"}
        ]
    }
