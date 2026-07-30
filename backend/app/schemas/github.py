from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class GithubAnalyzeRequest(BaseModel):
    github_url: str

class GithubAnalysisOut(BaseModel):
    id: int
    student_id: int
    repositories: List[Dict[str, Any]] = []
    languages_summary: Dict[str, Any] = {}
    total_commits: int = 0
    github_score: float = 0.0
    project_quality_score: float = 0.0
    skill_confidence: Dict[str, float] = {}
    analyzed_at: datetime

    class Config:
        from_attributes = True
