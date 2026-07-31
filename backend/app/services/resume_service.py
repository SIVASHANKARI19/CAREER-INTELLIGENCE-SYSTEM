"""
Production Resume Analyzer service.

Pipeline:
  1. PyMuPDF   -> extract raw text from the uploaded resume PDF
  2. Regex     -> segment the resume into sections (Education, Experience,
                  Projects, Certifications, Skills) using heading detection
  3. spaCy     -> PhraseMatcher for exact/case-insensitive skill matching
                  against a curated taxonomy, + NER (ORG/DATE) when the
                  trained pipeline is available, to pull companies/institutes
  4. Sentence Transformers -> semantic fallback matching: catches skill
                  mentions that don't exactly match the taxonomy string
                  (e.g. "Node JS" vs "Node.js", "React.js" vs "React") by
                  embedding noun-chunks and comparing cosine similarity
                  against taxonomy embeddings
  5. Rule-based ATS scoring + suggestion generation
"""

import os
import re
import datetime
from typing import Dict, Any, List, Tuple, Optional

import fitz  # PyMuPDF
import spacy
from spacy.matcher import PhraseMatcher

# ---------------------------------------------------------------------------
# Skill taxonomy — the canonical vocabulary the extractor recognizes.
# Grouped only for readability; matching is flat across all of them.
# ---------------------------------------------------------------------------
SKILL_TAXONOMY: List[str] = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C", "C#", "Go", "Rust",
    "Kotlin", "Swift", "PHP", "Ruby", "R", "Scala", "MATLAB", "SQL",
    # Web / Frontend
    "React", "Angular", "Vue.js", "Next.js", "Redux", "TailwindCSS", "Bootstrap",
    "HTML", "CSS", "jQuery",
    # Backend / Frameworks
    "FastAPI", "Django", "Flask", "Spring Boot", "Node.js", "Express.js",
    "ASP.NET", "GraphQL", "REST APIs",
    # Data / ML / AI
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "TensorFlow",
    "PyTorch", "Keras", "Scikit-Learn", "Pandas", "NumPy", "OpenCV", "XGBoost",
    "Sentence Transformers", "spaCy", "Hugging Face", "LangChain",
    # Databases
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "Firebase",
    "Cassandra", "DynamoDB",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "CI/CD",
    "Terraform", "Ansible", "Linux", "Nginx", "Git", "GitHub Actions",
    # Other CS fundamentals
    "Data Structures", "Algorithms", "System Design", "Microservices",
    "Agile", "Scrum", "Unit Testing", "OOP",
    # Data / Analytics / BI (career_goal isn't limited to SDE roles)
    "Tableau", "Power BI", "Excel", "Data Visualization", "Data Analysis",
    "Statistics", "A/B Testing", "ETL", "Apache Spark", "Airflow", "Hadoop",
    # Product / Design
    "Figma", "UI/UX Design", "Product Management", "Wireframing",
]

SECTION_HEADINGS = {
    "education": ["education", "academic background", "academics"],
    "experience": ["experience", "work experience", "professional experience", "internship", "internships"],
    "projects": ["projects", "academic projects", "personal projects"],
    "certifications": ["certifications", "certificates", "licenses & certifications"],
    "skills": ["skills", "technical skills", "core competencies"],
    "achievements": ["achievements", "awards", "honors"],
}

ACTION_VERBS = [
    "developed", "built", "designed", "implemented", "led", "engineered",
    "architected", "optimized", "automated", "deployed", "created", "improved",
    "reduced", "increased", "launched", "managed", "collaborated", "integrated",
]

# ---------------------------------------------------------------------------
# Lazy-loaded singletons — models load once per process, not per request.
# ---------------------------------------------------------------------------
_nlp = None
_skill_matcher = None
_embedder = None
_taxonomy_embeddings = None


def _get_nlp_and_matcher():
    global _nlp, _skill_matcher
    if _nlp is None:
        try:
            _nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Trained pipeline not downloaded yet in this environment.
            # Run: python -m spacy download en_core_web_sm
            # Falls back to a blank tokenizer-only pipeline; exact skill
            # matching still works, NER-based org/date extraction will not.
            _nlp = spacy.blank("en")
        _skill_matcher = PhraseMatcher(_nlp.vocab, attr="LOWER")
        patterns = [_nlp.make_doc(skill) for skill in SKILL_TAXONOMY]
        _skill_matcher.add("SKILLS", patterns)
    return _nlp, _skill_matcher


