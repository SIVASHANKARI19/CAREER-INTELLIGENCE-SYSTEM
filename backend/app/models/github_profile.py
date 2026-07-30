from sqlalchemy import Column, Integer, Float, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class GithubAnalysis(Base):
    __tablename__ = "github_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    repositories = Column(JSON, default=list, nullable=True)
    languages_summary = Column(JSON, default=dict, nullable=True)
    total_commits = Column(Integer, default=0, nullable=False)
    github_score = Column(Float, default=0.0, nullable=False)
    project_quality_score = Column(Float, default=0.0, nullable=False)
    skill_confidence = Column(JSON, default=dict, nullable=True)
    analyzed_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
