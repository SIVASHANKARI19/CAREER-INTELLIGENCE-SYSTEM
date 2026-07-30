import datetime
from typing import Dict, Any

def analyze_skill_gap_mock(student_id: int, target_role: str = "SDE") -> Dict[str, Any]:
    role_lower = target_role.lower()

    if "data" in role_lower or "ai" in role_lower or "ml" in role_lower:
        matched = ["Python", "SQL", "Git", "REST APIs"]
        missing = ["PyTorch", "Pandas", "Scikit-Learn", "Feature Engineering", "MLOps / MLflow"]
        priority = {
            "PyTorch": "High",
            "Pandas": "High",
            "Scikit-Learn": "Medium",
            "Feature Engineering": "Medium",
            "MLOps / MLflow": "Low"
        }
        estimates = {
            "PyTorch": "3 weeks",
            "Pandas": "1 week",
            "Scikit-Learn": "2 weeks",
            "Feature Engineering": "2 weeks",
            "MLOps / MLflow": "4 weeks"
        }
    else:
        # Default Full-Stack / SDE
        matched = ["Python", "FastAPI", "React", "TypeScript", "SQL", "Git"]
        missing = ["System Design Basics", "Docker & Containers", "Redis Caching", "CI/CD Pipelines", "AWS S3/EC2"]
        priority = {
            "System Design Basics": "High",
            "Docker & Containers": "High",
            "Redis Caching": "Medium",
            "CI/CD Pipelines": "Medium",
            "AWS S3/EC2": "Low"
        }
        estimates = {
            "System Design Basics": "3 weeks",
            "Docker & Containers": "2 weeks",
            "Redis Caching": "1 week",
            "CI/CD Pipelines": "2 weeks",
            "AWS S3/EC2": "3 weeks"
        }

    return {
        "student_id": student_id,
        "target_role": target_role,
        "matched_skills": matched,
        "missing_skills": missing,
        "priority_map": priority,
        "estimated_learning_time": estimates,
        "generated_at": datetime.datetime.utcnow().isoformat()
    }
