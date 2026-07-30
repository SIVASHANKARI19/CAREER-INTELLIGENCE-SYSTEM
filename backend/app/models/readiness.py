from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
import datetime
from app.core.database import Base

class ReadinessScore(Base):
    __tablename__ = "readiness_scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    technical_readiness = Column(Float, default=0.0, nullable=False)
    communication_readiness = Column(Float, default=0.0, nullable=False)
    resume_readiness = Column(Float, default=0.0, nullable=False)
    project_readiness = Column(Float, default=0.0, nullable=False)
    github_readiness = Column(Float, default=0.0, nullable=False)
    interview_readiness = Column(Float, default=0.0, nullable=False)
    overall_readiness = Column(Float, default=0.0, nullable=False)
    computed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
