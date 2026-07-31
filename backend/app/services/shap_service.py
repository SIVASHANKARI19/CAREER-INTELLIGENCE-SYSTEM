"""
Production Explainable AI service (Module 12) — TreeSHAP over the XGBoost
placement model trained in Module 8.

Why this is straightforward for XGBoost specifically (and was one of the
justifications for choosing XGBoost over SVM/MLP in Module 8): TreeSHAP is
EXACT and fast for gradient-boosted trees, unlike KernelSHAP which would be
needed for SVM/neural nets and is both approximate and much slower.

IMPORTANT — how the waterfall numbers are computed:
XGBoost's TreeExplainer produces SHAP values in log-odds (margin) space,
which are additive there but NOT linearly additive once converted to
probability (sigmoid is nonlinear). This service follows the same approach
SHAP's own waterfall plots use: walk features in order of impact magnitude,
apply the sigmoid to the *cumulative* log-odds after each feature is added,
and report each feature's "impact" as the resulting change in probability
at that step. This guarantees the waterfall visually reconstructs to the
model's true predicted probability — but it also means a feature's impact
value is somewhat order-dependent near the boundary; this is a known,
accepted property of explaining nonlinear model outputs and not a bug.
"""

from typing import Dict, Any
import numpy as np
import shap

from app.services.prediction_service import _load_model

FEATURE_DISPLAY_NAMES = {
    "cgpa": "CGPA",
    "ats_score": "Resume ATS Score",
    "github_score": "GitHub Score",
    "project_quality_score": "Project Quality Score",
    "resume_credibility_score": "Resume Credibility Score",
    "verified_skills_count": "Verified Skills Count",
    "hidden_skills_count": "Hidden Skills Count",
    "unsupported_claims_count": "Unsupported Resume Claims",
    "projects_count": "Number of Projects",
    "certifications_count": "Certifications Count",
    "internships_count": "Internship Experience",
    "programming_languages_count": "Programming Languages Known",
    "total_commits": "GitHub Commit Activity",
}

_explainer = None


def _sigmoid(z: float) -> float:
    return 1 / (1 + np.exp(-z))


def _get_explainer(model):
    global _explainer
    if _explainer is None:
        _explainer = shap.TreeExplainer(model)
    return _explainer


def explain_prediction(feature_snapshot: Dict[str, float], prediction_id: int) -> Dict[str, Any]:
    model, feature_order = _load_model()
    x = np.array([[feature_snapshot.get(f, 0) for f in feature_order]])

    explainer = _get_explainer(model)
    raw_shap = explainer.shap_values(x)
    shap_values = np.array(raw_shap[0] if isinstance(raw_shap, list) else raw_shap[0])

    base_value = explainer.expected_value
    if isinstance(base_value, (list, np.ndarray)):
        base_value = float(np.array(base_value).flatten()[0])

    order = np.argsort(-np.abs(shap_values))  # most impactful feature first

    cumulative_logodds = base_value
    base_prob = _sigmoid(cumulative_logodds)
    prev_prob = base_prob

    waterfall = [{"name": "Base Value", "val": round(float(base_prob), 4),
                  "cumulative": round(float(base_prob), 4), "type": "base"}]
    positive_features, negative_features = [], []

    for idx in order:
        cumulative_logodds += float(shap_values[idx])
        new_prob = _sigmoid(cumulative_logodds)
        impact = new_prob - prev_prob
        feat_key = feature_order[idx]
        feat_name = FEATURE_DISPLAY_NAMES.get(feat_key, feat_key)

        entry = {"feature": feat_name, "impact": round(float(impact), 4)}
        (positive_features if impact >= 0 else negative_features).append(entry)
        waterfall.append({
            "name": feat_name, "val": round(float(impact), 4),
            "cumulative": round(float(new_prob), 4),
            "type": "positive" if impact >= 0 else "negative",
        })
        prev_prob = new_prob

    waterfall.append({"name": "Final Prediction", "val": round(float(prev_prob), 4),
                       "cumulative": round(float(prev_prob), 4), "type": "total"})

    return {
        "prediction_id": prediction_id,
        "positive_features": sorted(positive_features, key=lambda f: -f["impact"])[:6],
        "negative_features": sorted(negative_features, key=lambda f: f["impact"])[:6],
        "base_value": round(float(base_prob), 4),
        "output_value": round(float(prev_prob), 4),
        "waterfall_data": waterfall,
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock
# ---------------------------------------------------------------------------
def generate_shap_explanation_mock(prediction_id: int) -> Dict[str, Any]:
    base_val, output_val = 0.50, 0.85
    positive_feats = [
        {"feature": "Resume ATS Score", "impact": 0.14},
        {"feature": "Verified Skills Count", "impact": 0.12},
        {"feature": "GitHub Commit Activity", "impact": 0.08},
        {"feature": "CGPA", "impact": 0.06},
    ]
    negative_feats = [
        {"feature": "Unsupported Resume Claims", "impact": -0.03},
        {"feature": "Certifications Count", "impact": -0.02},
    ]
    waterfall = [
        {"name": "Base Value", "val": 0.50, "cumulative": 0.50, "type": "base"},
        {"name": "Resume ATS Score", "val": 0.14, "cumulative": 0.64, "type": "positive"},
        {"name": "Verified Skills", "val": 0.12, "cumulative": 0.76, "type": "positive"},
        {"name": "GitHub Activity", "val": 0.08, "cumulative": 0.84, "type": "positive"},
        {"name": "CGPA", "val": 0.06, "cumulative": 0.90, "type": "positive"},
        {"name": "Unsupported Claims", "val": -0.03, "cumulative": 0.87, "type": "negative"},
        {"name": "Certifications", "val": -0.02, "cumulative": 0.85, "type": "negative"},
        {"name": "Final Prediction", "val": 0.85, "cumulative": 0.85, "type": "total"},
    ]
    return {
        "prediction_id": prediction_id, "positive_features": positive_feats,
        "negative_features": negative_feats, "base_value": base_val,
        "output_value": output_val, "waterfall_data": waterfall,
    }