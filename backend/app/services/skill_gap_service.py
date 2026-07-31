"""
Production Skill Gap Analysis service (Module 10).

Uses Sentence-BERT embeddings + cosine similarity to compare a student's
actual skill set (resume + GitHub + LinkedIn evidence, via Module 7's
fusion output) against the required skills for their target role — pulled
from admin-managed company_requirements (Module 14) when available, with a
built-in default skill profile per role family as a fallback for when the
admin hasn't populated real company data yet.

Semantic matching (not just exact string match) is the point here: a
company requiring "Node.js" should still register as matched if the
student's evidence says "NodeJS" or "Node JS" — cosine similarity over
sentence embeddings catches this where naive string equality would miss it.
"""

import datetime
from typing import Dict, Any, List, Optional

MATCH_THRESHOLD = 0.72  # cosine similarity above which two skill strings are considered the same skill

_embedder = None


def _get_embedder():
    """Lazy-loaded singleton, shared model choice with Module 4/6/7's
    semantic matching (all-MiniLM-L6-v2) to avoid loading multiple models
    into memory at once."""
    global _embedder
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _embedder = False
    return _embedder


def _cosine_sim_matrix(a, b):
    import numpy as np
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-9)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-9)
    return a_norm @ b_norm.T


# Fallback skill profiles, used only when the admin hasn't populated any
# matching company_requirements yet. Priority/time estimates are curated
# defaults; once real company_requirements data exists it takes over
# automatically and these are bypassed entirely.
DEFAULT_ROLE_PROFILES: Dict[str, Dict[str, Any]] = {
    "data": {
        "skills": ["Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "PyTorch",
                   "Machine Learning", "Data Visualization", "Statistics", "ETL"],
        "priority": {"Python": "High", "SQL": "High", "Pandas": "High", "Machine Learning": "High",
                     "PyTorch": "Medium", "Scikit-Learn": "Medium", "Statistics": "Medium",
                     "NumPy": "Medium", "Data Visualization": "Low", "ETL": "Low"},
        "weeks": {"Python": 2, "SQL": 2, "Pandas": 1, "Machine Learning": 4, "PyTorch": 3,
                  "Scikit-Learn": 2, "Statistics": 3, "NumPy": 1, "Data Visualization": 2, "ETL": 2},
    },
    "frontend": {
        "skills": ["JavaScript", "TypeScript", "React", "HTML", "CSS", "TailwindCSS",
                   "Redux", "Next.js", "REST APIs", "Git"],
        "priority": {"JavaScript": "High", "React": "High", "TypeScript": "High", "CSS": "Medium",
                     "HTML": "Medium", "TailwindCSS": "Medium", "Redux": "Medium",
                     "Next.js": "Low", "REST APIs": "Medium", "Git": "High"},
        "weeks": {"JavaScript": 2, "React": 3, "TypeScript": 2, "CSS": 1, "HTML": 1,
                  "TailwindCSS": 1, "Redux": 2, "Next.js": 2, "REST APIs": 1, "Git": 1},
    },
    "devops": {
        "skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux", "Terraform",
                   "Ansible", "Nginx", "Git", "System Design"],
        "priority": {"Docker": "High", "Kubernetes": "High", "AWS": "High", "CI/CD": "Medium",
                     "Linux": "High", "Terraform": "Medium", "Ansible": "Low",
                     "Nginx": "Low", "Git": "High", "System Design": "Medium"},
        "weeks": {"Docker": 2, "Kubernetes": 4, "AWS": 3, "CI/CD": 2, "Linux": 2,
                  "Terraform": 3, "Ansible": 2, "Nginx": 1, "Git": 1, "System Design": 3},
    },
    "default_sde": {
        "skills": ["Python", "Java", "Data Structures", "Algorithms", "System Design",
                   "Docker", "SQL", "Git", "REST APIs", "CI/CD"],
        "priority": {"Data Structures": "High", "Algorithms": "High", "System Design": "High",
                     "Docker": "Medium", "SQL": "High", "Git": "High", "REST APIs": "Medium",
                     "CI/CD": "Medium", "Python": "High", "Java": "Medium"},
        "weeks": {"Data Structures": 3, "Algorithms": 3, "System Design": 3, "Docker": 2,
                  "SQL": 2, "Git": 1, "REST APIs": 1, "CI/CD": 2, "Python": 2, "Java": 2},
    },
}


