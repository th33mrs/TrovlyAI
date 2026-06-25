from datetime import datetime, timedelta, timezone

from auto_apply import (
    SubmissionResult,
    enqueue_matches,
    evaluate_auto_apply_eligibility,
    list_queue,
    process_queue,
    update_queue_item,
    weekly_progress,
)

UTC = timezone.utc  # noqa: UP017 - Test suite runs on Python 3.10.
NOW = datetime(2026, 6, 24, 12, tzinfo=UTC)


def _job(**overrides):
    job = {
        "uid": "greenhouse:123",
        "title": "Senior Platform Engineer",
        "company": "Acme Cloud",
        "description": "Build distributed cloud infrastructure with Python and Kubernetes.",
        "url": "https://boards.greenhouse.io/acme/jobs/123",
        "location": "Remote",
        "source": "greenhouse",
        "posted_date": (NOW - timedelta(hours=6)).isoformat(),
        "salary": "$170,000 - $210,000",
    }
    job.update(overrides)
    return job


def _settings(**overrides):
    settings = {
        "enabled": True,
        "consent": True,
        "min_match_score": 0.80,
        "max_post_age_hours": 24,
        "weekly_target": 200,
        "weekly_hard_cap": 250,
        "daily_hard_cap": 50,
    }
    settings.update(overrides)
    return settings


def _profile():
    return {
        "full_name": "Carly Jordan",
        "email": "carly@example.com",
        "phone": "555-0100",
        "location": "New York, NY",
        "work_authorization": "Authorized to work in the United States",
    }


def test_score_must_be_strictly_over_threshold():
    at_threshold = evaluate_auto_apply_eligibility(_job(), 0.80, _settings(), now=NOW)
    over_threshold = evaluate_auto_apply_eligibility(_job(), 0.8001, _settings(), now=NOW)

    assert at_threshold["eligible"] is False
    assert "Match must be over 80%" in at_threshold["blockers"]
    assert over_threshold["eligible"] is True


def test_posting_must_have_known_date_within_24_hours():
    exactly_24_hours = evaluate_auto_apply_eligibility(
        _job(posted_date=(NOW - timedelta(hours=24)).isoformat()),
        0.90,
        _settings(),
        now=NOW,
    )
    too_old = evaluate_auto_apply_eligibility(
        _job(posted_date=(NOW - timedelta(hours=24, seconds=1)).isoformat()),
        0.90,
        _settings(),
        now=NOW,
    )
    unknown = evaluate_auto_apply_eligibility(
        _job(posted_date=None), 0.90, _settings(), now=NOW
    )

    assert exactly_24_hours["eligible"] is True
    assert too_old["eligible"] is False
    assert unknown["eligible"] is False


def test_queue_deduplicates_jobs_and_tracked_applications(tmp_path):
    queue_path = tmp_path / "queue.json"
    first = enqueue_matches(
        "carly",
        [(_job(), 0.91)],
        settings=_settings(),
        now=NOW,
        path=queue_path,
    )
    duplicate = enqueue_matches(
        "carly",
        [(_job(), 0.94)],
        settings=_settings(),
        now=NOW,
        path=queue_path,
    )
    tracked = enqueue_matches(
        "carly",
        [(_job(uid="greenhouse:456", url="https://example.com/456"), 0.93)],
        settings=_settings(),
        existing_applications=[
            {"title": "Senior Platform Engineer", "company": "Acme Cloud"}
        ],
        now=NOW,
        path=queue_path,
    )

    assert first["queued_count"] == 1
    assert duplicate["duplicates"] == 1
    assert tracked["skipped_count"] == 1
    assert len(list_queue("carly", path=queue_path)) == 1


def test_weekly_progress_counts_only_confirmed_submissions(tmp_path):
    queue_path = tmp_path / "queue.json"
    enqueue_matches(
        "carly",
        [(_job(), 0.91)],
        settings=_settings(),
        now=NOW,
        path=queue_path,
    )
    queued_item = list_queue("carly", path=queue_path)[0]
    before = weekly_progress("carly", _settings(), now=NOW, path=queue_path)
    update_queue_item(
        "carly", queued_item["id"], "submitted", now=NOW, path=queue_path
    )
    after = weekly_progress("carly", _settings(), now=NOW, path=queue_path)

    assert before["submitted_this_week"] == 0
    assert before["remaining"] == 200
    assert after["submitted_this_week"] == 1
    assert after["remaining"] == 199


def test_process_queue_requires_adapter_confirmation(tmp_path):
    queue_path = tmp_path / "queue.json"
    enqueue_matches(
        "carly",
        [(_job(), 0.91)],
        settings=_settings(),
        now=NOW,
        path=queue_path,
    )

    without_adapter = process_queue(
        "carly",
        _profile(),
        _settings(),
        submitters={},
        now=NOW,
        path=queue_path,
    )
    assert without_adapter["submitted"] == 0
    assert without_adapter["needs_review"] == 1

    queue_path_2 = tmp_path / "confirmed.json"
    enqueue_matches(
        "carly",
        [(_job(), 0.91)],
        settings=_settings(),
        now=NOW,
        path=queue_path_2,
    )
    confirmed = process_queue(
        "carly",
        _profile(),
        _settings(),
        submitters={
            "greenhouse": lambda _item, _profile: SubmissionResult(
                confirmed=True,
                reference="greenhouse-confirmation-123",
            )
        },
        now=NOW,
        path=queue_path_2,
    )

    assert confirmed["submitted"] == 1
    assert weekly_progress("carly", _settings(), now=NOW, path=queue_path_2)[
        "submitted_this_week"
    ] == 1
