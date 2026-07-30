from typing import Dict, Any

def generate_shap_explanation_mock(prediction_id: int) -> Dict[str, Any]:
    base_val = 0.50
    output_val = 0.85

    positive_feats = [
        {"feature": "ATS Resume Score (>80%)", "impact": 0.14},
        {"feature": "Verified Full Stack Skills (>=5)", "impact": 0.12},
        {"feature": "Strong GitHub Commit History", "impact": 0.08},
        {"feature": "High CGPA (>=8.5)", "impact": 0.06}
    ]

    negative_feats = [
        {"feature": "Missing System Design Project", "impact": -0.03},
        {"feature": "No Cloud Certification On Resume", "impact": -0.02}
    ]

    waterfall = [
        {"name": "Base Value", "val": 0.50, "cumulative": 0.50, "type": "base"},
        {"name": "ATS Resume Score", "val": 0.14, "cumulative": 0.64, "type": "positive"},
        {"name": "Verified Skills", "val": 0.12, "cumulative": 0.76, "type": "positive"},
        {"name": "GitHub Activity", "val": 0.08, "cumulative": 0.84, "type": "positive"},
        {"name": "High CGPA", "val": 0.06, "cumulative": 0.90, "type": "positive"},
        {"name": "Missing System Design", "val": -0.03, "cumulative": 0.87, "type": "negative"},
        {"name": "No Cloud Cert", "val": -0.02, "cumulative": 0.85, "type": "negative"},
        {"name": "Final Prediction", "val": 0.85, "cumulative": 0.85, "type": "total"}
    ]

    return {
        "id": 101,
        "prediction_id": prediction_id,
        "positive_features": positive_feats,
        "negative_features": negative_feats,
        "base_value": base_val,
        "output_value": output_val,
        "waterfall_data": waterfall
    }
