import datetime
from typing import Dict, Any

def get_readiness_scores_mock(student_id: int) -> Dict[str, Any]:
    tech = round(85.0 + (student_id % 3) * 2.5, 1)
    comm = round(78.0 + (student_id % 4) * 3.0, 1)
    resume = round(82.0 + (student_id % 5) * 2.0, 1)
    proj = round(88.0 + (student_id % 2) * 4.0, 1)
    gh = round(80.0 + (student_id % 4) * 3.5, 1)
    interview = round(74.0 + (student_id % 5) * 4.0, 1)
    
    overall = round((tech * 0.25 + comm * 0.15 + resume * 0.15 + proj * 0.20 + gh * 0.15 + interview * 0.10), 1)

    return {
        "student_id": student_id,
        "technical_readiness": tech,
        "communication_readiness": comm,
        "resume_readiness": resume,
        "project_readiness": proj,
        "github_readiness": gh,
        "interview_readiness": interview,
        "overall_readiness": overall,
        "computed_at": datetime.datetime.utcnow().isoformat()
    }
