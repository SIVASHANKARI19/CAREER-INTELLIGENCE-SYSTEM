from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AppliedChangeItem(BaseModel):
    action: str
    category: Optional[str] = "certification"

class SimulatorRequest(BaseModel):
    student_id: Optional[int] = None
    applied_changes: List[AppliedChangeItem] = []

class SimulatorSessionOut(BaseModel):
    id: int
    student_id: int
    baseline_probability: float
    applied_changes: List[Dict[str, Any]] = []
    simulated_probability: float
    delta: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True
