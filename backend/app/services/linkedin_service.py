"""
Production LinkedIn PDF Analyzer service.

LinkedIn's "Save to PDF" export has a fairly predictable structure: Name on
the first line, Headline directly beneath it, then a fixed sequence of
section headings (Summary/About, Experience, Education, Licenses &
Certifications, Skills). This service segments on those specific headings
and reuses the PDF-extraction and skill-matching machinery already built
and tested in Module 4 (resume_service.py) rather than duplicating it.
"""

import re
import datetime
from typing import Dict, Any, List

from app.services.resume_service import extract_text_from_pdf, extract_skills, DATE_RANGE_RE

LINKEDIN_SECTION_HEADINGS = {
    "summary": ["summary", "about"],
    "experience": ["experience"],
    "education": ["education"],
    "certifications": ["licenses & certifications", "licenses and certifications", "certifications"],
    "skills": ["skills", "top skills"],
}


def segment_linkedin_sections(text: str) -> Dict[str, str]:
    lines = text.split("\n")
    heading_positions = []
    for idx, line in enumerate(lines):
        clean = line.strip().lower().strip(":")
        if not clean or len(clean) > 40:
            continue
        for section, keywords in LINKEDIN_SECTION_HEADINGS.items():
            if clean in keywords:
                heading_positions.append((idx, section))
                break

    sections: Dict[str, str] = {}
    for i, (line_idx, section) in enumerate(heading_positions):
        start = line_idx + 1
        end = heading_positions[i + 1][0] if i + 1 < len(heading_positions) else len(lines)
        sections[section] = "\n".join(lines[start:end]).strip()

    return sections, heading_positions


def extract_headline(text: str, heading_positions) -> str:
    """LinkedIn PDFs put the person's full name on the first non-empty line
    and their headline directly beneath it, before any section heading."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    first_heading_line = min((pos for pos, _ in heading_positions), default=len(lines))
    preamble = [l for i, l in enumerate(text.split("\n")) if l.strip()][:6]
    # name = preamble[0]; headline is typically the next substantive line
    for line in preamble[1:]:
        if len(line) > 5 and not line.lower().startswith(("contact", "www.", "http", "linkedin.com/in")):
            return line[:255]
    return ""


def _date_anchored_entries(section_text: str, header_field_names: List[str]) -> List[Dict[str, Any]]:
    """Shared pattern used by both Experience and Education: LinkedIn lists
    a short header block (title/company or institution/degree) immediately
    followed by a date range line, then optional description lines. Anchor
    on the date line the same way Module 4's resume parser does — that
    approach was validated against a real extraction test in Module 4."""
    if not section_text:
        return []
    lines = [l.strip() for l in section_text.split("\n") if l.strip()]
    date_line_indices = [i for i, l in enumerate(lines) if DATE_RANGE_RE.search(l)]

    if not date_line_indices:
        return []

    entries = []
    prev_end = 0
    for i, date_idx in enumerate(date_line_indices):
        header_lines = lines[prev_end:date_idx]
        date_match = DATE_RANGE_RE.search(lines[date_idx])
        duration = f"{date_match.group(1)} - {date_match.group(2)}"
        next_date_idx = date_line_indices[i + 1] if i + 1 < len(date_line_indices) else len(lines)
        desc_lines = lines[date_idx + 1:next_date_idx]

        entry = {header_field_names[j]: (header_lines[j][:150] if j < len(header_lines) else None)
                 for j in range(len(header_field_names))}
        entry["duration"] = duration
        entry["description"] = " ".join(desc_lines)[:500] if desc_lines else None
        entries.append(entry)
        prev_end = next_date_idx

    return entries[:10]


def extract_experience(section_text: str) -> List[Dict[str, Any]]:
    entries = _date_anchored_entries(section_text, ["title", "company"])
    for e in entries:
        e.setdefault("location", None)
    return entries


def extract_education(section_text: str) -> List[Dict[str, Any]]:
    entries = _date_anchored_entries(section_text, ["institution", "degree"])
    # LinkedIn calls the date range "period" for education rather than "duration"
    for e in entries:
        e["period"] = e.pop("duration", None)
        e.pop("description", None)
    return entries


def extract_certificates(section_text: str) -> List[Dict[str, Any]]:
    if not section_text:
        return []
    lines = [l.strip() for l in section_text.split("\n") if l.strip()]
    entries = []
    i = 0
    while i < len(lines):
        name = lines[i]
        issuer = lines[i + 1] if i + 1 < len(lines) else None
        issue_date = None
        date_match = re.search(r"(issued\s+)?((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4})",
                                lines[i + 2] if i + 2 < len(lines) else "", re.IGNORECASE)
        if date_match:
            issue_date = date_match.group(2)
            i += 3
        elif issuer:
            i += 2
        else:
            i += 1
        entries.append({"name": name[:150], "issued_by": issuer, "issue_date": issue_date})
    return entries[:10]


def analyze_linkedin(file_path: str, student_id: int) -> Dict[str, Any]:
    text = extract_text_from_pdf(file_path)
    sections, heading_positions = segment_linkedin_sections(text)

    headline = extract_headline(text, heading_positions)
    summary = sections.get("summary", "").strip() or None
    skills_from_section = extract_skills(sections.get("skills", "")) if sections.get("skills") else []
    skills_from_summary = extract_skills(summary) if summary else []
    extracted_skills = sorted(set(skills_from_section) | set(skills_from_summary))

    experience = extract_experience(sections.get("experience", ""))
    education = extract_education(sections.get("education", ""))
    certificates = extract_certificates(sections.get("certifications", ""))

    return {
        "student_id": student_id,
        "headline": headline,
        "summary": summary,
        "extracted_skills": extracted_skills,
        "extracted_experience": experience,
        "extracted_education": education,
        "extracted_certificates": certificates,
        "analyzed_at": datetime.datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock
# ---------------------------------------------------------------------------
def analyze_linkedin_mock(student_id: int) -> Dict[str, Any]:
    return {
        "student_id": student_id,
        "headline": "Aspiring Full Stack Engineer | CS Senior | Open to SDE Roles",
        "summary": "Passionate software engineer skilled in building scalable web apps.",
        "extracted_skills": ["Python", "React.js", "RESTful APIs", "Database Design"],
        "extracted_experience": [{"title": "Software Engineering Intern", "company": "TechNova Solutions",
                                   "duration": "May 2024 - Aug 2024", "description": "Built REST APIs."}],
        "extracted_education": [{"institution": "National Institute of Technology",
                                  "degree": "B.Tech Computer Science", "period": "2021 - 2025"}],
        "extracted_certificates": [{"name": "AWS Certified Cloud Practitioner",
                                     "issued_by": "Amazon Web Services", "issue_date": "May 2024"}],
        "analyzed_at": datetime.datetime.utcnow().isoformat(),
    }