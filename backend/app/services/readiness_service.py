"""
Production Career Readiness Dashboard service (Module 9).

Aggregates real outputs from Modules 4-8 into the 7 readiness dimensions the
spec requires. Two of these dimensions (communication_readiness and
interview_readiness) have NO dedicated data source anywhere in this
project's 14 modules — there's no video/speech assessment or mock-interview
module. Rather than fabricate a number with no defensible basis, these are
explicitly computed as coarse proxies from adjacent signals, documented
below. Be upfront about this in your report/viva — it's a legitimate,
common limitation, not something to hide.
"""

import datetime
from typing import Dict, Any, Optional


def compute_readiness(
    resume_ats_score: Optional[float],
    github_score: Optional[float],
    project_quality_score: Optional[float],
    resume_credibility_score: Optional[float],
    verified_skills_count: int,
    programming_languages_count: int,
    projects_count: int,
    achievements_count: int,
    linkedin_summary_length: int,
    student_id: int,
) -> Dict[str, Any]:

    # 1. Technical readiness — GitHub strength + breadth of verified/claimed skills
    technical_readiness = round(
        0.45 * (github_score or 0)
        + 0.30 * min(verified_skills_count / 10, 1.0) * 100
        + 0.25 * min(programming_languages_count / 6, 1.0) * 100,
        1
    )

    # 2. Communication readiness — PROXY ONLY. No direct measurement exists
    # in this system (no interview transcript / speech data). Approximated
    # from LinkedIn summary quality (a written self-presentation signal) and
    # achievements count (a proxy for leadership/extracurricular communication).
    communication_readiness = round(
        50
        + min(linkedin_summary_length / 400, 1.0) * 25
        + min(achievements_count / 4, 1.0) * 25,
        1
    )

    # 3. Resume readiness — direct reuse of Module 4's ATS score
    resume_readiness = round(resume_ats_score or 0, 1)

    # 4. Project readiness — GitHub project quality + breadth of listed projects
    project_readiness = round(
        0.55 * (project_quality_score or 0)
        + 0.45 * min(projects_count / 4, 1.0) * 100,
        1
    )

    # 5. GitHub readiness — direct reuse of Module 5's github_score
    github_readiness = round(github_score or 0, 1)

    # 6. Interview readiness — PROXY ONLY, same caveat as communication above.
    # Derived from technical strength, the communication proxy, and resume
    # credibility (a candidate whose resume claims hold up under scrutiny is
    # more likely to hold up under interview questioning about it).
    interview_readiness = round(
        0.50 * technical_readiness
        + 0.30 * communication_readiness
        + 0.20 * (resume_credibility_score or 0),
        1
    )

    overall_readiness = round(
        technical_readiness * 0.25
        + communication_readiness * 0.15
        + resume_readiness * 0.15
        + project_readiness * 0.20
        + github_readiness * 0.15
        + interview_readiness * 0.10,
        1
    )

    return {
        "student_id": student_id,
        "technical_readiness": technical_readiness,
        "communication_readiness": communication_readiness,
        "resume_readiness": resume_readiness,
        "project_readiness": project_readiness,
        "github_readiness": github_readiness,
        "interview_readiness": interview_readiness,
        "overall_readiness": overall_readiness,
        "computed_at": datetime.datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock
# ---------------------------------------------------------------------------
def get_readiness_scores_mock(student_id: int) -> Dict[str, Any]:
    tech = round(85.0 + (student_id % 3) * 2.5, 1)
    comm = round(78.0 + (student_id % 4) * 3.0, 1)
    resume = round(82.0 + (student_id % 5) * 2.0, 1)
    proj = round(88.0 + (student_id % 2) * 4.0, 1)
    gh = round(80.0 + (student_id % 4) * 3.5, 1)
    interview = round(74.0 + (student_id % 5) * 4.0, 1)
    overall = round((tech * 0.25 + comm * 0.15 + resume * 0.15 + proj * 0.20 + gh * 0.15 + interview * 0.10), 1)
    return {
        "student_id": student_id, "technical_readiness": tech, "communication_readiness": comm,
        "resume_readiness": resume, "project_readiness": proj, "github_readiness": gh,
        "interview_readiness": interview, "overall_readiness": overall,
        "computed_at": datetime.datetime.utcnow().isoformat(),
    }