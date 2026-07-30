from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FusionRequest(BaseModel):
    student_id: Optional[int] = None

class FusionResultOut(BaseModel):
    id: int
    student_id: int
    verified_skills: List[str] = []
    hidden_skills: List[str] = []
    unsupported_claims: List[str] = []
    resume_credibility_score: float = 0.0
    suggestions: List[str] = []
    generated_at: datetime

    class Config:
        from_attributes = True
