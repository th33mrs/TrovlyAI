"""Admin helpers for the JSON-backed Trovly app."""

import json
import logging
import os
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

from auth import load_users, save_users
from usage_limits import TIER_LIMITS, get_current_period

logger = logging.getLogger("trovly.admin")

ADMIN_SECRET_KEYS = ("TROVLY_ADMIN_USERS", "ADMIN_USERS")
STORE_PATHS = (
    "users.json",
    "usage.json",
    "applications.json",
    "analytics_events.json",
    "tracked_jobs.json",
)
INTERVIEW_STATUSES = {"Phone Screen", "Interview", "Take Home", "Final Round", "Offer"}


def _read_json(path, default):
    path = Path(path)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        logger.error("Error reading %s: %s", path, exc)
        return default


def _write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2))


def _parse_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _date_label(value):
    if not value:
        return ""
    return str(value)[:10]


def _parse_admins(raw_value):
    if not raw_value:
        return set()
    return {
        item.strip().lower()
        for item in str(raw_value).replace(";", ",").split(",")
        if item.strip()
    }


def _streamlit_secret(key):
    try:
        import streamlit as st

        if key in st.secrets:
            return st.secrets.get(key, "")
    except Exception:
        return ""
    return ""


def configured_admin_usernames():
    """Return admin usernames configured through env vars or Streamlit secrets."""
    admins = set()
    for key in ADMIN_SECRET_KEYS:
        admins.update(_parse_admins(os.environ.get(key, "")))
        admins.update(_parse_admins(_streamlit_secret(key)))
    return admins


def is_admin_user(username, user_data=None, configured_admins=None):
    """Check whether a user should see the admin panel."""
    if not username:
        return False

    user_data = user_data or {}
    if user_data.get("is_admin") is True:
        return True

    role = str(user_data.get("role", "")).strip().lower()
    if role in {"admin", "owner"}:
        return True

    configured_admins = (
        configured_admin_usernames() if configured_admins is None else configured_admins
    )
    return username.strip().lower() in configured_admins


def load_admin_state():
    """Load all JSON stores needed by the admin panel."""
    return {
        "users": load_users(),
        "usage": _read_json("usage.json", {}),
        "applications": _read_json("applications.json", {}),
        "events": _read_json("analytics_events.json", []),
    }


def _normalized_tier(user_data):
    tier = user_data.get("tier", "free")
    if tier == "power":
        return "career_hunter"
    return tier if tier in TIER_LIMITS else "free"


def _is_locked(user_data, now=None):
    locked_until = _parse_datetime(user_data.get("locked_until"))
    if not locked_until:
        return False
    return locked_until > (now or datetime.now())


def _events_since(events, days, now=None):
    now = now or datetime.now()
    cutoff = now - timedelta(days=days)
    return [
        event
        for event in events
        if _parse_datetime(event.get("created_at"))
        and _parse_datetime(event.get("created_at")) >= cutoff
    ]


def build_admin_overview(users, usage, applications, events, period=None, now=None):
    """Return top-line product and account metrics for admins."""
    period = period or get_current_period()
    now = now or datetime.now()
    configured_admins = configured_admin_usernames()
    events_30d = _events_since(events, 30, now=now)

    all_apps = [app for apps in applications.values() for app in apps]
    active_users = {event.get("user", "anonymous") for event in events_30d}
    new_users = [
        user
        for user in users.values()
        if _parse_datetime(user.get("created_at"))
        and _parse_datetime(user.get("created_at")) >= now - timedelta(days=30)
    ]

    return {
        "total_users": len(users),
        "new_users_30d": len(new_users),
        "active_users_30d": len(active_users),
        "admin_users": sum(
            1
            for username, user in users.items()
            if is_admin_user(username, user, configured_admins=configured_admins)
        ),
        "premium_users": sum(
            1 for user in users.values() if _normalized_tier(user) != "free"
        ),
        "locked_accounts": sum(1 for user in users.values() if _is_locked(user, now=now)),
        "onboarding_complete": sum(
            1 for user in users.values() if user.get("onboarding_completed")
        ),
        "profiles_with_resume": sum(
            1 for user in users.values() if str(user.get("resume", "")).strip()
        ),
        "scans_this_month": sum(
            usage.get(username, {}).get(period, {}).get("scans", 0) for username in users
        ),
        "tailors_this_month": sum(
            usage.get(username, {}).get(period, {}).get("tailors", 0) for username in users
        ),
        "applications_total": len(all_apps),
        "interviews_total": sum(
            1 for app in all_apps if app.get("status") in INTERVIEW_STATUSES
        ),
        "offers_total": sum(1 for app in all_apps if app.get("status") == "Offer"),
        "events_30d": len(events_30d),
        "upgrade_intents_30d": sum(
            1 for event in events_30d if event.get("event") == "upgrade_intent"
        ),
    }


