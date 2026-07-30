from sqlalchemy import Column, Integer, Float, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class FusionResult(Base):
    __tablename__ = "fusion_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    verified_skills = Column(JSON, default=list, nullable=True)
    hidden_skills = Column(JSON, default=list, nullable=True)
    unsupported_claims = Column(JSON, default=list, nullable=True)
    resume_credibility_score = Column(Float, default=0.0, nullable=False)
    suggestions = Column(JSON, default=list, nullable=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
