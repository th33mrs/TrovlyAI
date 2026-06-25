"""Eligibility, pacing, and queue management for consent-based auto apply."""

from __future__ import annotations

import hashlib
import json
import logging
import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from dateutil import parser as date_parser

logger = logging.getLogger("trovly.auto_apply")
UTC = timezone.utc  # noqa: UP017 - Python 3.10 does not provide datetime.UTC.

QUEUE_PATH = Path("auto_apply_queue.json")

DEFAULT_AUTO_APPLY_SETTINGS = {
    "enabled": False,
    "min_match_score": 0.80,
    "max_post_age_hours": 24,
    "weekly_target": 200,
    "weekly_hard_cap": 250,
    "daily_hard_cap": 50,
    "consent": False,
    "consent_at": None,
    "excluded_keywords": [],
}

ACTIVE_QUEUE_STATUSES = {"queued", "needs_review", "failed"}
FINAL_QUEUE_STATUSES = {"submitted", "skipped"}


@dataclass(frozen=True)
class SubmissionResult:
    """A provider adapter result. Only confirmed results count as submitted."""

    confirmed: bool
    reference: str = ""
    message: str = ""
    needs_review: bool = False


def normalize_settings(settings: dict[str, Any] | None) -> dict[str, Any]:
    """Merge persisted values with bounded defaults."""
    normalized = {**DEFAULT_AUTO_APPLY_SETTINGS, **(settings or {})}
    normalized["enabled"] = bool(normalized.get("enabled"))
    normalized["consent"] = bool(normalized.get("consent"))
    normalized["min_match_score"] = min(
        max(float(normalized.get("min_match_score", 0.80)), 0.50), 0.99
    )
    normalized["max_post_age_hours"] = min(
        max(int(normalized.get("max_post_age_hours", 24)), 1), 168
    )
    normalized["weekly_target"] = min(max(int(normalized.get("weekly_target", 200)), 1), 1000)
    normalized["weekly_hard_cap"] = min(
        max(
            int(normalized.get("weekly_hard_cap", 250)),
            normalized["weekly_target"],
        ),
        1500,
    )
    normalized["daily_hard_cap"] = min(max(int(normalized.get("daily_hard_cap", 50)), 1), 250)
    normalized["excluded_keywords"] = [
        str(value).strip().lower()
        for value in normalized.get("excluded_keywords", [])
        if str(value).strip()
    ]
    return normalized


def validate_application_profile(profile: dict[str, Any]) -> list[str]:
    """Return fields that must be completed before auto apply can be enabled."""
    required = {
        "full_name": "full name",
        "email": "email",
        "phone": "phone",
        "location": "location",
        "work_authorization": "work authorization",
    }
    return [label for key, label in required.items() if not str(profile.get(key, "")).strip()]


def _utc_now(now: datetime | None = None) -> datetime:
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        return current.replace(tzinfo=UTC)
    return current.astimezone(UTC)


def _job_value(job: Any, field: str, default: Any = "") -> Any:
    if isinstance(job, dict):
        return job.get(field, default)
    return getattr(job, field, default)


def _parse_datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return _utc_now(value)
    if isinstance(value, int | float) or str(value).strip().isdigit():
        try:
            timestamp = float(value)
            while timestamp > 10_000_000_000:
                timestamp /= 1000
            if timestamp > 1_000_000_000:
                return datetime.fromtimestamp(timestamp, tz=UTC)
        except (OSError, OverflowError, TypeError, ValueError):
            return None
    try:
        parsed = date_parser.parse(str(value))
    except (TypeError, ValueError, OverflowError):
        return None
    return _utc_now(parsed)


def _job_uid(job: Any) -> str:
    existing = str(_job_value(job, "uid", "")).strip()
    if existing:
        return existing
    identity = "|".join(
        [
            str(_job_value(job, "company", "")).strip().lower(),
            str(_job_value(job, "title", "")).strip().lower(),
            str(_job_value(job, "url", "")).strip().lower(),
        ]
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]


def _application_keys(applications: list[dict[str, Any]] | None) -> set[str]:
    keys = set()
    for application in applications or []:
        url = str(application.get("url", "")).strip().lower()
        company = str(application.get("company", "")).strip().lower()
        title = str(application.get("title", "")).strip().lower()
        if url:
            keys.add(f"url:{url}")
        if company and title:
            keys.add(f"role:{company}|{title}")
    return keys


