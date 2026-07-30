import datetime
from typing import Dict, Any

def analyze_github_mock(github_url: str, student_id: int = 1) -> Dict[str, Any]:
    username = github_url.rstrip("/").split("/")[-1] if github_url else f"student{student_id}"
    
    total_commits = 340 + (student_id % 5) * 85
    github_score = round(78.0 + (student_id % 6) * 3.2, 1)
    if github_score > 98.0:
        github_score = 94.5
        
    project_quality_score = round(81.5 + (student_id % 4) * 4.0, 1)

    return {
        "student_id": student_id,
        "repositories": [
            {
                "name": "fullstack-placement-engine",
                "description": "AI-Powered placement prediction & career intelligence dashboard",
                "languages": ["TypeScript", "Python", "HTML", "CSS"],
                "stars": 14,
                "forks": 4,
                "commits": 142,
                "readme_quality": "High (Detailed architecture diagram & API specs)"
            },
            {
                "name": "algo-visualizer-react",
                "description": "Interactive data structures and algorithms visualizer",
                "languages": ["TypeScript", "JavaScript"],
                "stars": 28,
                "forks": 8,
                "commits": 89,
                "readme_quality": "Medium (Setup instructions included)"
            },
            {
                "name": "fastapi-microservice-boilerplate",
                "description": "Production-ready template for FastAPI with JWT & SQLAlchemy",
                "languages": ["Python", "Dockerfile"],
                "stars": 39,
                "forks": 12,
                "commits": 115,
                "readme_quality": "High (Complete documentation)"
            }
        ],
        "languages_summary": {
            "Python": "42%",
            "TypeScript": "35%",
            "JavaScript": "13%",
            "HTML/CSS": "7%",
            "Docker": "3%"
        },
        "total_commits": total_commits,
        "github_score": github_score,
        "project_quality_score": project_quality_score,
        "skill_confidence": {
            "Python": 0.92,
            "FastAPI": 0.88,
            "React": 0.85,
            "TypeScript": 0.81,
            "Docker": 0.65,
            "Git": 0.95
        },
        "analyzed_at": datetime.datetime.utcnow().isoformat()
    }
