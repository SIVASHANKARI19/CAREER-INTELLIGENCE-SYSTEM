from sqlalchemy import Column, Integer, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    weekly_plan = Column(JSON, default=list, nullable=True)
    monthly_plan = Column(JSON, default=list, nullable=True)
    recommended_projects = Column(JSON, default=list, nullable=True)
    recommended_courses = Column(JSON, default=list, nullable=True)
    interview_questions = Column(JSON, default=list, nullable=True)
    resources = Column(JSON, default=list, nullable=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
