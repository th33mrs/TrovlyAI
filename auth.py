"""
Trovly - Authentication (Hardened)
Security features:
- bcrypt password hashing (replaces SHA-256)
- Email + username uniqueness checks
- Password strength requirements
- Rate limiting on login attempts
- Account lockout after failed attempts
- Timing attack protection (constant-time comparison)
- Email format validation
- Username format validation (no special chars except _ and -)
"""

import json
import logging
import re
import time
from datetime import datetime, timedelta
from html import escape
from pathlib import Path
from textwrap import dedent

import bcrypt
import streamlit as st

from analytics import track_event
from notification_engine import DEFAULT_ALERT_PREFS
from product_strategy import (
    COMPANY_LOGOS,
    FAQS,
    FEATURE_GRID,
    HOMEPAGE_COPY,
    HOW_IT_WORKS,
    PLAN_CATALOG,
    SOCIAL_PROOF,
    SUCCESS_STORIES,
    TESTIMONIALS,
)

logger = logging.getLogger("trovly.auth")

# Security settings
MIN_PASSWORD_LENGTH = 12
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
RATE_LIMIT_SECONDS = 2
BCRYPT_ROUNDS = 12

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{3,32}$")
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def hash_password(password):
    """Hash password using bcrypt with random salt."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt(rounds=BCRYPT_ROUNDS)).decode("utf-8")


def verify_password(password, stored_hash):
    """Verify password against bcrypt hash. Constant-time comparison."""
    if isinstance(password, str):
        password = password.encode("utf-8")
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode("utf-8")
    try:
        return bcrypt.checkpw(password, stored_hash)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def validate_username(username):
    """Validate username format."""
    if not username or not isinstance(username, str):
        return False, "Username is required"
    username = username.strip()
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 32:
        return False, "Username must be 32 characters or less"
    if not USERNAME_PATTERN.match(username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    return True, username


def validate_email(email):
    """Validate email format."""
    if not email or not isinstance(email, str):
        return False, "Email is required"
    email = email.strip().lower()
    if len(email) > 254:
        return False, "Email is too long"
    if not EMAIL_PATTERN.match(email):
        return False, "Invalid email format"
    return True, email


def validate_password(password):
    """Validate password strength."""
    if not password or not isinstance(password, str):
        return False, "Password is required"
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    if len(password) > 128:
        return False, "Password is too long (max 128 characters)"

    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"[0-9]", password))
    has_special = bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};:,.<>?/]", password))

    strength_count = sum([has_upper, has_lower, has_digit, has_special])
    if strength_count < 3:
        return (
            False,
            "Password must contain at least 3 of: uppercase, lowercase, numbers, special characters",
        )

    common_passwords = {
        "password",
        "12345678",
        "qwerty",
        "letmein",
        "welcome",
        "admin123",
        "password123",
        "trovly",
        "trovlyai",
    }
    if password.lower() in common_passwords:
        return False, "This password is too common, please choose another"

    return True, "Strong password"


def load_users():
    """Load all users from disk."""
    users_path = Path("users.json")
    if not users_path.exists():
        return {}
    try:
        return json.loads(users_path.read_text())
    except Exception as e:
        logger.error(f"Error loading users: {e}")
        return {}


def save_users(users):
    """Save all users to disk."""
    users_path = Path("users.json")
    users_path.write_text(json.dumps(users, indent=2))


def email_exists(email, exclude_username=None):
    """Check if email is already in use."""
    email = email.lower().strip()
    users = load_users()
    for uname, data in users.items():
        if uname == exclude_username:
            continue
        if data.get("email", "").lower().strip() == email:
            return True
    return False


def username_exists(username):
    """Check if username is already taken."""
    users = load_users()
    return username in users


def is_account_locked(username):
    """Check if account is currently locked due to failed attempts."""
    users = load_users()
    user = users.get(username, {})
    locked_until = user.get("locked_until")
    if not locked_until:
        return False, None

    try:
        lock_time = datetime.fromisoformat(locked_until)
        if datetime.now() < lock_time:
            remaining = (lock_time - datetime.now()).total_seconds() / 60
            return True, f"Account locked. Try again in {int(remaining) + 1} minutes"
    except ValueError:
        return False, None
    return False, None


def record_failed_login(username):
    """Track failed login attempts and lock account if threshold reached."""
    users = load_users()
    if username not in users:
        return

    user = users[username]
    failed = user.get("failed_attempts", 0) + 1
    user["failed_attempts"] = failed
    user["last_failed_attempt"] = datetime.now().isoformat()

    if failed >= MAX_LOGIN_ATTEMPTS:
        lock_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
        user["locked_until"] = lock_until.isoformat()
        logger.warning(f"Account locked: {username} after {failed} failed attempts")

    users[username] = user
    save_users(users)


def reset_failed_attempts(username):
    """Clear failed attempt counter on successful login."""
    users = load_users()
    if username in users:
        users[username]["failed_attempts"] = 0
        users[username]["locked_until"] = None
        users[username]["last_login"] = datetime.now().isoformat()
        save_users(users)


def check_credentials(username, password):
    """
    Verify login credentials with security protections.
    Returns (success, message).
    """
    if not username or not password:
        time.sleep(RATE_LIMIT_SECONDS)
        return False, "Username and password are required"

    users = load_users()

    # Always do a bcrypt operation to prevent username enumeration via timing
    if username not in users:
        bcrypt.checkpw(b"dummy", bcrypt.hashpw(b"dummy", bcrypt.gensalt(rounds=4)))
        time.sleep(RATE_LIMIT_SECONDS)
        return False, "Invalid username or password"

    locked, lock_msg = is_account_locked(username)
    if locked:
        return False, lock_msg

    user = users[username]
    stored_hash = user.get("password_hash", "")

    if not verify_password(password, stored_hash):
        record_failed_login(username)
        time.sleep(RATE_LIMIT_SECONDS)
        attempts_left = MAX_LOGIN_ATTEMPTS - user.get("failed_attempts", 0) - 1
        if attempts_left <= 2 and attempts_left > 0:
            return False, f"Invalid credentials. {attempts_left} attempts remaining before lockout."
        return False, "Invalid username or password"

    reset_failed_attempts(username)
    return True, "Login successful"


def register_user(username, password, email):
    """
    Register new user with full validation.
    Returns (success, message).
    """
    # Validate username
    valid, result = validate_username(username)
    if not valid:
        return False, result
    username = result

    # Validate email
    valid, result = validate_email(email)
    if not valid:
        return False, result
    email = result

    # Validate password
    valid, result = validate_password(password)
    if not valid:
        return False, result

    # Check uniqueness
    if username_exists(username):
        return False, "Username already taken"

    if email_exists(email):
        return False, "An account with this email already exists"

    # Create user
    users = load_users()
    users[username] = {
        "password_hash": hash_password(password),
        "email": email,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "failed_attempts": 0,
        "locked_until": None,
        "role": "user",
        "is_admin": False,
        "tier": "free",
        "resume": "",
        "queries": [],
        "threshold": 0.55,
        "remote_only": True,
        "target_salary": 150000,
        "target_roles": [],
        "alert_preferences": DEFAULT_ALERT_PREFS,
        "auto_apply_settings": {
            "enabled": False,
            "min_match_score": 0.80,
            "max_post_age_hours": 24,
            "weekly_target": 200,
            "weekly_hard_cap": 250,
            "daily_hard_cap": 50,
            "consent": False,
            "consent_at": None,
            "excluded_keywords": [],
        },
        "application_profile": {},
        "onboarding_completed": False,
    }
    save_users(users)
    logger.info(f"New user registered: {username}")
    return True, "Account created successfully"


def find_username_by_email(email):
    """
    Find the username registered to an email address.
    Returns (success, message, username).
    """
    valid, result = validate_email(email)
    if not valid:
        return False, result, None
    email = result

    users = load_users()
    for username, data in users.items():
        if data.get("email", "").lower().strip() == email:
            return True, "Username found", username

    return False, "No account found for that email", None


def reset_password(username, email, new_password):
    """
    Reset a password after matching both username and account email.
    Returns (success, message).
    """
    valid, result = validate_username(username)
    if not valid:
        return False, result
    username = result

    valid, result = validate_email(email)
    if not valid:
        return False, result
    email = result

    valid, result = validate_password(new_password)
    if not valid:
        return False, result

    users = load_users()
    user = users.get(username)
    if not user or user.get("email", "").lower().strip() != email:
        return False, "Username and email do not match an account"

    user["password_hash"] = hash_password(new_password)
    user["failed_attempts"] = 0
    user["locked_until"] = None
    user["last_failed_attempt"] = None
    user["last_password_reset"] = datetime.now().isoformat()
    users[username] = user
    save_users(users)
    logger.info(f"Password reset for user: {username}")
    return True, "Password updated. You can log in with your new password."


def get_user_data(username):
    """Get user profile data."""
    users = load_users()
    return users.get(username, {})


def save_user_data(username, data):
    """Update user profile data (excludes auth fields)."""
    users = load_users()
    if username in users:
        # Don't allow auth fields to be overwritten
        protected_fields = {
            "created_at",
            "email",
            "failed_attempts",
            "is_admin",
            "last_password_reset",
            "locked_until",
            "password_hash",
            "role",
        }
        safe_data = {k: v for k, v in data.items() if k not in protected_fields}
        users[username].update(safe_data)
    else:
        users[username] = data
    save_users(users)


def _render_html(html):
    """Render HTML without letting Markdown turn indented blocks into code."""
    cleaned = dedent(html).strip()
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        cleaned = "\n".join(line.lstrip() for line in cleaned.splitlines())
        st.markdown(cleaned, unsafe_allow_html=True)


def _cards(items, class_name):
    html = []
    for item in items:
        html.append(
            "<div class='{class_name}'>"
            "<div class='card-kicker'>{kicker}</div>"
            "<h3>{title}</h3>"
            "<p>{body}</p>"
            "</div>".format(
                class_name=class_name,
                kicker=escape(item.get("step", item.get("outcome", ""))),
                title=escape(item.get("title", item.get("person", ""))),
                body=escape(item.get("body", item.get("quote", ""))),
            )
        )
    return "".join(html)


def _pricing_cards():
    cards = []
    for plan_key in ["free", "pro", "career_hunter", "offer_accelerator"]:
        plan = PLAN_CATALOG[plan_key]
        features = "".join(f"<li>{escape(feature)}</li>" for feature in plan["features"])
        featured = " featured-plan" if plan.get("featured") else ""
        annual = (
            "<p class='plan-note'>{}</p>".format(escape(plan.get("annual_note", "")))
            if plan.get("annual_note")
            else ""
        )
        cards.append(
            "<div class='pricing-card{featured}'>"
            "<div class='plan-name'>{name}</div>"
            "<div class='plan-price'>{price}<span>{cadence}</span></div>"
            "<p>{summary}</p>"
            "{annual}"
            "<ul>{features}</ul>"
            "<a class='plan-cta' href='#signup'>{cta}</a>"
            "</div>".format(
                featured=featured,
                name=escape(plan["name"]),
                price=escape(plan["price"]),
                cadence=escape(plan["cadence"]),
                summary=escape(plan["summary"]),
                annual=annual,
                features=features,
                cta=escape(plan["cta"]),
            )
        )
    return "".join(cards)


def _render_public_landing():
    """Render the public positioning and conversion page before auth."""
    _render_html(
        """
        <style>
        .trovly-public {
            color: #101418;
            font-family: Outfit, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .public-hero {
            border: 1px solid #dce4e8;
            border-radius: 8px;
            padding: 48px;
            background:
                radial-gradient(circle at 80% 0%, rgba(45, 212, 191, 0.14), transparent 34%),
                linear-gradient(135deg, #ffffff 0%, #f7faf9 52%, #eef6f2 100%);
            box-shadow: 0 22px 70px rgba(16, 24, 40, 0.08);
        }
        .hero-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
            gap: 32px;
            align-items: center;
        }
        .eyebrow {
            color: #087f5b;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .public-hero h1 {
            color: #101418 !important;
            font-size: clamp(44px, 7vw, 74px);
            line-height: 0.95;
            letter-spacing: 0 !important;
            margin: 12px 0 18px;
            background: none !important;
            -webkit-text-fill-color: #101418 !important;
        }
        .public-hero p {
            color: #43515c;
            font-size: 1.12rem;
            line-height: 1.65;
            max-width: 680px;
        }
        .hero-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin: 28px 0 10px;
        }
        .hero-actions a, .plan-cta {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            min-height: 44px;
            padding: 0 18px;
            text-decoration: none !important;
            font-weight: 700;
            border: 1px solid #101418;
        }
        .hero-actions .primary, .plan-cta {
            background: #101418;
            color: #ffffff !important;
        }
        .hero-actions .secondary {
            background: #ffffff;
            color: #101418 !important;
            border-color: #c9d5d8;
        }
        .proof-row, .logo-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 22px;
        }
        .proof-pill, .logo-pill {
            border: 1px solid #dce4e8;
            border-radius: 999px;
            background: rgba(255,255,255,0.76);
            color: #29343b;
            padding: 8px 12px;
            font-size: 0.86rem;
            font-weight: 600;
        }
        .match-console {
            background: #101418;
            color: #f7faf9;
            border-radius: 8px;
            padding: 22px;
            border: 1px solid #2b3840;
            box-shadow: 0 18px 60px rgba(16, 20, 24, 0.22);
        }
        .console-top {
            display: flex;
            justify-content: space-between;
            color: #9fb2bb;
            font-size: 0.82rem;
            margin-bottom: 16px;
        }
        .score-card {
            background: #172027;
            border: 1px solid #273842;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .score-line {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            font-weight: 700;
        }
        .score-line span:last-child { color: #2dd4bf; }
        .score-card p {
            color: #b8c7cc;
            margin: 8px 0 0;
            font-size: 0.92rem;
            line-height: 1.45;
        }
        .progress {
            height: 7px;
            background: #26333b;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 12px;
        }
        .progress div {
            height: 100%;
            background: linear-gradient(90deg, #2dd4bf, #a3e635);
            border-radius: 999px;
        }
        .section {
            padding: 46px 0 0;
        }
        .section h2 {
            color: #101418 !important;
            font-size: clamp(28px, 4vw, 42px);
            margin-bottom: 10px;
        }
        .section-lead {
            color: #52616b;
            max-width: 760px;
            line-height: 1.65;
        }
        .card-grid, .pricing-grid, .story-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 22px;
        }
        .feature-card, .how-card, .story-card, .testimonial-card, .pricing-card, .faq-card {
            border: 1px solid #dce4e8;
            border-radius: 8px;
            background: #ffffff;
            padding: 18px;
            box-shadow: 0 10px 34px rgba(16, 24, 40, 0.05);
        }
        .feature-card h3, .how-card h3, .story-card h3, .testimonial-card h3, .pricing-card h3 {
            color: #101418 !important;
            margin: 6px 0 8px;
            font-size: 1.05rem;
        }
        .feature-card p, .how-card p, .story-card p, .testimonial-card p, .pricing-card p, .faq-card p {
            color: #52616b;
            line-height: 1.55;
            margin: 0;
        }
        .card-kicker, .plan-name {
            color: #087f5b;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .resume-example {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin-top: 22px;
        }
        .resume-box {
            border: 1px solid #dce4e8;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
        }
        .resume-box strong { color: #101418; }
        .resume-box p { color: #52616b; line-height: 1.6; }
        .pricing-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .pricing-card {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .featured-plan {
            border-color: #2dd4bf;
            box-shadow: 0 18px 44px rgba(45, 212, 191, 0.16);
        }
        .plan-price {
            color: #101418;
            font-size: 2rem;
            font-weight: 800;
        }
        .plan-price span {
            color: #52616b;
            font-size: 0.9rem;
            font-weight: 600;
            margin-left: 6px;
        }
        .plan-note {
            color: #087f5b !important;
            font-weight: 700;
        }
        .pricing-card ul {
            padding-left: 18px;
            color: #29343b;
            line-height: 1.7;
            flex: 1;
        }
        .faq-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
            margin-top: 22px;
        }
        .faq-card h3 {
            color: #101418 !important;
            margin: 0 0 8px;
            font-size: 1rem;
        }
        .cta-band {
            margin-top: 36px;
            border-radius: 8px;
            padding: 28px;
            background: #101418;
            color: #ffffff;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
        }
        .cta-band h2 {
            color: #ffffff !important;
            margin: 0;
            font-size: 2rem;
        }
        .cta-band p {
            color: #c8d5da;
            margin: 8px 0 0;
        }
        .cta-band a {
            background: #2dd4bf;
            color: #101418 !important;
            border-radius: 8px;
            padding: 12px 16px;
            text-decoration: none !important;
            font-weight: 800;
            white-space: nowrap;
        }
        @media (max-width: 900px) {
            .public-hero { padding: 28px; }
            .hero-grid, .resume-example, .faq-grid { grid-template-columns: 1fr; }
            .card-grid, .pricing-grid, .story-grid { grid-template-columns: 1fr; }
            .cta-band { align-items: flex-start; flex-direction: column; }
        }
        </style>
        """
    )

    proof = "".join(f"<span class='proof-pill'>{escape(item)}</span>" for item in SOCIAL_PROOF)
    logos = "".join(f"<span class='logo-pill'>{escape(item)}</span>" for item in COMPANY_LOGOS)
    how_cards = _cards(HOW_IT_WORKS, "how-card")
    feature_cards = _cards(FEATURE_GRID, "feature-card")
    testimonial_cards = _cards(TESTIMONIALS, "testimonial-card")
    story_cards = "".join(
        "<div class='story-card'>"
        "<div class='card-kicker'>{metric}</div>"
        "<h3>{title}</h3>"
        "<p><strong>Before:</strong> {before}</p>"
        "<p><strong>After:</strong> {after}</p>"
        "</div>".format(
            metric=escape(story["metric"]),
            title=escape(story["title"]),
            before=escape(story["before"]),
            after=escape(story["after"]),
        )
        for story in SUCCESS_STORIES
    )
    faq_cards = "".join(
        "<div class='faq-card'><h3>{}</h3><p>{}</p></div>".format(
            escape(item["q"]),
            escape(item["a"]),
        )
        for item in FAQS
    )

    _render_html(
        """
        <div class='trovly-public'>
            <section class='public-hero'>
                <div class='hero-grid'>
                    <div>
                        <div class='eyebrow'>{eyebrow}</div>
                        <h1>{headline}</h1>
                        <p>{subheadline}</p>
                        <div class='hero-actions'>
                            <a class='primary' href='#signup'>{primary_cta}</a>
                            <a class='secondary' href='#pricing'>See pricing</a>
                        </div>
                        <p>{proof_line}</p>
                        <div class='proof-row'>{proof}</div>
                    </div>
                    <div class='match-console'>
                        <div class='console-top'><span>Match engine preview</span><span>Live role scoring</span></div>
                        <div class='score-card'>
                            <div class='score-line'><span>Senior Cloud Platform Engineer</span><span>86%</span></div>
                            <p>Strong AWS, Terraform, Kubernetes, and reliability overlap. Interview likelihood: 68%.</p>
                            <div class='progress'><div style='width:86%'></div></div>
                        </div>
                        <div class='score-card'>
                            <div class='score-line'><span>Remote DevSecOps Engineer</span><span>79%</span></div>
                            <p>Salary aligned. Missing emphasis: threat detection, policy automation, SAST tooling.</p>
                            <div class='progress'><div style='width:79%'></div></div>
                        </div>
                        <div class='score-card'>
                            <div class='score-line'><span>AI Infrastructure Engineer</span><span>72%</span></div>
                            <p>Promising fit. Tailor resume around Python, embeddings, APIs, and production ML systems.</p>
                            <div class='progress'><div style='width:72%'></div></div>
                        </div>
                    </div>
                </div>
            </section>

            <section class='section'>
                <div class='eyebrow'>Trusted career signal</div>
                <h2>Built for the tech candidates chasing better compensation, not more busywork.</h2>
                <p class='section-lead'>Trovly focuses the search around roles where your resume, salary target, seniority, and remote preferences actually line up.</p>
                <div class='logo-row'>{logos}</div>
            </section>

            <section class='section'>
                <div class='eyebrow'>How it works</div>
                <h2>From resume to targeted applications in minutes.</h2>
                <div class='card-grid'>{how_cards}</div>
            </section>

            <section class='section'>
                <div class='eyebrow'>Premium copilot features</div>
                <h2>Everything needed to turn high-fit jobs into interviews.</h2>
                <div class='card-grid'>{feature_cards}</div>
            </section>

            <section class='section'>
                <div class='eyebrow'>Resume optimization example</div>
                <h2>Less generic. More role-specific proof.</h2>
                <div class='resume-example'>
                    <div class='resume-box'>
                        <strong>Before</strong>
                        <p>Responsible for cloud deployments and helped improve infrastructure processes.</p>
                    </div>
                    <div class='resume-box'>
                        <strong>After</strong>
                        <p>Designed Terraform-backed AWS deployment workflows that reduced release time by 60% while improving reliability across production services.</p>
                    </div>
                </div>
            </section>

            <section class='section'>
                <div class='eyebrow'>Results</div>
                <h2>Salary-focused search stories.</h2>
                <div class='story-grid'>{story_cards}</div>
            </section>

            <section class='section'>
                <div class='eyebrow'>What users say</div>
                <h2>Sharper targeting, faster interviews.</h2>
                <div class='card-grid'>{testimonial_cards}</div>
            </section>

            <section id='pricing' class='section'>
                <div class='eyebrow'>Pricing</div>
                <h2>Pick the level of acceleration you need.</h2>
                <div class='pricing-grid'>{pricing_cards}</div>
            </section>

            <section class='section'>
                <div class='eyebrow'>FAQ</div>
                <h2>Built for serious tech searches.</h2>
                <div class='faq-grid'>{faq_cards}</div>
            </section>

            <div class='cta-band'>
                <div>
                    <h2>Stop applying blindly.</h2>
                    <p>Run a focused career scan and see which roles deserve your next tailored application.</p>
                </div>
                <a href='#signup'>Create your free account</a>
            </div>
        </div>
        """.format(
            eyebrow=escape(HOMEPAGE_COPY["eyebrow"]),
            headline=escape(HOMEPAGE_COPY["headline"]),
            subheadline=escape(HOMEPAGE_COPY["subheadline"]),
            primary_cta=escape(HOMEPAGE_COPY["primary_cta"]),
            proof_line=escape(HOMEPAGE_COPY["proof"]),
            proof=proof,
            logos=logos,
            how_cards=how_cards,
            feature_cards=feature_cards,
            story_cards=story_cards,
            testimonial_cards=testimonial_cards,
            pricing_cards=_pricing_cards(),
            faq_cards=faq_cards,
        )
    )


def login_page():
    """Render login/register page."""
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return st.session_state.username

    _render_public_landing()

    st.markdown("<div id='signup'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.25, 1])

    with col2:
        st.markdown(
            """
        <div style='text-align:center; padding: 2rem 0 1rem;'>
            <div style='width: 64px; height: 64px; margin: 0 auto 16px; background: #101418; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-family: Outfit, sans-serif; font-weight: 800; font-size: 34px; box-shadow: 0 10px 28px rgba(16, 24, 40, 0.18);'>T</div>
            <h1 style='font-family: Outfit, sans-serif; font-weight: 800; font-size: 36px; margin: 0; color:#101418;'>Trovly AI</h1>
            <p style='color:#52616b; margin-top: 8px; letter-spacing: 0.05em;'>CAREER COPILOT FOR $150K+ TECH ROLES</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        tab_login, tab_register, tab_recover = st.tabs(["Log in", "Sign up", "Recover"])

        with tab_login:
            login_user = st.text_input("Username", key="login_user", max_chars=32)
            login_pass = st.text_input("Password", type="password", key="login_pass", max_chars=128)

            if st.button("Log in", type="primary", use_container_width=True):
                success, msg = check_credentials(login_user.strip(), login_pass)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = login_user.strip()
                    track_event(login_user.strip(), "login_completed")
                    st.rerun()
                else:
                    st.error(msg)

        with tab_register:
            reg_user = st.text_input(
                "Username",
                key="reg_user",
                max_chars=32,
                help="3-32 characters. Letters, numbers, underscores, hyphens only.",
            )
            reg_email = st.text_input("Email", key="reg_email", max_chars=254)
            reg_pass = st.text_input(
                "Password",
                type="password",
                key="reg_pass",
                max_chars=128,
                help="At least 12 characters with 3 of: uppercase, lowercase, numbers, symbols",
            )
            reg_pass2 = st.text_input(
                "Confirm password", type="password", key="reg_pass2", max_chars=128
            )

            if st.button("Create account", type="primary", use_container_width=True):
                if reg_pass != reg_pass2:
                    st.error("Passwords don't match")
                else:
                    success, msg = register_user(reg_user, reg_pass, reg_email)
                    if success:
                        # Auto-login: drop the user straight into their profile
                        # instead of forcing a manual sign-in.
                        canonical_username = reg_user.strip()
                        st.session_state.authenticated = True
                        st.session_state.username = canonical_username
                        # Stamp last_login + clear any failed-attempt counter,
                        # mirroring what check_credentials does on a real login.
                        reset_failed_attempts(canonical_username)
                        track_event(canonical_username, "signup_completed", {"tier": "free"})
                        st.toast(
                            f"Welcome to Trovly, {canonical_username}.",
                        )
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_recover:
            recovery_mode = st.radio(
                "Recovery option",
                ["Find username", "Reset password"],
                horizontal=True,
                key="recovery_mode",
            )

            if recovery_mode == "Find username":
                recovery_email = st.text_input(
                    "Account email",
                    key="recover_username_email",
                    max_chars=254,
                )

                if st.button("Find username", use_container_width=True):
                    success, msg, recovered_username = find_username_by_email(recovery_email)
                    if success:
                        st.success(f"Username: {recovered_username}")
                    else:
                        st.error(msg)
            else:
                reset_user = st.text_input("Username", key="reset_user", max_chars=32)
                reset_email = st.text_input("Account email", key="reset_email", max_chars=254)
                reset_pass = st.text_input(
                    "New password",
                    type="password",
                    key="reset_pass",
                    max_chars=128,
                    help="At least 12 characters with 3 of: uppercase, lowercase, numbers, symbols",
                )
                reset_pass2 = st.text_input(
                    "Confirm new password",
                    type="password",
                    key="reset_pass2",
                    max_chars=128,
                )

                if st.button("Reset password", type="primary", use_container_width=True):
                    if reset_pass != reset_pass2:
                        st.error("Passwords don't match")
                    else:
                        success, msg = reset_password(reset_user.strip(), reset_email, reset_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

    return None


def logout():
    """Clear session state."""
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.rerun()
