from sqlalchemy import Column, Integer, String, JSON, DateTime, Enum as SQLEnum
import datetime
import enum
from app.core.database import Base

class ModelStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    TRAINING = "training"

class ModelRegistry(Base):
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(SQLEnum(ModelStatus), default=ModelStatus.ACTIVE, nullable=False)
    trained_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    metrics = Column(JSON, default=dict, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