def _get_embedder():
    """Lazy-load sentence-transformers only when semantic fallback matching
    is actually needed, and fail soft if the package/model isn't available
    in the current environment (keeps exact-match skill extraction working
    even if this optional dependency isn't installed)."""
    global _embedder, _taxonomy_embeddings
    if _embedder is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedder = SentenceTransformer("all-MiniLM-L6-v2")
            _taxonomy_embeddings = _embedder.encode(SKILL_TAXONOMY, normalize_embeddings=True)
        except Exception:
            _embedder = False  # sentinel: tried and unavailable, don't retry every call
    return _embedder, _taxonomy_embeddings


def _cosine_sim(a, b) -> float:
    import numpy as np
    return float(np.dot(a, b))


# ---------------------------------------------------------------------------
# Step 1: PDF text extraction
# ---------------------------------------------------------------------------
def extract_text_from_pdf(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Resume file not found at {file_path}")
    doc = fitz.open(file_path)
    try:
        pages = [page.get_text("text") for page in doc]
    finally:
        doc.close()
    text = "\n".join(pages)
    # Normalize excessive whitespace while keeping line breaks (needed for
    # section/heading detection downstream).
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Step 2: Section segmentation
# ---------------------------------------------------------------------------
def segment_sections(text: str) -> Dict[str, str]:
    lines = text.split("\n")
    heading_positions: List[Tuple[int, str]] = []

    for idx, line in enumerate(lines):
        clean = line.strip().lower().strip(":")
        if not clean or len(clean) > 40:
            continue
        for section, keywords in SECTION_HEADINGS.items():
            if clean in keywords or any(clean == kw or clean.startswith(kw) for kw in keywords):
                heading_positions.append((idx, section))
                break

    sections: Dict[str, str] = {}
    for i, (line_idx, section) in enumerate(heading_positions):
        start = line_idx + 1
        end = heading_positions[i + 1][0] if i + 1 < len(heading_positions) else len(lines)
        sections[section] = "\n".join(lines[start:end]).strip()

    return sections


# ---------------------------------------------------------------------------
# Step 3 + 4: Skill extraction (exact match + semantic fallback)
# ---------------------------------------------------------------------------
def extract_skills(text: str) -> List[str]:
    nlp, matcher = _get_nlp_and_matcher()
    doc = nlp(text)

    found = set()
    for match_id, start, end in matcher(doc):
        found.add(doc[start:end].text)

    # Normalize to canonical taxonomy casing
    canonical = {s.lower(): s for s in SKILL_TAXONOMY}
    exact_matches = {canonical.get(f.lower(), f) for f in found}

    # Semantic fallback over noun chunks for skill-like phrases not caught
    # by exact matching (only runs if sentence-transformers is available).
    embedder, taxonomy_emb = _get_embedder()
    if embedder:
        candidates = list({chunk.text.strip() for chunk in doc.noun_chunks
                            if 1 <= len(chunk.text.split()) <= 4}) if hasattr(doc, "noun_chunks") else []
        if candidates:
            chunk_embeddings = embedder.encode(candidates, normalize_embeddings=True)
            for cand, emb in zip(candidates, chunk_embeddings):
                if cand.lower() in [e.lower() for e in exact_matches]:
                    continue
                best_idx = None
                best_score = 0.0
                for i, tax_emb in enumerate(taxonomy_emb):
                    score = _cosine_sim(emb, tax_emb)
                    if score > best_score:
                        best_score = score
                        best_idx = i
                if best_idx is not None and best_score >= 0.80:
                    exact_matches.add(SKILL_TAXONOMY[best_idx])

    return sorted(exact_matches)


# ---------------------------------------------------------------------------
# Step 3: Structured section extraction (regex-driven; NER-augmented when
# the trained spaCy pipeline is available)
# ---------------------------------------------------------------------------
DATE_RANGE_RE = re.compile(
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}|\d{4})"
    r"\s*(?:-|–|to)\s*"
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*\d{4}|\d{4}|present|current)",
    re.IGNORECASE,
)


