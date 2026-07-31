"""
Production GitHub Analyzer service.

Uses the real GitHub REST API (v3) to pull repositories, per-repo language
breakdown, commit counts, and README quality signals, then derives:
  - github_score            (overall profile strength)
  - project_quality_score   (average quality across analyzed repos)
  - skill_confidence        (per-language confidence, blending code volume
                              with how many separate repos use it)

Handles: invalid usernames (404), rate limiting (403/429), and empty
profiles gracefully, since a student's GitHub URL is user-supplied input.
"""

import re
import datetime
from typing import Dict, Any, List, Optional

import requests

from app.core.config import settings

GITHUB_API = "https://api.github.com"
MAX_REPOS_ANALYZED = 10  # caps API calls per analysis to stay within rate limits


def _headers() -> Dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = getattr(settings, "GITHUB_TOKEN", "") or ""
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _extract_username(github_url: str) -> str:
    if not github_url or not github_url.strip():
        raise ValueError("No GitHub URL provided. Add one in your profile first.")
    username = github_url.strip().rstrip("/").split("/")[-1]
    username = re.sub(r"[^a-zA-Z0-9\-]", "", username)
    if not username:
        raise ValueError("Could not extract a valid GitHub username from the provided URL.")
    return username


def _get(url: str, params: Optional[dict] = None) -> requests.Response:
    return requests.get(url, headers=_headers(), params=params, timeout=15)


def _commit_count(owner: str, repo: str) -> int:
    """GitHub's API has no direct 'total commits' field. The standard trick:
    request 1 commit per page and read the last page number from the
    pagination Link header — that number equals the total commit count."""
    resp = _get(f"{GITHUB_API}/repos/{owner}/{repo}/commits", params={"per_page": 1})
    if resp.status_code != 200:
        return 0
    link = resp.headers.get("Link", "")
    match = re.search(r'page=(\d+)>;\s*rel="last"', link)
    if match:
        return int(match.group(1))
    try:
        return len(resp.json())
    except Exception:
        return 0


def _readme_quality(owner: str, repo: str) -> str:
    resp = _get(f"{GITHUB_API}/repos/{owner}/{repo}/readme")
    if resp.status_code != 200:
        return "Missing"
    size = resp.json().get("size", 0)
    if size > 3000:
        return "High (Detailed documentation)"
    if size > 500:
        return "Medium (Basic documentation)"
    return "Low (Minimal or placeholder README)"


def fetch_github_profile(username: str, max_repos: int = MAX_REPOS_ANALYZED) -> Dict[str, Any]:
    user_resp = _get(f"{GITHUB_API}/users/{username}")
    if user_resp.status_code == 404:
        raise ValueError(f"GitHub user '{username}' not found.")
    if user_resp.status_code in (403, 429):
        raise PermissionError(
            "GitHub API rate limit exceeded. Add a GITHUB_TOKEN in your .env "
            "to raise the limit from 60 to 5000 requests/hour."
        )
    user_resp.raise_for_status()
    user_data = user_resp.json()

    repos_resp = _get(f"{GITHUB_API}/users/{username}/repos",
                       params={"sort": "updated", "per_page": 100, "type": "owner"})
    if repos_resp.status_code in (403, 429):
        raise PermissionError("GitHub API rate limit exceeded while fetching repositories.")
    repos_resp.raise_for_status()
    all_repos = [r for r in repos_resp.json() if not r.get("fork")]

    # Rank by stars then recency, analyze only the top N to control API usage
    all_repos.sort(key=lambda r: (r.get("stargazers_count", 0), r.get("updated_at", "")), reverse=True)
    top_repos = all_repos[:max_repos]

    repositories: List[Dict[str, Any]] = []
    language_bytes: Dict[str, int] = {}
    total_commits = 0

    for r in top_repos:
        owner_login = r["owner"]["login"]
        name = r["name"]

        lang_resp = _get(f"{GITHUB_API}/repos/{owner_login}/{name}/languages")
        langs = lang_resp.json() if lang_resp.status_code == 200 else {}
        for lang, byte_count in langs.items():
            language_bytes[lang] = language_bytes.get(lang, 0) + byte_count

        commits = _commit_count(owner_login, name)
        total_commits += commits

        repositories.append({
            "name": name,
            "description": r.get("description") or "No description provided",
            "languages": list(langs.keys()),
            "stars": r.get("stargazers_count", 0),
            "forks": r.get("forks_count", 0),
            "commits": commits,
            "readme_quality": _readme_quality(owner_login, name),
        })

    total_bytes = sum(language_bytes.values()) or 1
    languages_summary = {
        lang: f"{round(bytes_ / total_bytes * 100, 1)}%"
        for lang, bytes_ in sorted(language_bytes.items(), key=lambda x: -x[1])[:8]
    }

    return {
        "user_data": user_data,
        "repositories": repositories,
        "languages_summary": languages_summary,
        "total_commits": total_commits,
        "all_repo_count": len(all_repos),
    }