def evaluate_auto_apply_eligibility(
    job: Any,
    score: float,
    settings: dict[str, Any] | None = None,
    existing_applications: list[dict[str, Any]] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Evaluate the non-negotiable rules for entering the auto-apply queue."""
    normalized = normalize_settings(settings)
    blockers: list[str] = []
    reasons: list[str] = []
    current = _utc_now(now)
    posted = _parse_datetime(_job_value(job, "posted_date", None))
    age_hours = None

    if float(score) <= normalized["min_match_score"]:
        blockers.append("Match must be over {:.0%}".format(normalized["min_match_score"]))
    else:
        reasons.append(f"{float(score):.0%} match clears the threshold")

    if posted is None:
        blockers.append("Posting date is unknown")
    else:
        age_hours = max((current - posted).total_seconds() / 3600, 0)
        if posted > current + timedelta(hours=1):
            blockers.append("Posting date is in the future")
        elif age_hours > normalized["max_post_age_hours"]:
            blockers.append(
                "Posting is older than {} hours".format(normalized["max_post_age_hours"])
            )
        else:
            reasons.append(f"Posted {age_hours:.1f} hours ago")

    url = str(_job_value(job, "url", "")).strip()
    if not url:
        blockers.append("Application URL is missing")

    description = " ".join(
        [
            str(_job_value(job, "title", "")),
            str(_job_value(job, "description", "")),
        ]
    ).lower()
    for keyword in normalized["excluded_keywords"]:
        if keyword in description:
            blockers.append(f"Excluded keyword detected: {keyword}")

    keys = _application_keys(existing_applications)
    company = str(_job_value(job, "company", "")).strip().lower()
    title = str(_job_value(job, "title", "")).strip().lower()
    if url and f"url:{url.lower()}" in keys:
        blockers.append("This application is already tracked")
    elif company and title and f"role:{company}|{title}" in keys:
        blockers.append("This company and role are already tracked")

    return {
        "eligible": not blockers,
        "reasons": reasons,
        "blockers": blockers,
        "age_hours": round(age_hours, 1) if age_hours is not None else None,
        "posted_at": posted.isoformat() if posted else None,
    }


def _load_queue(path: Path = QUEUE_PATH) -> dict[str, list[dict[str, Any]]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError) as exc:
        logger.error("Unable to load auto-apply queue: %s", exc)
        return {}


def _save_queue(data: dict[str, list[dict[str, Any]]], path: Path = QUEUE_PATH) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2))
    temporary.replace(path)


def list_queue(
    username: str,
    statuses: set[str] | None = None,
    path: Path = QUEUE_PATH,
) -> list[dict[str, Any]]:
    items = _load_queue(path).get(username, [])
    if statuses:
        items = [item for item in items if item.get("status") in statuses]
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)


def enqueue_matches(
    username: str,
    matches: list[tuple[Any, float]],
    settings: dict[str, Any] | None = None,
    existing_applications: list[dict[str, Any]] | None = None,
    now: datetime | None = None,
    path: Path = QUEUE_PATH,
) -> dict[str, Any]:
    """Queue eligible matches and return a transparent eligibility summary."""
    current = _utc_now(now)
    data = _load_queue(path)
    items = data.get(username, [])
    known_uids = {item.get("job_uid") for item in items}
    queued: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    duplicates = 0

    for job, score in matches:
        uid = _job_uid(job)
        if uid in known_uids:
            duplicates += 1
            continue
        evaluation = evaluate_auto_apply_eligibility(
            job,
            score,
            settings=settings,
            existing_applications=existing_applications,
            now=current,
        )
        if not evaluation["eligible"]:
            skipped.append(
                {
                    "job_uid": uid,
                    "title": str(_job_value(job, "title", "")),
                    "company": str(_job_value(job, "company", "")),
                    "blockers": evaluation["blockers"],
                }
            )
            continue

        item_id = hashlib.sha256(f"{username}|{uid}".encode()).hexdigest()[:16]
        item = {
            "id": item_id,
            "job_uid": uid,
            "title": str(_job_value(job, "title", "")).strip(),
            "company": str(_job_value(job, "company", "")).strip(),
            "url": str(_job_value(job, "url", "")).strip(),
            "location": str(_job_value(job, "location", "")).strip(),
            "salary": str(_job_value(job, "salary", "") or "").strip(),
            "source": str(_job_value(job, "source", "unknown")).strip().lower(),
            "match_score": round(float(score), 4),
            "posted_at": evaluation["posted_at"],
            "age_hours_at_queue": evaluation["age_hours"],
            "status": "queued",
            "reasons": evaluation["reasons"],
            "review_reason": "",
            "created_at": current.isoformat(),
            "updated_at": current.isoformat(),
            "submitted_at": None,
            "submission_reference": "",
        }
        items.append(item)
        queued.append(item)
        known_uids.add(uid)

    if queued:
        data[username] = items
        _save_queue(data, path)
    return {
        "queued": queued,
        "skipped": skipped,
        "duplicates": duplicates,
        "queued_count": len(queued),
        "skipped_count": len(skipped),
    }


def update_queue_item(
    username: str,
    item_id: str,
    status: str,
    *,
    review_reason: str = "",
    submission_reference: str = "",
    now: datetime | None = None,
    path: Path = QUEUE_PATH,
) -> tuple[bool, str, dict[str, Any] | None]:
    allowed_statuses = ACTIVE_QUEUE_STATUSES | FINAL_QUEUE_STATUSES
    if status not in allowed_statuses:
        return False, "Unknown queue status", None

    current = _utc_now(now)
    data = _load_queue(path)
    items = data.get(username, [])
    for item in items:
        if item.get("id") != item_id:
            continue
        item["status"] = status
        item["updated_at"] = current.isoformat()
        item["review_reason"] = review_reason
        if status == "submitted":
            item["submitted_at"] = current.isoformat()
            item["submission_reference"] = submission_reference or "manual-confirmation"
        data[username] = items
        _save_queue(data, path)
        return True, "Queue item updated", item
    return False, "Queue item not found", None


def weekly_progress(
    username: str,
    settings: dict[str, Any] | None = None,
    now: datetime | None = None,
    path: Path = QUEUE_PATH,
) -> dict[str, Any]:
    normalized = normalize_settings(settings)
    current = _utc_now(now)
    week_start = (current - timedelta(days=current.weekday())).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    day_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
    items = list_queue(username, path=path)
    submitted_dates = [
        _parse_datetime(item.get("submitted_at"))
        for item in items
        if item.get("status") == "submitted"
    ]
    submitted_this_week = sum(
        1 for submitted_at in submitted_dates if submitted_at and submitted_at >= week_start
    )
    submitted_today = sum(
        1 for submitted_at in submitted_dates if submitted_at and submitted_at >= day_start
    )
    remaining = max(normalized["weekly_target"] - submitted_this_week, 0)
    days_remaining = max(7 - current.weekday(), 1)
    return {
        "submitted_this_week": submitted_this_week,
        "submitted_today": submitted_today,
        "weekly_target": normalized["weekly_target"],
        "weekly_hard_cap": normalized["weekly_hard_cap"],
        "daily_hard_cap": normalized["daily_hard_cap"],
        "remaining": remaining,
        "daily_pace": math.ceil(remaining / days_remaining) if remaining else 0,
        "queued": sum(1 for item in items if item.get("status") == "queued"),
        "needs_review": sum(1 for item in items if item.get("status") == "needs_review"),
        "failed": sum(1 for item in items if item.get("status") == "failed"),
    }


Submitter = Callable[[dict[str, Any], dict[str, Any]], SubmissionResult]


def process_queue(
    username: str,
    profile: dict[str, Any],
    settings: dict[str, Any] | None = None,
    submitters: dict[str, Submitter] | None = None,
    now: datetime | None = None,
    path: Path = QUEUE_PATH,
) -> dict[str, int]:
    """Run connected source adapters without inventing successful submissions."""
    normalized = normalize_settings(settings)
    results = {"submitted": 0, "needs_review": 0, "failed": 0, "deferred": 0}
    missing = validate_application_profile(profile)
    if not normalized["enabled"] or not normalized["consent"] or missing:
        results["deferred"] = len(list_queue(username, {"queued"}, path))
        return results

    adapters = submitters or {}
    progress = weekly_progress(username, normalized, now=now, path=path)
    for item in reversed(list_queue(username, {"queued"}, path)):
        if progress["submitted_this_week"] >= normalized["weekly_hard_cap"]:
            results["deferred"] += 1
            continue
        if progress["submitted_today"] >= normalized["daily_hard_cap"]:
            results["deferred"] += 1
            continue

        submitter = adapters.get(item.get("source", ""))
        if submitter is None:
            update_queue_item(
                username,
                item["id"],
                "needs_review",
                review_reason="No confirmed submission adapter is connected for this source.",
                now=now,
                path=path,
            )
            results["needs_review"] += 1
            continue

        try:
            result = submitter(item, profile)
        except Exception as exc:  # Provider failures should never stop the queue.
            logger.exception("Auto-apply adapter failed for %s", item.get("id"))
            update_queue_item(
                username,
                item["id"],
                "failed",
                review_reason=str(exc),
                now=now,
                path=path,
            )
            results["failed"] += 1
            continue

        if result.confirmed:
            update_queue_item(
                username,
                item["id"],
                "submitted",
                submission_reference=result.reference,
                now=now,
                path=path,
            )
            results["submitted"] += 1
            progress["submitted_this_week"] += 1
            progress["submitted_today"] += 1
        elif result.needs_review:
            update_queue_item(
                username,
                item["id"],
                "needs_review",
                review_reason=result.message,
                now=now,
                path=path,
            )
            results["needs_review"] += 1
        else:
            update_queue_item(
                username,
                item["id"],
                "failed",
                review_reason=result.message,
                now=now,
                path=path,
            )
            results["failed"] += 1
    return results
