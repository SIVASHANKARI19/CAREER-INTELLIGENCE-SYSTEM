from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.model_registry import ModelStatus

class CompanyRequirementCreate(BaseModel):
    company_name: str
    role: str
    required_skills: List[str] = []
    min_cgpa: Optional[float] = None
    notes: Optional[str] = None

class CompanyRequirementUpdate(BaseModel):
    company_name: Optional[str] = None
    role: Optional[str] = None
    required_skills: Optional[List[str]] = None
    min_cgpa: Optional[float] = None
    notes: Optional[str] = None

class CompanyRequirementOut(BaseModel):
    id: int
    company_name: str
    role: str
    required_skills: List[str] = []
    min_cgpa: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ModelRegistryOut(BaseModel):
    id: int
    model_name: str
    version: str
    status: ModelStatus
    trained_at: datetime
    metrics: Dict[str, Any] = {}

    class Config:
        from_attributes = True

class ModelRetrainResponse(BaseModel):
    message: str
    model_name: str
    new_version: str
    status: str
    metrics: Dict[str, Any]

class AdminAnalyticsOut(BaseModel):
    total_students: int
    avg_readiness_score: float
    avg_ats_score: float
    avg_placement_probability: float
    industry_ready_count: int
    top_missing_skills: List[Dict[str, Any]]
    department_stats: List[Dict[str, Any]]
