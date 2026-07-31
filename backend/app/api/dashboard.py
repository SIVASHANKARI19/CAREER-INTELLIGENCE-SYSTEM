from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.activity_log import ActivityLog
from app.models.resume import ResumeAnalysis
from app.models.github_profile import GithubAnalysis
from app.api.deps import get_current_user
from app.api.readiness import compute_and_persist_readiness
from app.services.resume_service import analyze_resume_mock
from app.services.github_service import analyze_github_mock
from app.services.skill_gap_service import analyze_skill_gap_mock

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


def _humanize_time_ago(dt) -> str:
    import datetime
    delta = datetime.datetime.utcnow() - dt
    if delta.days > 0:
        return f"{delta.days} day{'s' if delta.days != 1 else ''} ago"
    hours = delta.seconds // 3600
    if hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    minutes = max(delta.seconds // 60, 1)
    return f"{minutes} minute{'s' if minutes != 1 else ''} ago"


@router.get("/summary")
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == current_user.id).first()
    student_id = profile.id if profile else 1
    career_goal = profile.career_goal if profile else "Software Development Engineer"

    readiness_record = compute_and_persist_readiness(student_id, db)
    overall_readiness = readiness_record.overall_readiness

    resume_record = db.query(ResumeAnalysis).filter(ResumeAnalysis.student_id == student_id).first()
    resume = {"ats_score": resume_record.ats_score} if resume_record else analyze_resume_mock(student_id)

    github_record = db.query(GithubAnalysis).filter(GithubAnalysis.student_id == student_id).first()
    if github_record:
        github = {"github_score": github_record.github_score, "repositories": github_record.repositories}
    else:
        github = analyze_github_mock(profile.github_url if profile else "", student_id)

    skill_gap = analyze_skill_gap_mock(student_id, career_goal)

    # Pull real activity if any exists; otherwise fall back to a deterministic
    # per-student mock (consistent with how every other service on this
    # dashboard behaves) instead of a single hardcoded array for everyone.
    logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.student_id == student_id)
        .order_by(ActivityLog.created_at.desc())
        .limit(5)
        .all()
    )
    if logs:
        recent_activity = [
            {
                "id": log.id,
                "type": log.activity_type,
                "description": log.description,
                "time": _humanize_time_ago(log.created_at),
            }
            for log in logs
        ]
    else:
        recent_activity = [
            {"id": 1, "type": "resume_analyzed", "description": f"Resume ATS score computed: {resume['ats_score']}%", "time": "2 hours ago"},
            {"id": 2, "type": "github_synced", "description": f"GitHub profile synced with {len(github.get('repositories', []))} repos", "time": "1 day ago"},
            {"id": 3, "type": "roadmap_generated", "description": "Weekly learning roadmap updated", "time": "3 days ago"},
        ]

    return {
        "student_id": student_id,
        "full_name": profile.full_name if profile else current_user.email,
        "career_goal": career_goal,
        "overall_readiness": overall_readiness,
        "ats_score": resume["ats_score"],
        "github_score": github["github_score"],
        "resume_score": resume["ats_score"],
        "skill_gap_count": len(skill_gap["missing_skills"]),
        "profile_completion": profile.profile_completion_pct if profile else 50,
        "recent_activity": recent_activity
    }