"""
Trovly - ATS Job Source Plugins
=================================
Pulls jobs directly from company Applicant Tracking Systems (ATS).
These are higher quality than aggregators because they come straight
from the company's career page.

Supported:
- Greenhouse: Stripe, Airbnb, Discord, Reddit, Notion, Anthropic, Coinbase
- Lever: Plaid, GitHub, Netflix, Mixpanel, Twitch
- Ashby: Linear, Vanta, Shopify
- Himalayas (full JSON API)
- Working Nomads RSS
"""

import logging
import time
from html import unescape
import re

import feedparser
import requests

import config
from sources import JobPosting

logger = logging.getLogger("trovly.sources_ats")


def _strip_html(text):
    """Remove HTML tags from job description."""
    if not text:
        return ""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _matches_queries(text, queries):
    """Check if text contains any of the search queries."""
    if not queries:
        return True
    text_lower = text.lower()
    return any(q.lower() in text_lower for q in queries)


# ─── Greenhouse ─────────────────────────────────────────────────────
def fetch_greenhouse(queries):
    """
    Greenhouse Job Board API - no key required.
    Companies use board tokens like: stripe, airbnb, discord, reddit, etc.
    """
    if not hasattr(config, "GREENHOUSE_COMPANIES") or not config.GREENHOUSE_COMPANIES:
        return []

    jobs = []
    for company in config.GREENHOUSE_COMPANIES:
        try:
            url = "https://boards-api.greenhouse.io/v1/boards/{}/jobs".format(company)
            params = {"content": "true"}
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for j in data.get("jobs", []):
                title = j.get("title", "")
                content = _strip_html(j.get("content", ""))
                combined = title + " " + content

                if not _matches_queries(combined, queries):
                    continue

                location = ""
                if isinstance(j.get("location"), dict):
                    location = j["location"].get("name", "")

                jobs.append(JobPosting(
                    title=title,
                    company=company.replace("-", " ").title(),
                    description=content,
                    url=j.get("absolute_url", ""),
                    location=location,
                    source="greenhouse",
                    posted_date=j.get("updated_at", ""),
                    uid="greenhouse:{}:{}".format(company, j.get("id", "")),
                ))
            time.sleep(0.5)
        except Exception as e:
            logger.error("Greenhouse error for '{}': {}".format(company, e))

    return jobs


# ─── Lever ──────────────────────────────────────────────────────────
def fetch_lever(queries):
    """
    Lever public postings API - no key required.
    Companies use slugs like: plaid, github, netflix, mixpanel, twitch
    """
    if not hasattr(config, "LEVER_COMPANIES") or not config.LEVER_COMPANIES:
        return []

    jobs = []
    for company in config.LEVER_COMPANIES:
        try:
            url = "https://api.lever.co/v0/postings/{}".format(company)
            params = {"mode": "json"}
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for j in data:
                title = j.get("text", "")
                description = _strip_html(j.get("descriptionPlain", "") or j.get("description", ""))
                combined = title + " " + description

                if not _matches_queries(combined, queries):
                    continue

                location = ""
                categories = j.get("categories", {})
                if isinstance(categories, dict):
                    location = categories.get("location", "")

                salary = None
                salary_range = j.get("salaryRange")
                if salary_range and isinstance(salary_range, dict):
                    salary = "{} {} - {}".format(
                        salary_range.get("currency", "USD"),
                        salary_range.get("min", "?"),
                        salary_range.get("max", "?"),
                    )

                jobs.append(JobPosting(
                    title=title,
                    company=company.replace("-", " ").title(),
                    description=description,
                    url=j.get("hostedUrl", ""),
                    location=location,
                    source="lever",
                    posted_date=str(j.get("createdAt", "")),
                    salary=salary,
                    uid="lever:{}:{}".format(company, j.get("id", "")),
                ))
            time.sleep(0.5)
        except Exception as e:
            logger.error("Lever error for '{}': {}".format(company, e))

    return jobs


