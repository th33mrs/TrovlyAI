"""
Trovly - Usage Limits and Tier Management
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger("trovly.usage")

TIER_LIMITS = {
    "free": {
        "scans_per_month": 5,
        "max_sources": 4,
        "max_queries": 3,
        "tailor_per_month": 5,
        "label": "Free",
    },
    "pro": {
        "scans_per_month": -1,
        "max_sources": -1,
        "max_queries": -1,
        "tailor_per_month": -1,
        "label": "Pro",
    },
    "power": {
        "scans_per_month": -1,
        "max_sources": -1,
        "max_queries": -1,
        "tailor_per_month": -1,
        "label": "Power",
    },
}


def get_user_tier(user_data):
    """Get the user's tier, defaulting to free."""
    return user_data.get("tier", "free")


def get_tier_limits(tier):
    """Get the limits for a given tier."""
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])


def get_current_period():
    """Returns the current month identifier like '2026-04'."""
    now = datetime.now()
    return "{}-{:02d}".format(now.year, now.month)


def get_usage(username):
    """Read usage data for a user."""
    usage_path = Path("usage.json")
    if not usage_path.exists():
        return {}

    try:
        all_usage = json.loads(usage_path.read_text())
        return all_usage.get(username, {})
    except Exception as e:
        logger.error("Error reading usage.json: {}".format(e))
        return {}


def save_usage(username, usage_data):
    """Save usage data for a user."""
    usage_path = Path("usage.json")
    if usage_path.exists():
        all_usage = json.loads(usage_path.read_text())
    else:
        all_usage = {}

    all_usage[username] = usage_data
    usage_path.write_text(json.dumps(all_usage, indent=2))


def get_scans_used(username):
    """Get the number of scans used in the current period."""
    usage = get_usage(username)
    period = get_current_period()
    return usage.get(period, {}).get("scans", 0)


def get_tailors_used(username):
    """Get the number of resume tailors used in the current period."""
    usage = get_usage(username)
    period = get_current_period()
    return usage.get(period, {}).get("tailors", 0)


def increment_scans(username):
    """Add 1 to the user's scan count for this period."""
    usage = get_usage(username)
    period = get_current_period()

    if period not in usage:
        usage[period] = {"scans": 0, "tailors": 0}

    usage[period]["scans"] = usage[period].get("scans", 0) + 1
    save_usage(username, usage)
    return usage[period]["scans"]


def increment_tailors(username):
    """Add 1 to the user's tailor count for this period."""
    usage = get_usage(username)
    period = get_current_period()

    if period not in usage:
        usage[period] = {"scans": 0, "tailors": 0}

    usage[period]["tailors"] = usage[period].get("tailors", 0) + 1
    save_usage(username, usage)
    return usage[period]["tailors"]


def can_scan(username, tier):
    """Check if the user can run another scan this period."""
    limits = get_tier_limits(tier)
    if limits["scans_per_month"] == -1:
        return True, None

    used = get_scans_used(username)
    remaining = limits["scans_per_month"] - used

    if remaining <= 0:
        return False, "You have used all {} free scans this month. Upgrade to Pro for unlimited scans.".format(
            limits["scans_per_month"]
        )

    return True, "{} of {} free scans remaining this month".format(
        remaining, limits["scans_per_month"]
    )


def can_tailor(username, tier):
    """Check if the user can run another resume tailor this period."""
    limits = get_tier_limits(tier)
    if limits["tailor_per_month"] == -1:
        return True, None

    used = get_tailors_used(username)
    remaining = limits["tailor_per_month"] - used

    if remaining <= 0:
        return False, "You have used all {} free resume analyses this month. Upgrade to Pro for unlimited.".format(
            limits["tailor_per_month"]
        )

    return True, "{} of {} free resume analyses remaining".format(
        remaining, limits["tailor_per_month"]
    )


def get_usage_summary(username, tier):
    """Get a summary of usage for display."""
    limits = get_tier_limits(tier)
    scans_used = get_scans_used(username)
    tailors_used = get_tailors_used(username)

    return {
        "tier": tier,
        "tier_label": limits["label"],
        "scans_used": scans_used,
        "scans_limit": limits["scans_per_month"],
        "tailors_used": tailors_used,
        "tailors_limit": limits["tailor_per_month"],
        "scans_remaining": (
            -1 if limits["scans_per_month"] == -1
            else max(0, limits["scans_per_month"] - scans_used)
        ),
        "tailors_remaining": (
            -1 if limits["tailor_per_month"] == -1
            else max(0, limits["tailor_per_month"] - tailors_used)
        ),
    }
