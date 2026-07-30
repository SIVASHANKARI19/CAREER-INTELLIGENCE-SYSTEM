from sqlalchemy import Column, Integer, Text, Float, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    raw_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=list, nullable=True)
    extracted_projects = Column(JSON, default=list, nullable=True)
    extracted_certifications = Column(JSON, default=list, nullable=True)
    extracted_experience = Column(JSON, default=list, nullable=True)
    extracted_education = Column(JSON, default=list, nullable=True)
    ats_score = Column(Float, default=0.0, nullable=False)
    suggestions = Column(JSON, default=list, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
