from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class SkillGapResult(Base):
    __tablename__ = "skill_gap_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    target_role = Column(String(150), nullable=False)
    matched_skills = Column(JSON, default=list, nullable=True)
    missing_skills = Column(JSON, default=list, nullable=True)
    priority_map = Column(JSON, default=dict, nullable=True)
    estimated_learning_time = Column(JSON, default=dict, nullable=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