def build_user_rows(users, usage, applications, events, period=None):
    """Build safe, table-friendly user rows for the admin UI."""
    period = period or get_current_period()
    configured_admins = configured_admin_usernames()
    events_by_user = {}
    for event in events:
        user = event.get("user", "anonymous")
        events_by_user.setdefault(user, []).append(event)

    rows = []
    for username, user in sorted(users.items()):
        user_events = events_by_user.get(username, [])
        sorted_events = sorted(
            user_events,
            key=lambda event: event.get("created_at", ""),
            reverse=True,
        )
        period_usage = usage.get(username, {}).get(period, {})
        apps = applications.get(username, [])
        status_counts = Counter(app.get("status", "Applied") for app in apps)
        tier = _normalized_tier(user)
        last_event = sorted_events[0] if sorted_events else {}

        rows.append(
            {
                "username": username,
                "email": user.get("email", ""),
                "tier": tier,
                "admin": is_admin_user(username, user, configured_admins=configured_admins),
                "locked": _is_locked(user),
                "onboarded": bool(user.get("onboarding_completed")),
                "created": _date_label(user.get("created_at")),
                "last_login": _date_label(user.get("last_login")),
                "resume_chars": len(str(user.get("resume", ""))),
                "queries": len(user.get("queries") or []),
                "scans": period_usage.get("scans", 0),
                "tailors": period_usage.get("tailors", 0),
                "applications": len(apps),
                "interviews": sum(status_counts.get(status, 0) for status in INTERVIEW_STATUSES),
                "offers": status_counts.get("Offer", 0),
                "events": len(user_events),
                "last_event": last_event.get("event", ""),
                "last_event_at": _date_label(last_event.get("created_at")),
            }
        )
    return rows


def build_event_rows(events, limit=50):
    """Return recent analytics events without raw object noise."""
    sorted_events = sorted(
        events,
        key=lambda event: event.get("created_at", ""),
        reverse=True,
    )
    rows = []
    for event in sorted_events[:limit]:
        properties = event.get("properties") or {}
        try:
            props = json.dumps(properties, sort_keys=True)
        except TypeError:
            props = str(properties)
        rows.append(
            {
                "created_at": event.get("created_at", "")[:19],
                "user": event.get("user", "anonymous"),
                "event": event.get("event", ""),
                "properties": props[:180],
            }
        )
    return rows


def build_event_mix(events, days=30):
    events = _events_since(events, days)
    counts = Counter(event.get("event", "unknown") for event in events)
    users_by_event = {}
    for event in events:
        users_by_event.setdefault(event.get("event", "unknown"), set()).add(
            event.get("user", "anonymous")
        )
    return [
        {"event": event, "events": count, "users": len(users_by_event.get(event, set()))}
        for event, count in counts.most_common()
    ]


def build_application_rows(applications, limit=50):
    rows = []
    for username, apps in applications.items():
        for app in apps:
            rows.append(
                {
                    "updated": (app.get("last_updated") or app.get("date_applied") or "")[:19],
                    "user": username,
                    "company": app.get("company", ""),
                    "title": app.get("title", ""),
                    "status": app.get("status", ""),
                    "source": app.get("source", ""),
                }
            )
    return sorted(rows, key=lambda row: row["updated"], reverse=True)[:limit]


def build_store_status(paths=STORE_PATHS):
    rows = []
    for path_name in paths:
        path = Path(path_name)
        exists = path.exists()
        data = _read_json(path, None) if exists else None
        if isinstance(data, dict):
            records = sum(len(value) if isinstance(value, list) else 1 for value in data.values())
        elif isinstance(data, list):
            records = len(data)
        else:
            records = 0
        rows.append(
            {
                "store": path_name,
                "status": "ok" if exists else "missing",
                "records": records,
                "updated": (
                    datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")
                    if exists
                    else ""
                ),
            }
        )
    return rows


def update_user_admin_fields(
    username,
    tier=None,
    is_admin=None,
    onboarding_completed=None,
    unlock=False,
    actor=None,
):
    """Update non-password account fields from the admin panel."""
    users = load_users()
    if username not in users:
        return False, "User not found"

    user = users[username]
    if tier is not None:
        if tier not in TIER_LIMITS:
            return False, "Unknown tier"
        user["tier"] = tier

    if is_admin is not None:
        user["is_admin"] = bool(is_admin)
        user["role"] = "admin" if is_admin else "member"

    if onboarding_completed is not None:
        user["onboarding_completed"] = bool(onboarding_completed)

    if unlock:
        user["failed_attempts"] = 0
        user["locked_until"] = None
        user["last_failed_attempt"] = None

    user["admin_updated_at"] = datetime.now().isoformat()
    if actor:
        user["admin_updated_by"] = actor

    users[username] = user
    save_users(users)
    return True, "User updated"


def reset_user_usage(username, period=None):
    """Reset scan and tailoring usage for the selected period."""
    period = period or get_current_period()
    usage = _read_json("usage.json", {})
    user_usage = usage.setdefault(username, {})
    user_usage[period] = {"scans": 0, "tailors": 0}
    _write_json("usage.json", usage)
    return True, "Usage reset"

