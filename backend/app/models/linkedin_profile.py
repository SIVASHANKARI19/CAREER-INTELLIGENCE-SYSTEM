from sqlalchemy import Column, Integer, String, Text, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class LinkedinAnalysis(Base):
    __tablename__ = "linkedin_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    headline = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    extracted_skills = Column(JSON, default=list, nullable=True)
    extracted_experience = Column(JSON, default=list, nullable=True)
    extracted_education = Column(JSON, default=list, nullable=True)
    extracted_certificates = Column(JSON, default=list, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