# ─── Ashby ──────────────────────────────────────────────────────────
def fetch_ashby(queries):
    """
    Ashby public posting API - no key required.
    Companies use job board names like: linear, vanta, shopify
    """
    if not hasattr(config, "ASHBY_COMPANIES") or not config.ASHBY_COMPANIES:
        return []

    jobs = []
    for company in config.ASHBY_COMPANIES:
        try:
            url = "https://api.ashbyhq.com/posting-api/job-board/{}".format(company)
            params = {"includeCompensation": "true"}
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            for j in data.get("jobs", []):
                title = j.get("title", "")
                description = _strip_html(j.get("descriptionHtml", ""))
                combined = title + " " + description

                if not _matches_queries(combined, queries):
                    continue

                location = j.get("locationName", "")
                if j.get("isRemote"):
                    location = location + " (Remote)" if location else "Remote"

                salary = None
                comp = j.get("compensation")
                if comp and isinstance(comp, dict):
                    summary = comp.get("compensationTierSummary", "")
                    if summary:
                        salary = summary

                jobs.append(JobPosting(
                    title=title,
                    company=j.get("companyName", company.replace("-", " ").title()),
                    description=description,
                    url=j.get("jobUrl", ""),
                    location=location,
                    source="ashby",
                    posted_date=j.get("publishedAt", ""),
                    salary=salary,
                    uid="ashby:{}:{}".format(company, j.get("id", "")),
                ))
            time.sleep(0.5)
        except Exception as e:
            logger.error("Ashby error for '{}': {}".format(company, e))

    return jobs


# ─── Himalayas Full JSON API ───────────────────────────────────────
def fetch_himalayas_api(queries):
    """
    Himalayas full JSON API with search filters.
    Way more data than the RSS feed - up to 100 results per query with rich metadata.
    """
    jobs = []
    for q in queries:
        try:
            resp = requests.get(
                "https://himalayas.app/jobs/api/search",
                params={"q": q, "limit": 50},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()

            for j in data.get("jobs", []):
                location = j.get("locationRestrictions") or "Remote"
                if isinstance(location, list):
                    location = ", ".join(location[:3]) if location else "Remote"

                salary = None
                salary_min = j.get("salaryMin")
                salary_max = j.get("salaryMax")
                if salary_min and salary_max:
                    currency = j.get("currency", "USD")
                    salary = "{} {} - {}".format(currency, salary_min, salary_max)

                jobs.append(JobPosting(
                    title=j.get("title", ""),
                    company=j.get("companyName", "Unknown"),
                    description=_strip_html(j.get("excerpt", "") or j.get("description", "")),
                    url=j.get("applicationLink") or j.get("guid", ""),
                    location=location,
                    source="himalayas_api",
                    posted_date=j.get("pubDate", ""),
                    salary=salary,
                    uid="himalayas_api:{}".format(j.get("guid", j.get("title", ""))),
                ))
            time.sleep(1)
        except Exception as e:
            logger.error("Himalayas API error for '{}': {}".format(q, e))

    return jobs


# ─── Working Nomads ────────────────────────────────────────────────
def fetch_working_nomads(queries):
    """Working Nomads RSS feed - no key required."""
    jobs = []
    feed_url = "https://www.workingnomads.com/jobsrss/feed/jobs.rss"

    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:75]:
            title = entry.get("title", "")
            desc = _strip_html(entry.get("summary", "") or entry.get("description", ""))
            combined = title + " " + desc

            if not _matches_queries(combined, queries):
                continue

            jobs.append(JobPosting(
                title=title,
                company=entry.get("author", "Unknown"),
                description=desc,
                url=entry.get("link", ""),
                location="Remote",
                source="working_nomads",
                posted_date=entry.get("published", ""),
                uid="working_nomads:{}".format(entry.get("link", "")),
            ))
    except Exception as e:
        logger.error("Working Nomads error: {}".format(e))

    return jobs


# ─── Aggregator ─────────────────────────────────────────────────────
ATS_SOURCE_MAP = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "himalayas_api": fetch_himalayas_api,
    "working_nomads": fetch_working_nomads,
}
