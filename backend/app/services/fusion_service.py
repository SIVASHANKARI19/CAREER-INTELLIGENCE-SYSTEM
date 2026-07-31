"""
Production Resume + GitHub + LinkedIn Fusion service — the project's main
novelty module.

Cross-references skill evidence across all three sources to compute:
  - verified_skills:     resume-claimed skills confirmed by >=1 other source
  - hidden_skills:       skills evidenced in GitHub/LinkedIn but absent from
                          the resume (the student is underselling themselves)
  - unsupported_claims:  resume-claimed skills with no supporting evidence
                          anywhere else (the classic "AWS on resume, zero
                          AWS projects on GitHub" problem from the spec)
  - resume_credibility_score: rewards a high verification rate, penalizes
                          unsupported claims

This is a pure function (no DB access) so it can be unit tested directly;
the API layer is responsible for pulling the three source records and
persisting the result.
"""

import datetime
from typing import Dict, Any, List, Set

from app.services.resume_service import SKILL_TAXONOMY

# GitHub reports its own language names, which don't always match the
# taxonomy 1:1 (e.g. Dockerfile vs Docker). Map the common mismatches so
# fusion doesn't miss real evidence over a naming difference.
GITHUB_LANGUAGE_ALIASES = {
    "dockerfile": "Docker",
    "vue": "Vue.js",
    "tsx": "TypeScript",
    "jsx": "JavaScript",
    "shell": "Linux",
    "jupyter notebook": "Python",
}

_CANONICAL_LOOKUP = {s.lower(): s for s in SKILL_TAXONOMY}

# Minimum GitHub skill_confidence to count a language as real evidence
# rather than an incidental one-off file in a repo.
GITHUB_EVIDENCE_THRESHOLD = 0.30


def _canonicalize(skill: str) -> str:
    key = skill.strip().lower()
    if key in GITHUB_LANGUAGE_ALIASES:
        key = GITHUB_LANGUAGE_ALIASES[key].lower()
    return _CANONICAL_LOOKUP.get(key, skill.strip())


def _canonical_set(skills: List[str]) -> Set[str]:
    return {_canonicalize(s) for s in skills if s and s.strip()}


def run_fusion(
    resume_skills: List[str],
    resume_project_tech: List[str],
    github_languages: List[str],
    github_skill_confidence: Dict[str, float],
    linkedin_skills: List[str],
    student_id: int,
) -> Dict[str, Any]:

    resume_set = _canonical_set(resume_skills) | _canonical_set(resume_project_tech)

    github_evidence = _canonical_set([
        lang for lang in github_languages
    ]) | _canonical_set([
        skill for skill, conf in github_skill_confidence.items() if conf >= GITHUB_EVIDENCE_THRESHOLD
    ])

    linkedin_set = _canonical_set(linkedin_skills)

    other_sources = github_evidence | linkedin_set

    verified_skills = sorted(resume_set & other_sources)
    hidden_skills = sorted(other_sources - resume_set)
    unsupported_claims = sorted(resume_set - other_sources)

    total_claimed = len(resume_set)
    verification_rate = len(verified_skills) / total_claimed if total_claimed else 0.0

    # Credibility rewards verification rate, penalized per unsupported claim.
    # A resume with nothing to verify (empty skills) scores low, not zero,
    # since that's a completeness problem rather than a trust problem.
    if total_claimed == 0:
        credibility_score = 40.0
    else:
        base = 50 + 50 * verification_rate
        penalty = min(len(unsupported_claims) * 6, 40)
        credibility_score = round(max(min(base - penalty, 100.0), 0.0), 1)

    suggestions: List[str] = []
    for skill in hidden_skills[:5]:
        source = "GitHub" if skill in github_evidence else "LinkedIn"
        suggestions.append(
            f"Add '{skill}' to your resume — it's evidenced on your {source} but currently missing from your resume."
        )
    for skill in unsupported_claims[:5]:
        suggestions.append(
            f"'{skill}' is listed on your resume but isn't backed by a GitHub project or your LinkedIn profile — "
            f"add a supporting project, or remove it to keep your resume credible with ATS and recruiters."
        )
    if total_claimed == 0:
        suggestions.insert(0, "No skills were detected on your resume — list your technical skills explicitly so they can be verified against GitHub and LinkedIn.")
    if not suggestions:
        suggestions.append("Your resume is well-aligned with your GitHub and LinkedIn evidence — no major gaps detected.")

    return {
        "student_id": student_id,
        "verified_skills": verified_skills,
        "hidden_skills": hidden_skills,
        "unsupported_claims": unsupported_claims,
        "resume_credibility_score": credibility_score,
        "suggestions": suggestions[:6],
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock
# ---------------------------------------------------------------------------
def run_fusion_mock(student_id: int) -> Dict[str, Any]:
    credibility_score = round(84.0 + (student_id % 5) * 2.5, 1)
    return {
        "student_id": student_id,
        "verified_skills": ["Python", "FastAPI", "React", "TypeScript", "Git", "REST APIs"],
        "hidden_skills": ["Docker", "Redis", "AWS"],
        "unsupported_claims": ["Kubernetes", "GraphQL"],
        "resume_credibility_score": credibility_score,
        "suggestions": [
            "Add 'Docker' to your resume — it's evidenced on your GitHub but currently missing from your resume.",
            "'Kubernetes' is listed on your resume but isn't backed by a GitHub project — add a supporting project or remove it.",
        ],
        "generated_at": datetime.datetime.utcnow().isoformat(),
    }