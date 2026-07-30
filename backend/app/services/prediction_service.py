import datetime
from typing import Dict, Any

def predict_placement_mock(student_id: int) -> Dict[str, Any]:
    prob = round(0.82 + (student_id % 4) * 0.03, 2)
    if prob > 0.95:
        prob = 0.92

    readiness = "industry_ready" if prob >= 0.80 else ("intermediate" if prob >= 0.60 else "beginner")

    return {
        "student_id": student_id,
        "placement_probability": prob,
        "expected_salary_range": "$85,000 - $115,000 / yr" if prob >= 0.80 else "$65,000 - $85,000 / yr",
        "confidence": 0.89,
        "readiness_level": readiness,
        "model_version": "v2.1-XGBoost-Explainable",
        "feature_snapshot": {
            "cgpa": 8.6,
            "ats_score": 85.0,
            "github_score": 82.5,
            "internships_count": 1,
            "projects_count": 3,
            "verified_skills_count": 6
        },
        "predicted_at": datetime.datetime.utcnow().isoformat()
    }
