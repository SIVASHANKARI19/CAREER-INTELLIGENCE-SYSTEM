from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Enum as SQLEnum
import datetime
import enum
from app.core.database import Base

class ReadinessLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    INDUSTRY_READY = "industry_ready"

class PlacementPrediction(Base):
    __tablename__ = "placement_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    placement_probability = Column(Float, default=0.0, nullable=False)
    expected_salary_range = Column(String(50), nullable=True)
    confidence = Column(Float, default=0.0, nullable=False)
    readiness_level = Column(SQLEnum(ReadinessLevel), default=ReadinessLevel.BEGINNER, nullable=False)
    model_version = Column(String(50), default="1.0.0", nullable=False)
    feature_snapshot = Column(JSON, default=dict, nullable=True)
    predicted_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
