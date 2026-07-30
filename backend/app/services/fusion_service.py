import datetime
from typing import Dict, Any

def run_fusion_mock(student_id: int) -> Dict[str, Any]:
    credibility_score = round(84.0 + (student_id % 5) * 2.5, 1)

    return {
        "student_id": student_id,
        "verified_skills": ["Python", "FastAPI", "React", "TypeScript", "Git", "REST APIs"],
        "hidden_skills": ["Docker", "Redis", "Cloud Practitioner (AWS)", "Agile Methodologies"],
        "unsupported_claims": ["Kubernetes", "GraphQL"],
        "resume_credibility_score": credibility_score,
        "suggestions": [
            "Add 'Docker' and 'AWS Cloud Practitioner' to your resume - they are confirmed on GitHub and LinkedIn but missing on your resume!",
            "Include a GitHub project sample or remove 'Kubernetes' from resume skills to maintain high credibility.",
            "Highlight verified full-stack capabilities at the top of your professional summary."
        ],
        "generated_at": datetime.datetime.utcnow().isoformat()
    }
