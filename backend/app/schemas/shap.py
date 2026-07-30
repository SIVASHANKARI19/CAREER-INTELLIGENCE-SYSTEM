from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ShapRequest(BaseModel):
    prediction_id: int

class ShapFeatureImpact(BaseModel):
    feature: str
    impact: float

class ShapExplanationOut(BaseModel):
    id: int
    prediction_id: int
    positive_features: List[ShapFeatureImpact] = []
    negative_features: List[ShapFeatureImpact] = []
    base_value: float
    output_value: float
    waterfall_data: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True