def compute_github_score(user_data: dict, repositories: List[dict], all_repo_count: int, total_commits: int) -> float:
    score = 0.0

    # Repo count & activity (25 pts)
    score += min(all_repo_count / 10, 1.0) * 15
    score += min(total_commits / 200, 1.0) * 10

    # Popularity signal across analyzed repos (20 pts)
    total_stars = sum(r["stars"] for r in repositories)
    total_forks = sum(r["forks"] for r in repositories)
    score += min(total_stars / 20, 1.0) * 12
    score += min(total_forks / 8, 1.0) * 8

    # README / documentation quality (20 pts)
    high_quality = sum(1 for r in repositories if r["readme_quality"].startswith("High"))
    score += min(high_quality / max(len(repositories), 1), 1.0) * 20

    # Language diversity (15 pts)
    all_langs = set()
    for r in repositories:
        all_langs.update(r["languages"])
    score += min(len(all_langs) / 6, 1.0) * 15

    # Profile completeness: bio, company/blog, has public repos (10 pts)
    completeness = sum([
        bool(user_data.get("bio")),
        bool(user_data.get("blog") or user_data.get("company")),
        user_data.get("public_repos", 0) > 0,
    ])
    score += (completeness / 3) * 10

    # Baseline activity bonus (10 pts)
    score += 10 if user_data.get("public_repos", 0) >= 3 else 5

    return round(min(score, 100.0), 1)


def compute_project_quality_score(repositories: List[dict]) -> float:
    if not repositories:
        return 0.0
    readme_points = {
        "High (Detailed documentation)": 35,
        "Medium (Basic documentation)": 20,
        "Low (Minimal or placeholder README)": 5,
        "Missing": 0,
    }
    scores = []
    for r in repositories:
        s = 0.0
        s += 30 if r["description"] and r["description"] != "No description provided" else 0
        s += readme_points.get(r["readme_quality"], 10)
        s += min(r["stars"] / 5, 1.0) * 20
        s += min(r["commits"] / 20, 1.0) * 15
        scores.append(s)
    return round(sum(scores) / len(scores), 1)


def compute_skill_confidence(languages_summary: Dict[str, str], repositories: List[dict]) -> Dict[str, float]:
    """Blends code footprint (% of total bytes) with repo spread (how many
    separate projects use it) — a language used once in one large repo is
    less convincing evidence of real skill than one used consistently
    across several smaller projects."""
    confidence = {}
    for lang, pct_str in languages_summary.items():
        pct = float(pct_str.rstrip("%"))
        repo_count = sum(1 for r in repositories if lang in r.get("languages", []))
        footprint_score = min(pct / 40, 1.0)
        spread_score = min(repo_count / max(len(repositories), 1), 1.0)
        confidence[lang] = round(0.6 * footprint_score + 0.4 * spread_score, 2)
    return confidence


def analyze_github(github_url: str, student_id: int) -> Dict[str, Any]:
    username = _extract_username(github_url)
    profile = fetch_github_profile(username)

    github_score = compute_github_score(
        profile["user_data"], profile["repositories"], profile["all_repo_count"], profile["total_commits"]
    )
    project_quality_score = compute_project_quality_score(profile["repositories"])
    skill_confidence = compute_skill_confidence(profile["languages_summary"], profile["repositories"])

    return {
        "student_id": student_id,
        "repositories": profile["repositories"],
        "languages_summary": profile["languages_summary"],
        "total_commits": profile["total_commits"],
        "github_score": github_score,
        "project_quality_score": project_quality_score,
        "skill_confidence": skill_confidence,
        "analyzed_at": datetime.datetime.utcnow().isoformat(),
    }


# ---------------------------------------------------------------------------
# Backward-compatible mock (dashboard.py still calls this for its own
# lightweight preview; safe to remove once every caller uses analyze_github).
# ---------------------------------------------------------------------------
def analyze_github_mock(github_url: str, student_id: int = 1) -> Dict[str, Any]:
    username = github_url.rstrip("/").split("/")[-1] if github_url else f"student{student_id}"
    total_commits = 340 + (student_id % 5) * 85
    github_score = round(78.0 + (student_id % 6) * 3.2, 1)
    if github_score > 98.0:
        github_score = 94.5
    project_quality_score = round(81.5 + (student_id % 4) * 4.0, 1)

    return {
        "student_id": student_id,
        "repositories": [
            {"name": "fullstack-placement-engine", "description": "AI-powered placement prediction dashboard",
             "languages": ["TypeScript", "Python"], "stars": 14, "forks": 4, "commits": 142,
             "readme_quality": "High (Detailed documentation)"},
        ],
        "languages_summary": {"Python": "42%", "TypeScript": "35%", "JavaScript": "13%", "HTML/CSS": "7%", "Docker": "3%"},
        "total_commits": total_commits,
        "github_score": github_score,
        "project_quality_score": project_quality_score,
        "skill_confidence": {"Python": 0.92, "FastAPI": 0.88, "React": 0.85, "TypeScript": 0.81, "Git": 0.95},
        "analyzed_at": datetime.datetime.utcnow().isoformat(),
    }