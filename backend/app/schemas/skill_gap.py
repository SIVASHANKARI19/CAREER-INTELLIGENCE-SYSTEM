from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SkillGapRequest(BaseModel):
    student_id: Optional[int] = None
    target_role: str

class SkillGapResultOut(BaseModel):
    id: int
    student_id: int
    target_role: str
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    priority_map: Dict[str, str] = {}
    estimated_learning_time: Dict[str, str] = {}
    generated_at: datetime

    class Config:
        from_attributes = True
