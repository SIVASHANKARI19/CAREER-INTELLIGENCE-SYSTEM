from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.placement_prediction import ReadinessLevel

class PredictionRequest(BaseModel):
    student_id: Optional[int] = None

class PlacementPredictionOut(BaseModel):
    id: int
    student_id: int
    placement_probability: float
    expected_salary_range: str
    confidence: float
    readiness_level: ReadinessLevel
    model_version: str
    feature_snapshot: Dict[str, Any] = {}
    predicted_at: datetime

    class Config:
        from_attributes = True
