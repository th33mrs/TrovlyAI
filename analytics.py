"""
Lightweight product analytics for the current JSON-backed Streamlit app.

This is not a replacement for PostHog/Segment in production, but it gives the
team immediate funnel, usage, and retention data while the SaaS architecture is
being hardened.
"""

import json
import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("trovly.analytics")

EVENTS_PATH = Path("analytics_events.json")


def _load_events():
    if not EVENTS_PATH.exists():
        return []
    try:
        return json.loads(EVENTS_PATH.read_text())
    except Exception as exc:
        logger.error("Error loading analytics events: %s", exc)
        return []


def _save_events(events):
    EVENTS_PATH.write_text(json.dumps(events, indent=2))


def track_event(username, event_name, properties=None):
    """Append a product analytics event."""
    events = _load_events()
    events.append(
        {
            "user": username or "anonymous",
            "event": event_name,
            "properties": properties or {},
            "created_at": datetime.now().isoformat(),
        }
    )
    _save_events(events)


def get_user_events(username, days=None):
    events = [event for event in _load_events() if event.get("user") == username]
    if days is None:
        return events
    cutoff = datetime.now() - timedelta(days=days)
    return [
        event for event in events if _event_datetime(event) and _event_datetime(event) >= cutoff
    ]


def _event_datetime(event):
    try:
        return datetime.fromisoformat(event.get("created_at", ""))
    except Exception:
        return None


def get_funnel_metrics(days=30):
    """Return SaaS funnel metrics for admin analytics."""
    events = _load_events()
    cutoff = datetime.now() - timedelta(days=days)
    filtered = [
        event for event in events if _event_datetime(event) and _event_datetime(event) >= cutoff
    ]
    by_event = Counter(event["event"] for event in filtered)
    users_by_event = defaultdict(set)
    for event in filtered:
        users_by_event[event["event"]].add(event.get("user", "anonymous"))

    funnel = [
        ("signup_completed", "Signups"),
        ("profile_saved", "Profiles completed"),
        ("scan_completed", "Scans completed"),
        ("job_apply_clicked", "Apply clicks"),
        ("application_tracked", "Applications tracked"),
        ("upgrade_intent", "Upgrade intents"),
    ]
    rows = []
    previous = None
    for key, label in funnel:
        users = len(users_by_event.get(key, set()))
        conversion = None
        if previous:
            conversion = round(users / previous * 100, 1) if previous else 0
        rows.append(
            {
                "event": key,
                "label": label,
                "events": by_event.get(key, 0),
                "users": users,
                "conversion_from_previous": conversion,
            }
        )
        previous = users
    return rows


def get_retention_metrics(days=30):
    """Simple engagement retention view."""
    events = _load_events()
    cutoff = datetime.now() - timedelta(days=days)
    active_by_day = defaultdict(set)
    for event in events:
        dt = _event_datetime(event)
        if not dt or dt < cutoff:
            continue
        active_by_day[dt.date().isoformat()].add(event.get("user", "anonymous"))

    return [
        {"date": day, "active_users": len(users)} for day, users in sorted(active_by_day.items())
    ]


def user_career_metrics(username, applications_stats=None, tracked_jobs=None):
    """Dashboard metrics that connect product usage to career outcomes."""
    events = get_user_events(username)
    event_counts = Counter(event["event"] for event in events)
    tracked_jobs = tracked_jobs or []
    applications_stats = applications_stats or {}

    high_quality_matches = [job for job in tracked_jobs if job.get("match_score", 0) >= 0.7]
    total_matches = len(tracked_jobs)
    match_quality = (
        round(len(high_quality_matches) / total_matches * 100, 1) if total_matches else 0
    )
    applications_saved = max(0, total_matches - applications_stats.get("total", 0))
    interviews = applications_stats.get("interviews", 0)

    return {
        "resume_uploads": event_counts.get("profile_saved", 0),
        "scans": event_counts.get("scan_completed", 0),
        "tailors": event_counts.get("tailor_completed", 0),
        "apply_clicks": event_counts.get("job_apply_clicked", 0),
        "upgrade_intents": event_counts.get("upgrade_intent", 0),
        "interviews_generated": interviews,
        "applications_saved": applications_saved,
        "estimated_salary_uplift": applications_stats.get("estimated_salary_uplift", 31000),
        "match_quality": match_quality,
    }
