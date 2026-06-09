"""
Role-level intelligence for Trovly job matches.

These functions are intentionally deterministic and provider-free so the
current product can show premium-grade insights before the OpenAI/embeddings
pipeline is migrated to background jobs.
"""

import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import quote_plus

from tailor import _extract_keywords

UTC = timezone.utc  # noqa: UP017 - local project venv is Python 3.10

TECH_SKILLS = [
    "python",
    "javascript",
    "typescript",
    "java",
    "go",
    "rust",
    "react",
    "node.js",
    "fastapi",
    "django",
    "aws",
    "gcp",
    "azure",
    "docker",
    "kubernetes",
    "terraform",
    "ansible",
    "ci/cd",
    "github actions",
    "jenkins",
    "postgresql",
    "redis",
    "mongodb",
    "linux",
    "nginx",
    "cloudflare",
    "rest",
    "graphql",
    "microservices",
    "serverless",
    "machine learning",
    "llm",
    "nlp",
    "security",
    "siem",
    "splunk",
    "iam",
    "soc",
    "devsecops",
    "datadog",
    "prometheus",
    "grafana",
    "snowflake",
    "databricks",
]

ROLE_SKILL_MAP = {
    "cloud": {"aws", "gcp", "azure", "terraform", "kubernetes", "iam", "linux"},
    "devops": {"ci/cd", "docker", "kubernetes", "terraform", "github actions", "jenkins"},
    "platform": {"kubernetes", "terraform", "api", "ci/cd", "docker", "linux"},
    "reliability": {"datadog", "prometheus", "grafana", "linux", "kubernetes"},
    "security": {"security", "siem", "splunk", "iam", "soc", "devsecops"},
    "ai": {"python", "machine learning", "llm", "nlp", "api"},
}

REMOTE_TERMS = {"remote", "distributed", "work from home", "anywhere"}
SENIOR_TERMS = {"senior", "staff", "principal", "lead", "sr."}

RESPONSIVE_SOURCE_SIGNALS = {
    "lennys_jobs": (18, "Sourced from Lenny's Jobs/TrueUp, a curated tech hiring surface."),
    "ashby": (14, "Direct Ashby posting; usually closer to the hiring team than aggregators."),
    "lever": (14, "Direct Lever posting; usually closer to the hiring team than aggregators."),
    "greenhouse": (12, "Direct Greenhouse posting; usually closer to the hiring team than aggregators."),
    "himalayas_api": (10, "Remote-native source with structured job data."),
    "working_nomads": (8, "Remote-focused board with active postings."),
    "remotive": (6, "Remote-focused board."),
    "jobicy": (6, "Remote-focused board."),
    "the_muse": (4, "Curated job source."),
    "arbeitnow": (4, "Fresh job-board source."),
    "rss": (3, "RSS source; useful, but recruiter signal is limited."),
    "rss_feeds": (3, "RSS source; useful, but recruiter signal is limited."),
    "adzuna": (2, "Aggregator source; verify freshness before heavy outreach."),
}

FAST_ATS_TERMS = {
    "greenhouse.io",
    "job-boards.greenhouse.io",
    "boards.greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "jobs.ashbyhq.com",
    "smartrecruiters.com",
}
SLOW_ATS_TERMS = {"workdayjobs.com", "myworkdayjobs.com", "taleo.net", "icims.com"}

RESPONSIVE_STATUSES = {"Phone Screen", "Interview", "Take Home", "Final Round", "Offer"}
ANSWERED_STATUSES = RESPONSIVE_STATUSES | {"Rejected"}
LOW_RESPONSE_STATUSES = {"Ghosted"}


def _clean(text):
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _job_value(job, key, default=""):
    if isinstance(job, dict):
        return job.get(key, default)
    return getattr(job, key, default)


def _job_text(job):
    parts = [
        _job_value(job, "title"),
        _job_value(job, "company"),
        _job_value(job, "location"),
        _job_value(job, "salary"),
        _job_value(job, "description"),
    ]
    return _clean(" ".join(str(p or "") for p in parts))


def _normalize_company(company):
    return re.sub(r"[^a-z0-9]+", "", (company or "").lower())


def _parse_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, int | float):
        timestamp = float(value)
        while timestamp > 10_000_000_000:
            timestamp /= 1000
        try:
            return datetime.fromtimestamp(timestamp, tz=UTC)
        except (OSError, OverflowError, ValueError):
            return None

    text = str(value).strip()
    if not text:
        return None
    if text.isdigit():
        return _parse_datetime(float(text))
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _job_age_days(job):
    posted = (
        _parse_datetime(_job_value(job, "posted_date"))
        or _parse_datetime(_job_value(job, "updated_at"))
        or _parse_datetime(_job_value(job, "found_at"))
    )
    if not posted:
        return None
    return max(0, (datetime.now(UTC) - posted.astimezone(UTC)).days)