def _select_default_profile(target_role: str) -> Dict[str, Any]:
    role_lower = target_role.lower()
    if any(k in role_lower for k in ["data", "ai", "ml", "machine learning", "analyst"]):
        return DEFAULT_ROLE_PROFILES["data"]
    if any(k in role_lower for k in ["frontend", "front-end", "ui", "react developer"]):
        return DEFAULT_ROLE_PROFILES["frontend"]
    if any(k in role_lower for k in ["devops", "cloud", "sre", "infrastructure"]):
        return DEFAULT_ROLE_PROFILES["devops"]
    return DEFAULT_ROLE_PROFILES["default_sde"]


def analyze_skill_gap(
    student_skills: List[str],
    target_role: str,
    company_requirements: Optional[List[Dict[str, Any]]],
    student_id: int,
) -> Dict[str, Any]:

    if company_requirements:
        # Real admin-managed data available for this role — build the
        # required skill set and priority from actual company frequency.
        freq: Dict[str, int] = {}
        for req in company_requirements:
            for skill in req.get("required_skills", []):
                freq[skill] = freq.get(skill, 0) + 1
        required_skills = list(freq.keys())
        priority_map_raw = {s: ("High" if c >= 2 else "Medium") for s, c in freq.items()}
        weeks_map_raw = {s: 2 for s in required_skills}  # generic default; admin data has no time estimate
        source = f"{len(company_requirements)} company requirement(s) on file for roles matching '{target_role}'"
    else:
        profile = _select_default_profile(target_role)
        required_skills = profile["skills"]
        priority_map_raw = profile["priority"]
        weeks_map_raw = profile["weeks"]
        source = f"default skill profile (no admin company requirements yet for '{target_role}')"

    student_skills = [s for s in student_skills if s and s.strip()]
    matched_skills: List[str] = []
    missing_skills: List[str] = []

    if not student_skills or not required_skills:
        missing_skills = list(required_skills)
    else:
        embedder = _get_embedder()
        if embedder:
            import numpy as np
            req_emb = embedder.encode(required_skills, normalize_embeddings=True)
            stu_emb = embedder.encode(student_skills, normalize_embeddings=True)
            sims = _cosine_sim_matrix(np.array(req_emb), np.array(stu_emb))
            for i, req_skill in enumerate(required_skills):
                best = float(np.max(sims[i]))
                if best >= MATCH_THRESHOLD or req_skill.lower() in [s.lower() for s in student_skills]:
                    matched_skills.append(req_skill)
                else:
                    missing_skills.append(req_skill)
        else:
            # Semantic model unavailable in this environment — fall back to
            # exact case-insensitive matching only.
            student_lower = {s.lower() for s in student_skills}
            for req_skill in required_skills:
                (matched_skills if req_skill.lower() in student_lower else missing_skills).append(req_skill)

    priority_map = {s: priority_map_raw.get(s, "Medium") for s in missing_skills}
    estimated_learning_time = {s: f"{weeks_map_raw.get(s, 2)} week{'s' if weeks_map_raw.get(s, 2) != 1 else ''}" for s in missing_skills}

    return {
        "student_id": student_id,
        "target_role": target_role,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills),
        "priority_map": priority_map,
        "estimated_learning_time": estimated_learning_time,
        "match_source": source,
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock
# ---------------------------------------------------------------------------
def analyze_skill_gap_mock(student_id: int, target_role: str = "SDE") -> Dict[str, Any]:
    role_lower = target_role.lower()
    if "data" in role_lower or "ai" in role_lower or "ml" in role_lower:
        matched = ["Python", "SQL", "Git", "REST APIs"]
        missing = ["PyTorch", "Pandas", "Scikit-Learn", "Feature Engineering", "MLOps / MLflow"]
        priority = {"PyTorch": "High", "Pandas": "High", "Scikit-Learn": "Medium", "Feature Engineering": "Medium", "MLOps / MLflow": "Low"}
        estimates = {"PyTorch": "3 weeks", "Pandas": "1 week", "Scikit-Learn": "2 weeks", "Feature Engineering": "2 weeks", "MLOps / MLflow": "4 weeks"}
    else:
        matched = ["Python", "FastAPI", "React", "TypeScript", "SQL", "Git"]
        missing = ["System Design Basics", "Docker & Containers", "Redis Caching", "CI/CD Pipelines", "AWS S3/EC2"]
        priority = {"System Design Basics": "High", "Docker & Containers": "High", "Redis Caching": "Medium", "CI/CD Pipelines": "Medium", "AWS S3/EC2": "Low"}
        estimates = {"System Design Basics": "3 weeks", "Docker & Containers": "2 weeks", "Redis Caching": "1 week", "CI/CD Pipelines": "2 weeks", "AWS S3/EC2": "3 weeks"}
    return {
        "student_id": student_id, "target_role": target_role, "matched_skills": matched,
        "missing_skills": missing, "priority_map": priority, "estimated_learning_time": estimates,
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }