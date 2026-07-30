from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LinkedinAnalyzeRequest(BaseModel):
    student_id: Optional[int] = None

class LinkedinAnalysisOut(BaseModel):
    id: int
    student_id: int
    headline: Optional[str] = None
    summary: Optional[str] = None
    extracted_skills: List[str] = []
    extracted_experience: List[Dict[str, Any]] = []
    extracted_education: List[Dict[str, Any]] = []
    extracted_certificates: List[Dict[str, Any]] = []
    analyzed_at: datetime

    class Config:
        from_attributes = True
