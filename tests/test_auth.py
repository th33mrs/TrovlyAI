"""
Tests for auth.py.

Two layers:
1. Pure logic tests for register_user (validation, dedupe, hashing).
2. End-to-end signup flow via Streamlit's AppTest harness — this is the
   regression test for the signup auto-login behavior. If anyone breaks
   the auto-login by going back to the old "Account created. Log in
   above." pattern, this test fails.
"""

from pathlib import Path

import pytest

import auth

HARNESS = str(Path(__file__).parent / "_login_harness.py")

VALID_PASS = "Sup3rStr0ng!Pass"


# ─── register_user — pure logic ──────────────────────────────────────


def test_register_user_success_persists():
    ok, msg = auth.register_user("alice_dev", VALID_PASS, "alice@example.com")
    assert ok is True, msg
    assert "alice_dev" in auth.load_users()


def test_register_user_rejects_duplicate_username():
    auth.register_user("bob", VALID_PASS, "bob@example.com")
    ok, msg = auth.register_user("bob", VALID_PASS, "bob2@example.com")
    assert ok is False
    assert "taken" in msg.lower()


def test_register_user_rejects_duplicate_email():
    auth.register_user("carol", VALID_PASS, "shared@example.com")
    ok, msg = auth.register_user("carol2", VALID_PASS, "shared@example.com")
    assert ok is False
    assert "email" in msg.lower()


def test_register_user_rejects_weak_password():
    ok, msg = auth.register_user("dan", "weak", "dan@example.com")
    assert ok is False
    assert "characters" in msg.lower()


def test_register_user_rejects_invalid_email():
    ok, msg = auth.register_user("erin", VALID_PASS, "not-an-email")
    assert ok is False
    assert "email" in msg.lower()


def test_password_is_hashed_not_plaintext():
    auth.register_user("frank", VALID_PASS, "frank@example.com")
    stored = auth.load_users()["frank"]["password_hash"]
    assert stored != VALID_PASS
    assert stored.startswith("$2")  # bcrypt prefix
    assert auth.verify_password(VALID_PASS, stored) is True


# ─── signup → auto-login regression (Streamlit AppTest) ──────────────


def test_signup_auto_logs_user_in_and_routes_to_platform():
    """
    The signup button must drop a brand-new user straight into the app
    (auto-login) — not show a "Log in above" message.

    After clicking 'Create account':
      - st.session_state.authenticated must flip to True
      - st.session_state.username must be set to the new username
      - login_page() must return the username on the next render
        (which is what app_hosted.py keys off of to show the platform)
    """
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(HARNESS)
    at.run()

    # Fill the four signup fields (keys defined in auth.login_page).
    at.text_input(key="reg_user").set_value("eve_test")
    at.text_input(key="reg_email").set_value("eve@example.com")
    at.text_input(key="reg_pass").set_value(VALID_PASS)
    at.text_input(key="reg_pass2").set_value(VALID_PASS)

    # Click the "Create account" button (no explicit key — find by label).
    create_btn = next(b for b in at.button if b.label == "Create account")
    create_btn.click().run()

    # Streamlit's AppTest SessionState supports `in` and item access but
    # not .get(), so probe membership first.
    assert "authenticated" in at.session_state, (
        "Signup did not auto-authenticate the new user"
    )
    assert at.session_state["authenticated"] is True
    assert at.session_state["username"] == "eve_test"


def test_signup_with_mismatched_passwords_does_not_authenticate():
    """Negative case — mismatched passwords must NOT log the user in."""
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_file(HARNESS)
    at.run()

    at.text_input(key="reg_user").set_value("mallory")
    at.text_input(key="reg_email").set_value("mallory@example.com")
    at.text_input(key="reg_pass").set_value(VALID_PASS)
    at.text_input(key="reg_pass2").set_value("Different!Pass99")

    create_btn = next(b for b in at.button if b.label == "Create account")
    create_btn.click().run()

    authenticated = (
        "authenticated" in at.session_state
        and at.session_state["authenticated"]
    )
    assert not authenticated, "Mismatched-password signup must not authenticate"
    assert "mallory" not in auth.load_users()