def extract_experience(section_text: str) -> List[Dict[str, Any]]:
    if not section_text:
        return []
    nlp, _ = _get_nlp_and_matcher()
    lines = [l.strip() for l in section_text.split("\n") if l.strip()]

    date_line_indices = [i for i, l in enumerate(lines) if DATE_RANGE_RE.search(l)]
    if not date_line_indices:
        # No detectable date ranges in this section — safer to keep the
        # whole block as one entry than to fragment it line-by-line.
        combined = " ".join(lines)
        if not combined:
            return []
        return [{
            "company": None,
            "role": lines[0][:80] if lines else None,
            "duration": None,
            "description": combined[:800],
        }]

    entries = []
    prev_end = 0
    for i, date_idx in enumerate(date_line_indices):
        header_lines = lines[prev_end:date_idx]
        date_match = DATE_RANGE_RE.search(lines[date_idx])
        duration = f"{date_match.group(1)} - {date_match.group(2)}"
        next_date_idx = date_line_indices[i + 1] if i + 1 < len(date_line_indices) else len(lines)
        desc_lines = lines[date_idx + 1:next_date_idx]

        role = header_lines[0][:80] if header_lines else None
        company = header_lines[1][:80] if len(header_lines) > 1 else None
        if nlp.has_pipe("ner") and header_lines:
            doc = nlp(" ".join(header_lines)[:300])
            orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            if orgs:
                company = orgs[0]

        entries.append({
            "company": company,
            "role": role,
            "duration": duration,
            "description": " ".join(desc_lines)[:500],
        })
        prev_end = next_date_idx

    return entries[:10]


def extract_education(section_text: str) -> List[Dict[str, Any]]:
    if not section_text:
        return []
    entries = []
    blocks = [b.strip() for b in section_text.split("\n\n") if b.strip()]
    if not blocks:
        blocks = [b.strip() for b in section_text.split("\n") if b.strip()]
    for block in blocks[:5]:
        year_match = re.search(r"(19|20)\d{2}", block)
        entries.append({
            "degree": block.split("\n")[0][:120],
            "institution": block.split("\n")[1][:120] if "\n" in block else None,
            "graduation_year": int(year_match.group(0)) if year_match else None,
        })
    return entries


def _skill_mentioned(skill: str, text: str) -> bool:
    """Word-boundary match for alphanumeric-only skill names (prevents 'C' or
    'R' from matching inside words like 'Career' or 'Reduced'); falls back to
    substring match for skills containing punctuation (C++, C#, Node.js)
    where the punctuation itself already disambiguates."""
    skill_lower, text_lower = skill.lower(), text.lower()
    if re.fullmatch(r"[a-z0-9]+", skill_lower):
        return re.search(rf"\b{re.escape(skill_lower)}\b", text_lower) is not None
    return skill_lower in text_lower


def extract_projects(section_text: str) -> List[Dict[str, Any]]:
    if not section_text:
        return []
    # Most resumes separate project entries with a blank line — prefer that
    # signal; only fall back to the capital-letter heuristic (noisier) when
    # the section has no blank lines to split on.
    blocks = [b.strip() for b in re.split(r"\n\s*\n", section_text) if b.strip()]
    if len(blocks) <= 1:
        blocks = re.split(r"\n(?=[A-Z\u2022\-\*])", section_text)

    entries = []
    for block in blocks:
        block = block.strip().lstrip("•-* ").strip()
        if len(block) < 10:
            continue
        title = block.split("\n")[0][:100]
        tech_found = [s for s in SKILL_TAXONOMY if _skill_mentioned(s, block)]
        entries.append({
            "title": title,
            "description": block.replace("\n", " ")[:500],
            "tech_stack": tech_found[:8],
        })
    return entries[:10]


def extract_certifications(section_text: str) -> List[Dict[str, Any]]:
    if not section_text:
        return []
    entries = []
    lines = [l.strip().lstrip("•-* ").strip() for l in section_text.split("\n") if l.strip()]
    for line in lines[:10]:
        year_match = re.search(r"(19|20)\d{2}", line)
        parts = re.split(r"\s*[-–|]\s*", line, maxsplit=1)
        entries.append({
            "name": parts[0][:150],
            "issuer": parts[1][:100] if len(parts) > 1 else "Not specified",
            "date": year_match.group(0) if year_match else None,
        })
    return entries


