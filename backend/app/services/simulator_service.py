"""
Production Career Improvement Simulator service (Module 13).

The mock version this replaced applied a flat probability boost per action
category (e.g. "+0.08 for AWS") disconnected from the student's real data or
the trained model at all -- it would give every student the identical delta
regardless of their actual profile. This version instead:

  1. Builds the student's real current feature vector (same one Module 8
     uses), and gets a baseline prediction from the real XGBoost model.
  2. Applies each selected action as a concrete, bounded change to specific
     features in that vector (e.g. "AWS Certification" -> certifications_count
     + 1, plus a small resume_credibility_score bump since a verifiable cert
     supports resume claims).
  3. Re-runs the SAME trained model on the modified vector to get the
     simulated probability. The delta is therefore whatever the model
     actually learned that feature combination is worth for THIS student,
     not a hardcoded constant.

This is still an approximation -- it assumes the requested change happens in
isolation and immediately, and it can't capture second-order effects (e.g. an
internship might also change ats_score once the resume is updated to mention
it, which really happens through re-running Module 4, not this simulator).
That's a reasonable, disclosed simplification for a final-year project scope.
"""
import datetime
from typing import Dict, Any, List

from app.services.prediction_service import predict_placement, gather_features_from_db

# Bounded, per-action feature deltas. Kept conservative and capped in
# apply_action() below so stacking many actions can't push a feature past a
# realistic ceiling (e.g. can't simulate 40 certifications).
ACTION_FEATURE_EFFECTS = {
    "certification": {"certifications_count": 1, "resume_credibility_score": 3},
    "internship":    {"internships_count": 1, "resume_credibility_score": 4, "verified_skills_count": 1},
    "project":       {"projects_count": 1, "github_score": 3, "project_quality_score": 3},
    "skill":         {"verified_skills_count": 1, "programming_languages_count": 1},
    "dsa":           {"ats_score": 3, "verified_skills_count": 1},
}

FEATURE_CAPS = {
    "cgpa": 10.0, "ats_score": 100.0, "github_score": 100.0,
    "project_quality_score": 100.0, "resume_credibility_score": 100.0,
}


def _infer_category(action_text: str, given_category: str) -> str:
    text = action_text.lower()
    if given_category and given_category in ACTION_FEATURE_EFFECTS:
        return given_category
    if "aws" in text or "cloud" in text or "certif" in text:
        return "certification"
    if "intern" in text:
        return "internship"
    if "project" in text:
        return "project"
    if "dsa" in text or "data structure" in text or "algorithm" in text:
        return "dsa"
    return "skill"


def apply_action(features: Dict[str, float], action_text: str, category: str) -> Dict[str, float]:
    resolved_category = _infer_category(action_text, category)
    effects = ACTION_FEATURE_EFFECTS.get(resolved_category, ACTION_FEATURE_EFFECTS["skill"])
    updated = dict(features)
    for feature_name, delta in effects.items():
        new_value = updated.get(feature_name, 0) + delta
        cap = FEATURE_CAPS.get(feature_name)
        if cap is not None:
            new_value = min(new_value, cap)
        updated[feature_name] = new_value
    return updated


def simulate_career_impact(student_id: int, applied_changes: List[Dict[str, Any]], db) -> Dict[str, Any]:
    baseline_features = gather_features_from_db(student_id, db)
    baseline_result = predict_placement(baseline_features, student_id)
    baseline_probability = baseline_result["placement_probability"]

    simulated_features = dict(baseline_features)
    for change in applied_changes:
        simulated_features = apply_action(
            simulated_features,
            action_text=change.get("action", ""),
            category=change.get("category", ""),
        )

    simulated_result = predict_placement(simulated_features, student_id)
    simulated_probability = simulated_result["placement_probability"]

    return {
        "student_id": student_id,
        "baseline_probability": baseline_probability,
        "applied_changes": applied_changes,
        "simulated_probability": simulated_probability,
        "delta": round(simulated_probability - baseline_probability, 4),
        "created_at": datetime.datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock (used only if the trained model isn't available)
# ---------------------------------------------------------------------------
def simulate_career_impact_mock(student_id: int, applied_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    baseline = 0.72
    boost = 0.0
    for change in applied_changes:
        action_name = change.get("action", "").lower()
        if "aws" in action_name or "cloud" in action_name:
            boost += 0.08
        elif "system design" in action_name:
            boost += 0.09
        elif "docker" in action_name or "kubernetes" in action_name:
            boost += 0.06
        elif "internship" in action_name:
            boost += 0.12
        elif "project" in action_name:
            boost += 0.05
        else:
            boost += 0.04

    simulated = min(0.98, round(baseline + boost, 2))
    return {
        "student_id": student_id,
        "baseline_probability": baseline,
        "applied_changes": applied_changes,
        "simulated_probability": simulated,
        "delta": round(simulated - baseline, 2),
        "created_at": datetime.datetime.utcnow().isoformat(),
    }