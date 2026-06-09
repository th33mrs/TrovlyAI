"""
Notification preferences and premium alert templates for Trovly.

Provider-specific delivery adapters can call build_alert_message() and
should_send_alert() after a match is scored. The current app saves preferences
for email, SMS, Slack, Discord, Telegram, and push so Stripe/worker integration
can attach delivery later without changing the UX contract.
"""

from product_strategy import ALERT_CHANNELS, ALERT_TRIGGERS

DEFAULT_ALERT_PREFS = {
    "enabled": True,
    "channels": {
        "email": True,
        "sms": False,
        "slack": False,
        "discord": True,
        "telegram": True,
        "push": True,
    },
    "min_match": 0.72,
    "min_interview_probability": 55,
    "salary_target_only": False,
    "remote_only": True,
    "newly_posted_only": False,
}


def normalize_alert_preferences(prefs=None):
    prefs = prefs or {}
    normalized = {
        "enabled": prefs.get("enabled", DEFAULT_ALERT_PREFS["enabled"]),
        "channels": dict(DEFAULT_ALERT_PREFS["channels"]),
        "min_match": float(prefs.get("min_match", DEFAULT_ALERT_PREFS["min_match"])),
        "min_interview_probability": int(
            prefs.get(
                "min_interview_probability",
                DEFAULT_ALERT_PREFS["min_interview_probability"],
            )
        ),
        "salary_target_only": prefs.get(
            "salary_target_only",
            DEFAULT_ALERT_PREFS["salary_target_only"],
        ),
        "remote_only": prefs.get("remote_only", DEFAULT_ALERT_PREFS["remote_only"]),
        "newly_posted_only": prefs.get(
            "newly_posted_only",
            DEFAULT_ALERT_PREFS["newly_posted_only"],
        ),
    }
    normalized["channels"].update(prefs.get("channels", {}))
    return normalized


def should_send_alert(job, score, intelligence, prefs=None):
    """Decide whether a matched job should trigger a premium alert."""
    prefs = normalize_alert_preferences(prefs)
    if not prefs["enabled"]:
        return False, "Alerts are disabled"

    if score < prefs["min_match"]:
        return False, "Below match threshold"

    if intelligence.get("interview_probability", 0) < prefs["min_interview_probability"]:
        return False, "Below interview likelihood threshold"

    salary = intelligence.get("salary_competitiveness", {})
    if prefs["salary_target_only"] and salary.get("label") not in {"Strong", "Aligned"}:
        return False, "Below salary target"

    if prefs["remote_only"]:
        text = " ".join(
            str(getattr(job, key, "") if not isinstance(job, dict) else job.get(key, ""))
            for key in ["title", "location", "description"]
        ).lower()
        if "remote" not in text and "distributed" not in text:
            return False, "Not remote"

    return True, "High-fit alert"


def build_alert_message(job, intelligence, channel="email"):
    """Build concise urgency messaging for all notification channels."""
    title = job.get("title") if isinstance(job, dict) else getattr(job, "title", "Matched role")
    company = job.get("company") if isinstance(job, dict) else getattr(job, "company", "Company")
    salary = intelligence.get("salary_competitiveness", {})
    match_percent = intelligence.get("match_percent", 0)
    interview = intelligence.get("interview_probability", 0)
    urgency = intelligence.get("urgency", "High match detected.")

    if channel in {"sms", "push"}:
        return "{} {}% match: {} at {}. Interview likelihood {}%. Review now.".format(
            "High match detected.",
            match_percent,
            title,
            company,
            interview,
        )

    return {
        "subject": f"New {match_percent}% match: {title} at {company}",
        "headline": urgency,
        "body": (
            "{} at {} scored {}% with {}% interview likelihood. "
            "Salary signal: {}. Be among the first 50 applicants."
        ).format(
            title,
            company,
            match_percent,
            interview,
            salary.get("label", "Unknown"),
        ),
        "triggers": ALERT_TRIGGERS,
        "channels": ALERT_CHANNELS,
    }
