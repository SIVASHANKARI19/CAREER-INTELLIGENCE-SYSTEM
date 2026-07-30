from sqlalchemy import Column, Integer, Float, JSON, ForeignKey, DateTime
import datetime
from app.core.database import Base

class ShapExplanation(Base):
    __tablename__ = "shap_explanations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey("placement_predictions.id", ondelete="CASCADE"), nullable=False)
    positive_features = Column(JSON, default=list, nullable=True)
    negative_features = Column(JSON, default=list, nullable=True)
    base_value = Column(Float, default=0.0, nullable=False)
    output_value = Column(Float, default=0.0, nullable=False)
    waterfall_data = Column(JSON, default=list, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
