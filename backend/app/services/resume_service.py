import datetime
from typing import Dict, Any

def analyze_resume_mock(student_id: int) -> Dict[str, Any]:
    # Dynamic deterministic variation per student_id
    base_score = 72.5 + (student_id % 7) * 3.5
    if base_score > 96.0:
        base_score = 92.0

    return {
        "student_id": student_id,
        "raw_text": f"Curriculum Vitae for Student #{student_id}. Experienced software engineering candidate with strong computer science fundamentals, full-stack web development experience using React, FastAPI, Python, SQL, and Git.",
        "extracted_skills": ["Python", "FastAPI", "React", "TypeScript", "SQLAlchemy", "Git", "REST APIs", "TailwindCSS"],
        "extracted_projects": [
            {
                "title": "AI Career Placement Intelligence Platform",
                "tech_stack": ["FastAPI", "React", "TypeScript", "MySQL"],
                "description": "Engineered full-stack placement readiness portal with explainable AI placement prediction and roadmap generation."
            },
            {
                "title": "Distributed Task Scheduler",
                "tech_stack": ["Python", "Redis", "Docker"],
                "description": "Implemented high-throughput async queue system handling 10k requests/sec."
            }
        ],
        "extracted_certifications": [
            {"name": "AWS Certified Cloud Practitioner", "issuer": "Amazon Web Services", "date": "2024-05"},
            {"name": "MetaData Engineering Professional", "issuer": "Meta", "date": "2023-11"}
        ],
        "extracted_experience": [
            {
                "company": "TechNova Solutions",
                "role": "Software Engineering Intern",
                "duration": "3 months",
                "description": "Developed REST microservices and improved front-end page speed by 40%."
            }
        ],
        "extracted_education": [
            {
                "degree": "B.Tech in Computer Science & Engineering",
                "institution": "National Institute of Technology",
                "graduation_year": 2025
            }
        ],
        "ats_score": round(base_score, 1),
        "suggestions": [
            "Quantify project achievements with metrics (e.g. reduced latency by 35%).",
            "Add Docker and Kubernetes keywords under cloud DevOps competencies.",
            "Include direct URL links to GitHub project repositories in header."
        ],
        "analyzed_at": datetime.datetime.utcnow().isoformat()
    }
