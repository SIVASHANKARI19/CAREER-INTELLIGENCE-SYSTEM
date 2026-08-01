from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.placement_prediction import PlacementPrediction
from app.models.shap_explanation import ShapExplanation
from app.schemas.shap import ShapRequest, ShapExplanationOut
from app.api.deps import get_current_user
from app.services.shap_service import explain_prediction
from app.services.prediction_service import predict_placement, gather_features_from_db

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


@router.get("/student/{student_id}", response_model=ShapExplanationOut)
def get_shap_by_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convenience route: resolves the student's most recent placement
    prediction internally, so frontend callers never need to know that SHAP
    is actually keyed by prediction_id, a different primary key than
    student_id. If no prediction exists yet, runs one automatically (using
    the student's current real feature vector) rather than 404ing —
    Explainable AI is meaningless without a prediction to explain, so
    generating one on demand here is the more useful behavior."""
    prediction = (
        db.query(PlacementPrediction)
        .filter(PlacementPrediction.student_id == student_id)
        .order_by(PlacementPrediction.predicted_at.desc())
        .first()
    )

    if not prediction:
        features = gather_features_from_db(student_id, db)
        try:
            result = predict_placement(features, student_id)
        except FileNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

        prediction = PlacementPrediction(student_id=student_id)
        db.add(prediction)
        prediction.placement_probability = result["placement_probability"]
        prediction.expected_salary_range = result["expected_salary_range"]
        prediction.confidence = result["confidence"]
        prediction.readiness_level = result["readiness_level"]
        prediction.model_version = result["model_version"]
        prediction.feature_snapshot = result["feature_snapshot"]
        db.commit()
        db.refresh(prediction)

    return _run_and_persist(prediction.id, db)


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