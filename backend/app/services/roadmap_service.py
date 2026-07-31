"""
Production Learning Roadmap service (Module 11) — uses the Groq API.

IMPORTANT — TESTING DISCLOSURE:
This sandbox's network allowlist doesn't include api.groq.com, so the live
Groq call below could NOT be executed end-to-end in this environment. The
request/response shape follows Groq's OpenAI-compatible chat completions
API (verified via their docs), and the JSON-parsing + fallback logic IS
tested. Please test the live call yourself once GROQ_API_KEY is set in your
.env — if Groq changes their API shape before you deploy, only
_call_groq() needs updating; everything else (prompt construction,
parsing, persistence) is decoupled from the transport details.

Why Groq over Gemini for this module: Groq's API is OpenAI-compatible
(same request/response shape as the widely-documented Chat Completions
API), its free tier is generous for a student project's demo/viva usage,
and its LPU inference is fast enough that roadmap generation feels
near-instant in the UI rather than a multi-second wait.

Falls back to a rule-based mock roadmap (not a Groq call) if the API key
is missing or the call fails, so the demo/dashboard never breaks entirely
on an external API outage — but the fallback is clearly less personalized
and should not be presented as AI-generated in a demo.
"""

import os
import json
import datetime
import re
from typing import Dict, Any, List, Optional

import requests

from app.core.config import settings

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

ROADMAP_JSON_SCHEMA_HINT = """
Return ONLY valid JSON (no markdown fences, no commentary) with this exact structure:
{
  "weekly_plan": [{"week": 1, "focus": "string", "tasks": ["string", "string"]}],
  "monthly_plan": [{"month": 1, "goal": "string", "milestones": ["string", "string"]}],
  "recommended_projects": [{"title": "string", "description": "string", "skills_practiced": ["string"]}],
  "recommended_courses": [{"title": "string", "platform": "string", "skill": "string"}],
  "interview_questions": [{"question": "string", "topic": "string", "difficulty": "Easy|Medium|Hard"}],
  "resources": [{"title": "string", "type": "Article|Video|Documentation|Practice", "url": "string"}]
}
Provide 8 weekly_plan entries, 2 monthly_plan entries, 3-4 recommended_projects,
4-6 recommended_courses, 8-10 interview_questions, and 5-8 resources.
"""


def _build_prompt(target_role: str, missing_skills: List[str], priority_map: Dict[str, str],
                   verified_skills: List[str], cgpa: Optional[float]) -> str:
    priority_lines = "\n".join(f"- {s}: {priority_map.get(s, 'Medium')} priority" for s in missing_skills) or "- (none identified — focus on deepening existing skills)"
    verified_line = ", ".join(verified_skills) if verified_skills else "none detected yet"

    return f"""You are a career mentor for an engineering student targeting the role: {target_role}.

Student's already-verified skills: {verified_line}
CGPA: {cgpa if cgpa else 'not provided'}

Skill gaps to close, with priority:
{priority_lines}

Create a personalized, actionable learning roadmap that helps this specific student close
these exact skill gaps and become placement-ready for {target_role}, over an 8-week / 2-month plan.
Prioritize High-priority skills earlier in the plan. Be concrete and specific, not generic
advice — name real technologies, real project ideas, and real interview question topics
tied to the listed gaps.

{ROADMAP_JSON_SCHEMA_HINT}
"""


def _call_groq(prompt: str) -> Optional[dict]:
    api_key = getattr(settings, "GROQ_API_KEY", "") or os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a career mentor AI. Always respond with valid JSON only, no markdown fences, no commentary."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4096,
        "response_format": {"type": "json_object"},
    }
    try:
        resp = requests.post(
            GROQ_ENDPOINT,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        # Defensive: strip markdown fences in case the model wraps the JSON
        # despite response_format=json_object (seen occasionally on some models).
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
        return json.loads(text)
    except Exception as e:
        print(f"[roadmap_service] Groq call failed, falling back to rule-based roadmap: {e}")
        return None


def generate_roadmap(
    target_role: str,
    missing_skills: List[str],
    priority_map: Dict[str, str],
    verified_skills: List[str],
    cgpa: Optional[float],
    student_id: int,
) -> Dict[str, Any]:

    prompt = _build_prompt(target_role, missing_skills, priority_map, verified_skills, cgpa)
    groq_result = _call_groq(prompt)

    if groq_result:
        result = {
            "student_id": student_id,
            "weekly_plan": groq_result.get("weekly_plan", []),
            "monthly_plan": groq_result.get("monthly_plan", []),
            "recommended_projects": groq_result.get("recommended_projects", []),
            "recommended_courses": groq_result.get("recommended_courses", []),
            "interview_questions": groq_result.get("interview_questions", []),
            "resources": groq_result.get("resources", []),
            "generated_at": datetime.datetime.utcnow().isoformat(),
            "source": "groq",
        }
        return result

    return generate_roadmap_fallback(target_role, missing_skills, priority_map, student_id)


def generate_roadmap_fallback(target_role: str, missing_skills: List[str],
                               priority_map: Dict[str, str], student_id: int) -> Dict[str, Any]:
    """Rule-based roadmap used when GEMINI_API_KEY isn't set or the call
    fails. Deliberately simple and clearly non-AI-personalized — this keeps
    the dashboard functional, not a substitute for the real Groq output."""
    ordered_skills = sorted(missing_skills, key=lambda s: {"High": 0, "Medium": 1, "Low": 2}.get(priority_map.get(s, "Medium"), 1))[:8]
    weekly_plan = [
        {"week": i + 1, "focus": skill, "tasks": [f"Study core concepts of {skill}", f"Build a small practice exercise using {skill}"]}
        for i, skill in enumerate(ordered_skills[:8])
    ] or [{"week": 1, "focus": "General placement prep", "tasks": ["Review data structures & algorithms", "Polish resume and GitHub profile"]}]

    return {
        "student_id": student_id,
        "weekly_plan": weekly_plan,
        "monthly_plan": [
            {"month": 1, "goal": f"Close top skill gaps for {target_role}", "milestones": ordered_skills[:4] or ["Strengthen core fundamentals"]},
            {"month": 2, "goal": "Build portfolio projects and mock interview readiness", "milestones": ["Complete 1-2 portfolio projects", "Practice 20+ interview questions"]},
        ],
        "recommended_projects": [
            {"title": f"{skill} Mini Project", "description": f"A small project demonstrating practical {skill} usage.", "skills_practiced": [skill]}
            for skill in ordered_skills[:3]
        ],
        "recommended_courses": [
            {"title": f"{skill} Fundamentals", "platform": "Coursera / YouTube", "skill": skill}
            for skill in ordered_skills[:5]
        ],
        "interview_questions": [
            {"question": f"Explain a core concept in {skill} and how you've applied it.", "topic": skill, "difficulty": "Medium"}
            for skill in ordered_skills[:6]
        ],
        "resources": [
            {"title": f"Official {skill} Documentation", "type": "Documentation", "url": ""}
            for skill in ordered_skills[:5]
        ],
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "source": "rule_based_fallback",
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock (identical shape to generate_roadmap_fallback,
# kept as a separate name for dashboard/preview callers)
# ---------------------------------------------------------------------------
def generate_roadmap_mock(student_id: int) -> Dict[str, Any]:
    return generate_roadmap_fallback(
        target_role="Software Development Engineer",
        missing_skills=["Docker", "System Design", "AWS"],
        priority_map={"Docker": "High", "System Design": "High", "AWS": "Medium"},
        student_id=student_id,
    )