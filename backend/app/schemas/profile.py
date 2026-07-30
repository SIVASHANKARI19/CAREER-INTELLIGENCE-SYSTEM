from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime

class ProjectItem(BaseModel):
    title: str
    description: str
    tech_stack: List[str] = []
    link: Optional[str] = None

class CertificationItem(BaseModel):
    name: str
    issuer: str
    date: Optional[str] = None
    link: Optional[str] = None

class InternshipItem(BaseModel):
    company: str
    role: str
    duration: Optional[str] = None
    description: Optional[str] = None

class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    cgpa: Optional[float] = None
    year_of_study: Optional[int] = None
    career_goal: Optional[str] = None
    programming_languages: Optional[List[str]] = None
    projects: Optional[List[Dict[str, Any]]] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    internships: Optional[List[Dict[str, Any]]] = None
    achievements: Optional[List[str]] = None
    github_url: Optional[str] = None

class StudentProfileOut(BaseModel):
    id: int
    user_id: int
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    cgpa: Optional[float] = None
    year_of_study: Optional[int] = None
    career_goal: Optional[str] = None
    programming_languages: List[str] = []
    projects: List[Dict[str, Any]] = []
    certifications: List[Dict[str, Any]] = []
    internships: List[Dict[str, Any]] = []
    achievements: List[str] = []
    github_url: Optional[str] = None
    resume_file_path: Optional[str] = None
    linkedin_pdf_path: Optional[str] = None
    profile_completion_pct: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ProfileCompletionResponse(BaseModel):
    student_id: int
    completion_percentage: int
    missing_fields: List[str]
