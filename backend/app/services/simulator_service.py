import datetime
from typing import List, Dict, Any

def simulate_career_impact_mock(student_id: int, applied_changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    baseline = 0.72

    # Boost logic per change type
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
    delta = round(simulated - baseline, 2)

    return {
        "id": 1,
        "student_id": student_id,
        "baseline_probability": baseline,
        "applied_changes": applied_changes,
        "simulated_probability": simulated,
        "delta": delta,
        "created_at": datetime.datetime.utcnow().isoformat()
    }
