import json
from datetime import datetime, timedelta
from pathlib import Path

import admin_tools
import auth


def test_is_admin_user_supports_record_roles_and_secret_allowlist():
    assert admin_tools.is_admin_user("owner", {"is_admin": True}) is True
    assert admin_tools.is_admin_user("owner", {"role": "owner"}) is True
    assert (
        admin_tools.is_admin_user(
            "carly",
            {"tier": "free"},
            configured_admins={"carly"},
        )
        is True
    )
    assert admin_tools.is_admin_user("member", {"tier": "pro"}, configured_admins=set()) is False


def test_build_admin_overview_counts_product_state():
    now = datetime.now()
    users = {
        "alice": {
            "created_at": now.isoformat(),
            "tier": "pro",
            "resume": "resume text",
            "onboarding_completed": True,
            "is_admin": True,
        },
        "bob": {
            "created_at": (now - timedelta(days=60)).isoformat(),
            "tier": "free",
            "locked_until": (now + timedelta(minutes=5)).isoformat(),
            "resume": "",
        },
    }
    usage = {"alice": {"2026-06": {"scans": 3, "tailors": 1}}}
    applications = {
        "alice": [
            {"status": "Interview"},
            {"status": "Offer"},
        ],
        "bob": [{"status": "Rejected"}],
    }
    events = [
        {
            "user": "alice",
            "event": "scan_completed",
            "created_at": now.isoformat(),
        },
        {
            "user": "alice",
            "event": "upgrade_intent",
            "created_at": now.isoformat(),
        },
    ]

    overview = admin_tools.build_admin_overview(
        users,
        usage,
        applications,
        events,
        period="2026-06",
        now=now,
    )

    assert overview["total_users"] == 2
    assert overview["admin_users"] == 1
    assert overview["premium_users"] == 1
    assert overview["locked_accounts"] == 1
    assert overview["scans_this_month"] == 3
    assert overview["tailors_this_month"] == 1
    assert overview["applications_total"] == 3
    assert overview["interviews_total"] == 2
    assert overview["offers_total"] == 1
    assert overview["upgrade_intents_30d"] == 1


def test_update_user_admin_fields_and_reset_usage():
    auth.save_users(
        {
            "alice": {
                "email": "alice@example.com",
                "password_hash": "hash",
                "tier": "free",
                "failed_attempts": 5,
                "locked_until": "2999-01-01T00:00:00",
            }
        }
    )
    with open("usage.json", "w") as f:
        json.dump({"alice": {"2026-06": {"scans": 4, "tailors": 2}}}, f)

    ok, msg = admin_tools.update_user_admin_fields(
        "alice",
        tier="career_hunter",
        is_admin=True,
        onboarding_completed=True,
        unlock=True,
        actor="owner",
    )

    assert ok is True, msg
    user = auth.load_users()["alice"]
    assert user["tier"] == "career_hunter"
    assert user["is_admin"] is True
    assert user["role"] == "admin"
    assert user["failed_attempts"] == 0
    assert user["locked_until"] is None
    assert user["onboarding_completed"] is True
    assert user["admin_updated_by"] == "owner"
    assert user["password_hash"] == "hash"

    ok, msg = admin_tools.reset_user_usage("alice", period="2026-06")

    assert ok is True, msg
    usage = json.loads(Path("usage.json").read_text())
    assert usage["alice"]["2026-06"] == {"scans": 0, "tailors": 0}
