from sqlalchemy import Column, Integer, String, Float, Text, JSON, DateTime
import datetime
from app.core.database import Base

class CompanyRequirement(Base):
    __tablename__ = "company_requirements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_name = Column(String(150), nullable=False)
    role = Column(String(150), nullable=False)
    required_skills = Column(JSON, default=list, nullable=True)
    min_cgpa = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
