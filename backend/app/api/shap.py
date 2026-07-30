from fastapi import APIRouter, Depends
from app.models.user import User
from app.schemas.shap import ShapRequest, ShapExplanationOut
from app.api.deps import get_current_user
from app.services.shap_service import generate_shap_explanation_mock

router = APIRouter(prefix="/api/shap", tags=["Explainable AI"])

@router.post("", response_model=ShapExplanationOut)
def generate_shap(
    body: ShapRequest,
    current_user: User = Depends(get_current_user)
):
    mock_data = generate_shap_explanation_mock(body.prediction_id)
    return mock_data

@router.get("/{prediction_id}", response_model=ShapExplanationOut)
def get_shap_explanation(
    prediction_id: int,
    current_user: User = Depends(get_current_user)
):
    mock_data = generate_shap_explanation_mock(prediction_id)
    return mock_data
