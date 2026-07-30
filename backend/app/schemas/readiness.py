from pydantic import BaseModel
from datetime import datetime

class ReadinessScoreOut(BaseModel):
    id: int
    student_id: int
    technical_readiness: float
    communication_readiness: float
    resume_readiness: float
    project_readiness: float
    github_readiness: float
    interview_readiness: float
    overall_readiness: float
    computed_at: datetime

    class Config:
        from_attributes = True