def extract_salary_numbers(salary_text):
    """Return annualized salary numbers parsed from a salary string."""
    if not salary_text:
        return []
    text = salary_text.lower().replace(",", "")
    numbers = []
    for raw in re.findall(r"\$?\s*(\d+(?:\.\d+)?)\s*(k)?", text):
        value = float(raw[0])
        if raw[1] == "k":
            value *= 1000
        if value < 500:
            value *= 2080
        if value >= 30000:
            numbers.append(int(value))
    return numbers


def salary_competitiveness(salary_text, target_salary=150000):
    numbers = extract_salary_numbers(salary_text)
    if not numbers:
        return {
            "label": "Unknown",
            "detail": "No public salary range detected.",
            "max_salary": None,
            "target_salary": target_salary,
        }

    max_salary = max(numbers)
    min_salary = min(numbers)
    if max_salary >= target_salary * 1.12:
        label = "Strong"
        detail = "Posted range clears your target with room to negotiate."
    elif max_salary >= target_salary:
        label = "Aligned"
        detail = "Posted range reaches your salary target."
    elif max_salary >= target_salary * 0.9:
        label = "Close"
        detail = "Range is close, but the top end may require negotiation."
    else:
        label = "Below target"
        detail = "Posted range appears below your stated target."

    return {
        "label": label,
        "detail": detail,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "target_salary": target_salary,
    }


def infer_role_family(job):
    text = _job_text(job).lower()
    families = []
    for family in ROLE_SKILL_MAP:
        if family in text:
            families.append(family.title())
    if "sre" in text or "site reliability" in text:
        families.append("Reliability")
    if "devsecops" in text:
        families.append("Security")
    return sorted(set(families)) or ["Technical"]


def resume_strength_score(resume_text):
    """Estimate resume strength for premium dashboard gamification."""
    clean = _clean(resume_text)
    if not clean:
        return {
            "score": 0,
            "level": "Not started",
            "signals": [],
            "next_actions": ["Upload or paste your resume."],
        }

    lower = clean.lower()
    skills = sorted({skill for skill in TECH_SKILLS if skill in lower})
    numbers = re.findall(r"\b\d+[%+]?", clean)
    outcomes = [
        token
        for token in ["reduced", "increased", "saved", "launched", "built", "designed", "automated"]
        if token in lower
    ]

    score = 35
    score += min(len(skills), 16) * 2
    score += min(len(numbers), 12) * 2
    score += min(len(outcomes), 8) * 2
    if "aws" in lower or "azure" in lower or "gcp" in lower:
        score += 5
    if "terraform" in lower or "kubernetes" in lower:
        score += 5
    if len(clean) > 2500:
        score += 5
    score = max(0, min(score, 100))

    if score >= 85:
        level = "Offer-ready"
    elif score >= 70:
        level = "Interview-ready"
    elif score >= 55:
        level = "Needs targeting"
    else:
        level = "Needs rebuild"

    next_actions = []
    if len(skills) < 8:
        next_actions.append("Add more concrete cloud, DevOps, AI, or security skills.")
    if len(numbers) < 5:
        next_actions.append(
            "Add measurable outcomes: dollars saved, uptime, latency, releases, or hours reduced."
        )
    if "terraform" not in lower and "kubernetes" not in lower:
        next_actions.append(
            "Add infrastructure depth where accurate: Terraform, Kubernetes, CI/CD, or cloud services."
        )
    if not next_actions:
        next_actions.append("Use job-specific tailoring before every high-fit application.")

    return {
        "score": score,
        "level": level,
        "signals": skills[:12],
        "next_actions": next_actions,
    }


