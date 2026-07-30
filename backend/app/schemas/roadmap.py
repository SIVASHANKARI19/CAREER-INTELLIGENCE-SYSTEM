from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class RoadmapRequest(BaseModel):
    student_id: Optional[int] = None

class LearningRoadmapOut(BaseModel):
    id: int
    student_id: int
    weekly_plan: List[Dict[str, Any]] = []
    monthly_plan: List[Dict[str, Any]] = []
    recommended_projects: List[Dict[str, Any]] = []
    recommended_courses: List[Dict[str, Any]] = []
    interview_questions: List[Dict[str, Any]] = []
    resources: List[Dict[str, Any]] = []
    generated_at: datetime

    class Config:
        from_attributes = True
