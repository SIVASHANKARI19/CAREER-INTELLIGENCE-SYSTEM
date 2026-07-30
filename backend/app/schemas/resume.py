from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

class ResumeAnalyzeRequest(BaseModel):
    student_id: Optional[int] = None

class ResumeAnalysisOut(BaseModel):
    id: int
    student_id: int
    raw_text: Optional[str] = None
    extracted_skills: List[str] = []
    extracted_projects: List[Dict[str, Any]] = []
    extracted_certifications: List[Dict[str, Any]] = []
    extracted_experience: List[Dict[str, Any]] = []
    extracted_education: List[Dict[str, Any]] = []
    ats_score: float = 0.0
    suggestions: List[str] = []
    analyzed_at: datetime

    class Config:
        from_attributes = True
