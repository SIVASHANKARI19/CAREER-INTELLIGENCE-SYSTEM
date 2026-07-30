from sqlalchemy import Column, Integer, Float, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class SimulatorSession(Base):
    __tablename__ = "simulator_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    baseline_probability = Column(Float, default=0.0, nullable=False)
    applied_changes = Column(JSON, default=list, nullable=True)
    simulated_probability = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