# ---------------------------------------------------------------------------
# Step 5: ATS scoring + suggestions
# ---------------------------------------------------------------------------
def compute_ats_score(text: str, sections: Dict[str, str], skills: List[str]) -> Tuple[float, List[str]]:
    score = 0.0
    max_score = 100.0
    suggestions = []

    # 1. Contact info present (10 pts)
    has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
    has_phone = bool(re.search(r"(\+?\d[\d\s\-()]{8,}\d)", text))
    if has_email and has_phone:
        score += 10
    else:
        suggestions.append("Add a clearly visible email address and phone number near the top of your resume.")

    # 2. Core sections present (25 pts, ~5 each)
    required_sections = ["education", "experience", "projects", "skills"]
    present = sum(1 for s in required_sections if sections.get(s))
    score += (present / len(required_sections)) * 20
    if "certifications" in sections:
        score += 5
    missing_sections = [s for s in required_sections if not sections.get(s)]
    if missing_sections:
        suggestions.append(f"Add a clearly labeled section for: {', '.join(missing_sections)}.")

    # 3. Skill count / density (20 pts)
    skill_count = len(skills)
    score += min(skill_count / 12, 1.0) * 20
    if skill_count < 8:
        suggestions.append("List more relevant technical skills — aim for at least 8-12 keywords matching your target role.")

    # 4. Quantified achievements (15 pts) — numbers/percentages in bullet points
    quantified = len(re.findall(r"\b\d+%|\b\d+x\b|\breduced by \d+|\bimproved by \d+|\b\d+\s*(users|requests|records)", text, re.IGNORECASE))
    score += min(quantified / 3, 1.0) * 15
    if quantified < 2:
        suggestions.append("Quantify your project impact with metrics, e.g. 'reduced API latency by 35%' or 'served 10k+ users'.")

    # 5. Action verbs (15 pts)
    verb_count = sum(1 for v in ACTION_VERBS if re.search(rf"\b{v}\b", text, re.IGNORECASE))
    score += min(verb_count / 6, 1.0) * 15
    if verb_count < 4:
        suggestions.append("Start bullet points with strong action verbs (e.g. 'Built', 'Engineered', 'Optimized') instead of passive phrasing.")

    # 6. Resume length sanity (10 pts) — too short or too long both hurt ATS parsing/readability
    word_count = len(text.split())
    if 250 <= word_count <= 900:
        score += 10
    elif word_count < 250:
        suggestions.append("Your resume looks quite short — add more detail to your projects and experience sections.")
    else:
        suggestions.append("Your resume is on the longer side — consider trimming to the most relevant 1-2 pages.")

    # 7. Links present (5 pts) — GitHub/LinkedIn/portfolio
    has_link = bool(re.search(r"github\.com|linkedin\.com|https?://", text, re.IGNORECASE))
    if has_link:
        score += 5
    else:
        suggestions.append("Include a link to your GitHub or LinkedIn profile so recruiters and ATS systems can verify your work.")

    return round(min(score, max_score), 1), suggestions[:6]


# ---------------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------------
def analyze_resume(file_path: str, student_id: int) -> Dict[str, Any]:
    text = extract_text_from_pdf(file_path)
    sections = segment_sections(text)
    skills = extract_skills(text)

    experience = extract_experience(sections.get("experience", ""))
    education = extract_education(sections.get("education", ""))
    projects = extract_projects(sections.get("projects", ""))
    certifications = extract_certifications(sections.get("certifications", ""))

    ats_score, suggestions = compute_ats_score(text, sections, skills)

    return {
        "student_id": student_id,
        "raw_text": text,
        "extracted_skills": skills,
        "extracted_projects": projects,
        "extracted_certifications": certifications,
        "extracted_experience": experience,
        "extracted_education": education,
        "ats_score": ats_score,
        "suggestions": suggestions,
        "analyzed_at": datetime.datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock (kept so dashboard.py and other not-yet-migrated
# callers relying on synthetic data keep working; safe to remove once every
# caller has been switched to analyze_resume()).
# ---------------------------------------------------------------------------
def analyze_resume_mock(student_id: int) -> Dict[str, Any]:
    base_score = 72.5 + (student_id % 7) * 3.5
    if base_score > 96.0:
        base_score = 92.0
    return {
        "student_id": student_id,
        "raw_text": f"Curriculum Vitae for Student #{student_id}.",
        "extracted_skills": ["Python", "FastAPI", "React", "TypeScript", "SQLAlchemy", "Git", "REST APIs", "TailwindCSS"],
        "extracted_projects": [],
        "extracted_certifications": [],
        "extracted_experience": [],
        "extracted_education": [],
        "ats_score": round(base_score, 1),
        "suggestions": [],
        "analyzed_at": datetime.datetime.utcnow().isoformat(),
    }