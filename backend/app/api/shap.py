from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.placement_prediction import PlacementPrediction
from app.models.shap_explanation import ShapExplanation
from app.schemas.shap import ShapRequest, ShapExplanationOut
from app.api.deps import get_current_user
from app.services.shap_service import explain_prediction

router = APIRouter(prefix="/api/shap", tags=["Explainable AI"])


def _run_and_persist(prediction_id: int, db: Session) -> ShapExplanation:
    prediction = db.query(PlacementPrediction).filter(PlacementPrediction.id == prediction_id).first()
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found.")
    if not prediction.feature_snapshot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This prediction has no stored feature snapshot to explain."
        )

    try:
        result = explain_prediction(prediction.feature_snapshot, prediction_id)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"SHAP explanation failed: {str(e)}")

    record = db.query(ShapExplanation).filter(ShapExplanation.prediction_id == prediction_id).first()
    if record is None:
        record = ShapExplanation(prediction_id=prediction_id)
        db.add(record)

    record.positive_features = result["positive_features"]
    record.negative_features = result["negative_features"]
    record.base_value = result["base_value"]
    record.output_value = result["output_value"]
    record.waterfall_data = result["waterfall_data"]

    db.commit()
    db.refresh(record)
    return record


@router.post("", response_model=ShapExplanationOut)
def generate_shap(
    body: ShapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return _run_and_persist(body.prediction_id, db)


@router.get("/{prediction_id}", response_model=ShapExplanationOut)
def get_shap_explanation(
    prediction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(ShapExplanation).filter(ShapExplanation.prediction_id == prediction_id).first()
    if not record:
        return _run_and_persist(prediction_id, db)
    return record