def build_match_intelligence(job, score, resume_text="", target_salary=150000):
    """
    Create explainable premium signals for a matched job.

    Returns data for:
    - match percent
    - missing skills
    - why it fits
    - why it may not
    - probability of interview
    - salary competitiveness
    """
    job_text = _job_text(job)
    lower_job = job_text.lower()
    lower_resume = (resume_text or "").lower()

    jd_keywords = _extract_keywords(job_text)
    resume_keywords = _extract_keywords(resume_text or "")
    matched_skills = sorted(jd_keywords & resume_keywords)
    missing_skills = sorted(jd_keywords - resume_keywords)

    role_families = infer_role_family(job)
    role_skills = set()
    for family in role_families:
        role_skills |= ROLE_SKILL_MAP.get(family.lower(), set())
    inferred_missing = sorted(skill for skill in role_skills if skill not in lower_resume)
    missing = sorted(set(missing_skills + inferred_missing))[:8]

    why_fit = []
    if matched_skills:
        why_fit.append("Your resume overlaps with {}".format(", ".join(matched_skills[:5])))
    if any(term in lower_job for term in REMOTE_TERMS):
        why_fit.append("The role appears remote or distributed.")
    if score >= 0.75:
        why_fit.append("Semantic match is strong enough to justify a tailored application.")
    elif score >= 0.6:
        why_fit.append("Semantic match is promising, especially with targeted resume edits.")
    if any(term in lower_job for term in SENIOR_TERMS):
        why_fit.append("Seniority language aligns with mid-to-senior positioning.")

    if not why_fit:
        why_fit.append("The role has enough overlap to evaluate, but needs a closer resume pass.")

    why_not = []
    if missing:
        why_not.append("Missing or under-emphasized skills: {}".format(", ".join(missing[:5])))
    if "onsite" in lower_job or "on-site" in lower_job:
        why_not.append("Location language may conflict with a remote-first search.")
    if score < 0.58:
        why_not.append("Current resume language may not mirror the role closely enough.")
    if not why_not:
        why_not.append("No major fit risks detected from available posting text.")

    salary = salary_competitiveness(_job_value(job, "salary"), target_salary)
    keyword_coverage = len(matched_skills) / max(len(jd_keywords), 1)
    interview_probability = int(
        min(
            92,
            max(
                18,
                (score * 68)
                + (keyword_coverage * 18)
                + (8 if salary["label"] in {"Strong", "Aligned"} else 0)
                + (4 if any(term in lower_job for term in REMOTE_TERMS) else 0),
            ),
        )
    )

    readiness = resume_strength_score(resume_text)
    readiness_score = int((readiness["score"] * 0.45) + (score * 55))

    return {
        "match_percent": int(round(score * 100)),
        "role_family": role_families,
        "matched_skills": matched_skills[:10],
        "missing_skills": missing,
        "why_fit": why_fit,
        "why_not": why_not,
        "interview_probability": interview_probability,
        "salary_competitiveness": salary,
        "readiness_score": max(0, min(readiness_score, 100)),
        "urgency": urgency_message(job, score, salary),
    }


def _outcome_signal(company, applications):
    normalized = _normalize_company(company)
    if not normalized:
        return 0, [], []

    related = [
        app for app in applications or []
        if _normalize_company(app.get("company", "")) == normalized
    ]
    if not related:
        return 0, [], []

    statuses = {app.get("status") for app in related}
    score = 0
    reasons = []
    risks = []

    if statuses & RESPONSIVE_STATUSES:
        score += 24
        reasons.append("Your tracker shows this company has converted to interview-stage activity.")
    elif statuses & ANSWERED_STATUSES:
        score += 10
        reasons.append("Your tracker shows this company has responded before, even if it was a no.")

    if statuses & LOW_RESPONSE_STATUSES:
        score -= 24
        risks.append("Your tracker has at least one ghosted application at this company.")

    active_count = sum(1 for app in related if app.get("status") in {"Applied", "Phone Screen", "Interview", "Take Home", "Final Round"})
    if active_count:
        reasons.append(f"{active_count} active tracked application(s) can be followed up or mined for contacts.")

    return score, reasons, risks


def recruiter_target_roles(job):
    """Return recruiter/hiring-manager personas worth searching for."""
    title = _job_value(job, "title", "").lower()
    families = {family.lower() for family in infer_role_family(job)}

    if "product" in title:
        return ["Product recruiter", "Product talent partner", "Group product manager"]
    if "design" in title:
        return ["Design recruiter", "Product design manager", "Head of design"]
    if families & {"cloud", "devops", "platform", "reliability"}:
        return [
            "Technical recruiter",
            "Infrastructure engineering manager",
            "Platform or SRE lead",
        ]
    if "security" in families:
        return ["Security recruiter", "Security engineering manager", "SOC or detection lead"]
    if "ai" in families or "machine learning" in title or "ml" in title:
        return ["AI/ML recruiter", "AI platform engineering manager", "Head of AI"]
    return ["Technical recruiter", "Talent partner", "Hiring manager"]


