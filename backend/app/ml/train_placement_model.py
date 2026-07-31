"""
Training script for the Placement Readiness Prediction model (Module 8).

IMPORTANT — READ BEFORE USING IN A REAL DEMO:
This project has no real historical placement outcomes yet (no college
placement-cell dataset of "student features -> got placed or not"). Rather
than block the whole module on that, this script generates a SYNTHETIC but
realistically-structured dataset: features are sampled from plausible
distributions, and outcomes are sampled probabilistically from a weighted
formula + noise (not a hard rule), so the model has to genuinely learn
patterns rather than memorize a lookup table.

Once your college/admin provides real placement records (via Module 14's
Dataset Management), replace generate_synthetic_dataset() with a loader for
the real CSV/DB table and retrain — everything downstream (feature order,
model I/O contract) stays the same. Clearly disclose in your report that
initial results are demonstrated on synthetic data pending real records.

Run: python -m app.ml.train_placement_model
Outputs: app/ml_models/placement_xgboost.joblib, feature_order.json,
comparison metrics printed to stdout for your report/viva.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score
import xgboost as xgb
import joblib

FEATURE_ORDER = [
    "cgpa", "ats_score", "github_score", "project_quality_score",
    "resume_credibility_score", "verified_skills_count", "hidden_skills_count",
    "unsupported_claims_count", "projects_count", "certifications_count",
    "internships_count", "programming_languages_count", "total_commits",
]

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml_models")
os.makedirs(MODEL_DIR, exist_ok=True)


def generate_synthetic_dataset(n: int = 3000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    cgpa = np.clip(rng.normal(7.4, 1.1, n), 4.5, 10.0)
    ats_score = np.clip(rng.normal(68, 16, n), 10, 100)
    github_score = np.clip(rng.normal(60, 20, n), 0, 100)
    project_quality_score = np.clip(rng.normal(62, 18, n), 0, 100)
    resume_credibility_score = np.clip(rng.normal(70, 15, n), 0, 100)
    verified_skills_count = rng.poisson(6, n)
    hidden_skills_count = rng.poisson(2, n)
    unsupported_claims_count = rng.poisson(1.5, n)
    projects_count = rng.poisson(3, n)
    certifications_count = rng.poisson(1.2, n)
    internships_count = rng.binomial(2, 0.35, n)
    programming_languages_count = rng.poisson(4, n) + 1
    total_commits = np.clip(rng.normal(250, 180, n), 0, None).astype(int)

    df = pd.DataFrame({
        "cgpa": cgpa, "ats_score": ats_score, "github_score": github_score,
        "project_quality_score": project_quality_score,
        "resume_credibility_score": resume_credibility_score,
        "verified_skills_count": verified_skills_count,
        "hidden_skills_count": hidden_skills_count,
        "unsupported_claims_count": unsupported_claims_count,
        "projects_count": projects_count, "certifications_count": certifications_count,
        "internships_count": internships_count,
        "programming_languages_count": programming_languages_count,
        "total_commits": total_commits,
    })

    # Weighted "true" logit — plausible relative importances, not ground truth.
    # Deliberately includes noise so the model can't just memorize the formula.
    logit = (
        0.55 * (df.cgpa - 7.0)
        + 0.030 * (df.ats_score - 60)
        + 0.028 * (df.github_score - 55)
        + 0.022 * (df.project_quality_score - 55)
        + 0.018 * (df.resume_credibility_score - 60)
        + 0.15 * df.verified_skills_count
        - 0.25 * df.unsupported_claims_count
        + 0.20 * df.projects_count
        + 0.30 * df.certifications_count
        + 0.55 * df.internships_count
        + 0.004 * df.total_commits
        - 1.6
    )
    noise = rng.normal(0, 1.1, n)
    prob_true = 1 / (1 + np.exp(-(logit + noise)))
    placed = rng.binomial(1, prob_true)

    df["placed"] = placed
    return df


def train_and_compare(df: pd.DataFrame):
    X = df[FEATURE_ORDER]
    y = df["placed"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    models = {
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42),
        "SVM (RBF kernel)": SVC(kernel="rbf", probability=True, random_state=42),
        "Neural Network (MLP)": MLPClassifier(hidden_layer_sizes=(32, 16), max_iter=800, random_state=42),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=250, max_depth=4, learning_rate=0.05,
            subsample=0.85, colsample_bytree=0.85, eval_metric="logloss",
            random_state=42,
        ),
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        preds = (proba >= 0.5).astype(int)
        results[name] = {
            "accuracy": round(accuracy_score(y_test, preds), 4),
            "roc_auc": round(roc_auc_score(y_test, proba), 4),
            "f1": round(f1_score(y_test, preds), 4),
        }

    print("\n=== Model Comparison (synthetic dataset, 20% held-out test set) ===")
    print(f"{'Model':<22}{'Accuracy':<12}{'ROC-AUC':<12}{'F1':<10}")
    for name, m in results.items():
        print(f"{name:<22}{m['accuracy']:<12}{m['roc_auc']:<12}{m['f1']:<10}")

    xgb_model = models["XGBoost"]
    joblib.dump(xgb_model, os.path.join(MODEL_DIR, "placement_xgboost.joblib"))
    with open(os.path.join(MODEL_DIR, "feature_order.json"), "w") as f:
        json.dump(FEATURE_ORDER, f)
    with open(os.path.join(MODEL_DIR, "model_metrics.json"), "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved XGBoost model -> {MODEL_DIR}/placement_xgboost.joblib")
    return results, xgb_model


if __name__ == "__main__":
    dataset = generate_synthetic_dataset()
    train_and_compare(dataset)