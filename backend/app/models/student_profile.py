from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from app.core.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = Column(String(150), nullable=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    cgpa = Column(Float, nullable=True)
    year_of_study = Column(Integer, nullable=True)
    career_goal = Column(String(150), nullable=True)
    programming_languages = Column(JSON, default=list, nullable=True)
    projects = Column(JSON, default=list, nullable=True)
    certifications = Column(JSON, default=list, nullable=True)
    internships = Column(JSON, default=list, nullable=True)
    achievements = Column(JSON, default=list, nullable=True)
    github_url = Column(String(255), nullable=True)
    resume_file_path = Column(String(255), nullable=True)
    linkedin_pdf_path = Column(String(255), nullable=True)
    profile_completion_pct = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="profile")