def recruiter_search_links(job):
    """Build search URLs for finding likely outreach targets."""
    company = _job_value(job, "company", "")
    title = _job_value(job, "title", "")
    company_q = quote_plus(f'"{company}"')
    title_q = quote_plus(title)
    linkedin_keywords = quote_plus(f'{company} recruiter talent acquisition {title}')
    google_query = quote_plus(
        f'site:linkedin.com/in "{company}" (recruiter OR "talent acquisition" OR "technical recruiter") "{title}"'
    )
    x_query = quote_plus(f'"{company}" (hiring OR recruiter OR "talent acquisition") "{title}"')

    return [
        {
            "label": "LinkedIn recruiter search",
            "url": f"https://www.linkedin.com/search/results/people/?keywords={linkedin_keywords}",
        },
        {
            "label": "Google people search",
            "url": f"https://www.google.com/search?q={google_query}",
        },
        {
            "label": "X hiring search",
            "url": f"https://x.com/search?q={x_query}&src=typed_query",
        },
        {
            "label": "Company hiring mentions",
            "url": f"https://www.google.com/search?q={company_q}+hiring+recruiter+{title_q}",
        },
    ]


def recruiter_outreach_note(job, responsiveness=None):
    company = _job_value(job, "company", "your team")
    title = _job_value(job, "title", "the role")
    targets = recruiter_target_roles(job)
    reason = ""
    if responsiveness and responsiveness.get("reasons"):
        reason = f" I noticed {responsiveness['reasons'][0].lower()}"

    return (
        f"Hi - I saw the {title} opening at {company}.{reason} "
        "I am targeting roles where my background maps tightly to the team needs, "
        "and this one looks worth a focused conversation. "
        f"Are you the right person for this search, or should I reach out to the {targets[0].lower()}?"
    )


def build_responsiveness_intelligence(job, match_score=0, applications=None, peer_jobs=None):
    """
    Estimate whether a company/job is worth recruiter outreach.

    This is a signal model, not a promise. It favors fresh direct postings,
    curated/community sources, transparent hiring metadata, and proven
    response history from the user's own tracker.
    """
    source = str(_job_value(job, "source", "") or "").lower()
    url = str(_job_value(job, "url", "") or "").lower()
    text = _job_text(job).lower()
    company = _job_value(job, "company", "Unknown")

    score = 42
    reasons = []
    risks = []

    source_bonus, source_reason = RESPONSIVE_SOURCE_SIGNALS.get(source, (0, ""))
    if source_bonus:
        score += source_bonus
        reasons.append(source_reason)

    age_days = _job_age_days(job)
    if age_days is None:
        risks.append("Posting age is unknown, so freshness is hard to verify.")
    elif age_days <= 3:
        score += 18
        reasons.append("Posted or refreshed in the last 3 days.")
    elif age_days <= 7:
        score += 13
        reasons.append("Posted or refreshed in the last week.")
    elif age_days <= 14:
        score += 7
        reasons.append("Posting is still relatively fresh.")
    elif age_days >= 45:
        score -= 18
        risks.append("Posting is older than 45 days and may be stale.")
    elif age_days >= 30:
        score -= 10
        risks.append("Posting is older than 30 days; verify it is still active.")

    if "posted by lenny community" in text:
        score += 16
        reasons.append("Posted by Lenny Community, which is a warmer sourcing signal.")
    if "lenny 100" in text:
        score += 8
        reasons.append("Company appears in the Lenny 100 signal set.")
    if "last raised" in text or "early-stage startup" in text or "unicorn" in text:
        score += 8
        reasons.append("Company metadata suggests active growth or venture-backed hiring.")
    if "layoff" in text:
        score -= 8
        risks.append("Company metadata mentions a recent layoff.")

    open_roles_match = re.search(r"(?:company open roles|open jobs):\s*(\d+)", text)
    if open_roles_match:
        open_roles = int(open_roles_match.group(1))
        if open_roles >= 20:
            score += 12
            reasons.append(f"{open_roles} open roles suggests active hiring motion.")
        elif open_roles >= 5:
            score += 8
            reasons.append(f"{open_roles} open roles suggests the company is actively hiring.")
        elif open_roles >= 2:
            score += 4
            reasons.append(f"{open_roles} open roles gives a light active-hiring signal.")

    if _job_value(job, "salary"):
        score += 7
        reasons.append("Salary is listed, which often means a more concrete requisition.")

    if any(term in url for term in FAST_ATS_TERMS):
        score += 7
        reasons.append("Apply URL points to a direct ATS or company-hosted posting.")
    if any(term in url for term in SLOW_ATS_TERMS):
        score -= 7
        risks.append("Apply flow appears to use a slower enterprise ATS.")
    if "time-consuming ats" in text:
        score -= 5
        risks.append("Source metadata warns the ATS may be time-consuming.")

    if match_score >= 0.78:
        score += 7
        reasons.append("Your match score is high enough to justify direct outreach.")
    elif match_score and match_score < 0.55:
        score -= 5
        risks.append("Fit is below target; responsiveness may not matter if the match is weak.")

    outcome_bonus, outcome_reasons, outcome_risks = _outcome_signal(company, applications)
    score += outcome_bonus
    reasons.extend(outcome_reasons)
    risks.extend(outcome_risks)

    peer_count = sum(
        1 for peer in peer_jobs or []
        if _normalize_company(_job_value(peer[0] if isinstance(peer, tuple) else peer, "company")) == _normalize_company(company)
    )
    if peer_count >= 3:
        score += 6
        reasons.append(f"{peer_count} matching roles from this company appeared in your target pool.")

    score = max(0, min(100, int(round(score))))
    if score >= 80:
        label = "High response target"
        action = "Apply and contact a recruiter or hiring manager today."
    elif score >= 65:
        label = "Promising target"
        action = "Apply, then send a focused recruiter note within 24 hours."
    elif score >= 50:
        label = "Mixed signal"
        action = "Apply only if fit is strong; keep outreach lightweight."
    else:
        label = "Low-signal target"
        action = "Do not overinvest unless the role is unusually strong."

    result = {
        "score": score,
        "label": label,
        "action": action,
        "reasons": reasons[:6] or ["No strong responsiveness signals detected yet."],
        "risks": risks[:4],
        "recruiter_targets": recruiter_target_roles(job),
        "search_links": recruiter_search_links(job),
    }
    result["outreach_note"] = recruiter_outreach_note(job, result)
    return result


def rank_responsive_targets(job_entries, applications=None, limit=10):
    """Aggregate job-level responsiveness into company targets."""
    companies = {}
    entries = list(job_entries or [])

    for entry in entries:
        job, match_score = entry if isinstance(entry, tuple) else (entry, _job_value(entry, "match_score", 0))
        company = _job_value(job, "company", "Unknown")
        if not company or company == "Unknown":
            continue
        intel = build_responsiveness_intelligence(
            job,
            match_score=float(match_score or 0),
            applications=applications,
            peer_jobs=entries,
        )
        key = _normalize_company(company)
        current = companies.get(key)
        if not current or intel["score"] > current["score"]:
            companies[key] = {
                "company": company,
                "score": intel["score"],
                "label": intel["label"],
                "action": intel["action"],
                "best_job": {
                    "title": _job_value(job, "title", ""),
                    "url": _job_value(job, "url", ""),
                    "location": _job_value(job, "location", ""),
                    "source": _job_value(job, "source", ""),
                },
                "job_count": 0,
                "reasons": intel["reasons"],
                "risks": intel["risks"],
                "recruiter_targets": intel["recruiter_targets"],
                "search_links": intel["search_links"],
                "outreach_note": intel["outreach_note"],
            }
        companies[key]["job_count"] += 1

    return sorted(companies.values(), key=lambda target: target["score"], reverse=True)[:limit]


def urgency_message(job, score, salary=None):
    salary = salary or salary_competitiveness(_job_value(job, "salary"))
    title = _job_value(job, "title", "role")
    if score >= 0.78 and salary["label"] in {"Strong", "Aligned"}:
        return f"High match detected for a salary-aligned {title}."
    if score >= 0.7:
        return "Be among the first 50 applicants for this strong-fit role."
    if any(term in _job_text(job).lower() for term in REMOTE_TERMS):
        return "New remote role matched your search profile."
    return "Worth reviewing before the applicant pool gets crowded."


def cover_letter_outline(job, intelligence):
    """Generate a deterministic cover-letter structure for a matched role."""
    title = _job_value(job, "title", "the role")
    company = _job_value(job, "company", "the team")
    matched = intelligence.get("matched_skills") or []
    gaps = intelligence.get("missing_skills") or []

    return [
        f"Open with the exact role: {title} at {company}.",
        "Lead with 2-3 proof points tied to {}.".format(
            ", ".join(matched[:3]) if matched else "the role's highest-priority outcomes"
        ),
        "Connect your work to business outcomes: reliability, cost, speed, security, or scale.",
        "Address {} honestly if it is a real gap, or add credible adjacent experience.".format(
            gaps[0] if gaps else "the strongest required skill"
        ),
        "Close with a concise note on why you can deliver in the first 90 days.",
    ]
