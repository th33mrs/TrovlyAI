"""
Trovly - Hosted App
Run with: streamlit run app_hosted.py
"""

from datetime import datetime, timezone
from html import escape

import streamlit as st

from analytics import (
    get_funnel_metrics,
    get_retention_metrics,
    track_event,
    user_career_metrics,
)
from applications import (
    STATUS_OPTIONS,
    add_application,
    delete_application,
    get_follow_ups,
    get_stats,
    list_applications,
    update_application,
)
from auth import get_user_data, login_page, logout, save_user_data
from auto_apply import (
    ACTIVE_QUEUE_STATUSES,
    DEFAULT_AUTO_APPLY_SETTINGS,
    enqueue_matches,
    list_queue,
    update_queue_item,
    validate_application_profile,
    weekly_progress,
)
from auto_apply import (
    normalize_settings as normalize_auto_apply_settings,
)
from job_intelligence import (
    build_match_intelligence,
    build_responsiveness_intelligence,
    cover_letter_outline,
    rank_responsive_targets,
    resume_strength_score,
)
from notification_engine import (
    DEFAULT_ALERT_PREFS,
    build_alert_message,
    normalize_alert_preferences,
)
from product_strategy import (
    ALERT_CHANNELS,
    B2B_PLANS,
    HOMEPAGE_COPY,
    ONBOARDING_PRESETS,
    PLAN_CATALOG,
    SEO_CATEGORIES,
    UPGRADE_PROMPTS,
)
from resume_parser import parse_resume_file
from tracker import JobTracker
from usage_limits import (
    can_scan,
    can_tailor,
    get_usage_summary,
    get_user_tier,
    increment_scans,
    increment_tailors,
)

UTC = timezone.utc  # noqa: UP017 - Python 3.10 does not provide datetime.UTC.

st.set_page_config(
    page_title="Trovly",
    page_icon="mag",
    layout="wide",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
    --ink: #101418;
    --ink-soft: #29343b;
    --muted: #52616b;
    --line: #dce4e8;
    --panel: #ffffff;
    --page: #f7faf9;
    --teal: #2dd4bf;
    --green: #087f5b;
    --lime: #a3e635;
    --blue: #2563eb;
}

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    background: var(--page);
}

.main .block-container {
    padding-top: 1.5rem;
    max-width: 1240px;
}

h1, h2, h3 {
    font-weight: 800 !important;
    letter-spacing: 0 !important;
    color: var(--ink) !important;
}

p, li, label {
    color: var(--ink-soft);
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--ink) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: 1px solid var(--ink) !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 24px rgba(16, 24, 40, 0.12) !important;
    transition: transform 0.15s, box-shadow 0.2s !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 14px 34px rgba(16, 24, 40, 0.18) !important;
}

.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
    background: #ffffff !important;
    color: var(--ink) !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]):hover {
    border-color: var(--teal) !important;
    color: var(--green) !important;
}

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid var(--line);
    border-left: 3px solid var(--teal);
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 10px 30px rgba(16, 24, 40, 0.05);
}

div[data-testid="stMetric"] label {
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--ink) !important;
    font-weight: 800 !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    border-bottom: 1px solid var(--line);
}

.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    font-weight: 700 !important;
}

.stTabs [aria-selected="true"] {
    color: var(--green) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background: linear-gradient(90deg, var(--teal), var(--lime)) !important;
    height: 3px !important;
}

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid var(--line);
}

section[data-testid="stSidebar"] .stMarkdown h2 {
    color: var(--ink) !important;
    font-size: 28px !important;
}

div[data-testid="stAlert"] {
    border-radius: 8px;
    border-width: 1px;
}

.stSlider [role="slider"] {
    background: var(--teal) !important;
    border-color: var(--teal) !important;
}

.stTextInput input, .stTextArea textarea {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    color: var(--ink) !important;
    border-radius: 8px !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 1px var(--teal) !important;
}

.streamlit-expanderHeader {
    background: #ffffff !important;
    border: 1px solid var(--line) !important;
    border-radius: 8px !important;
    border-left: 3px solid var(--teal) !important;
}

[data-testid="stFileUploadDropzone"] {
    background: #ffffff !important;
    border: 2px dashed var(--line) !important;
    border-radius: 8px !important;
}

[data-testid="stFileUploadDropzone"]:hover {
    border-color: var(--teal) !important;
    background: #f3fbf8 !important;
}

.stSelectbox [data-baseweb="select"] {
    background: #ffffff !important;
    border-color: var(--line) !important;
}

a {
    color: var(--green) !important;
}

a:hover {
    color: var(--blue) !important;
}

.app-hero, .premium-panel, .pricing-panel {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 22px;
    box-shadow: 0 12px 36px rgba(16, 24, 40, 0.05);
}

.app-hero {
    background:
        radial-gradient(circle at 90% 10%, rgba(45, 212, 191, 0.18), transparent 28%),
        linear-gradient(135deg, #ffffff 0%, #f7faf9 100%);
}

.eyebrow {
    color: var(--green);
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 10px;
}

.mini-pill {
    display: inline-flex;
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 6px 10px;
    background: #ffffff;
    color: var(--ink-soft);
    font-size: 0.82rem;
    font-weight: 700;
}

.match-card {
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 16px;
    background: #ffffff;
    margin: 10px 0;
}

.match-header {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: flex-start;
}

.match-score {
    min-width: 72px;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    background: #101418;
    color: #ffffff;
    font-weight: 800;
}

.copy-card {
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 14px;
    background: #f7faf9;
    min-height: 110px;
}
</style>
""",
    unsafe_allow_html=True,
)

username = login_page()

if username is None:
    st.stop()

user_data = get_user_data(username)
is_admin = bool(user_data.get("is_admin")) or user_data.get("role") == "admin"
auto_apply_settings = normalize_auto_apply_settings(
    user_data.get("auto_apply_settings", DEFAULT_AUTO_APPLY_SETTINGS)
)
application_profile = {
    "full_name": "",
    "email": user_data.get("email", ""),
    "phone": "",
    "location": "",
    "work_authorization": "",
    "linkedin_url": "",
    "portfolio_url": "",
    **user_data.get("application_profile", {}),
}
tier = get_user_tier(user_data)
summary = get_usage_summary(username, tier)
tracker = JobTracker()
tracked_jobs = tracker.get_all()
application_stats = get_stats(username)
application_records = list_applications(username)
career_metrics = user_career_metrics(username, application_stats, tracked_jobs)
resume_strength = resume_strength_score(user_data.get("resume", ""))
stored_responsive_targets = rank_responsive_targets(
    tracked_jobs + application_records,
    applications=application_records,
)


def _pill_row(items):
    if not items:
        return ""
    return "<div class='pill-row'>{}</div>".format(
        "".join(f"<span class='mini-pill'>{escape(str(item))}</span>" for item in items)
    )


def _upgrade_intent(plan_key, source):
    save_user_data(
        username,
        {
            "checkout_intent": {
                "plan": plan_key,
                "source": source,
            }
        },
    )
    track_event(username, "upgrade_intent", {"plan": plan_key, "source": source})
    st.success("Upgrade intent saved. Connect Stripe Checkout to turn this into a paid conversion.")


def _render_plan(plan_key, current_tier):
    plan = PLAN_CATALOG[plan_key]
    st.markdown(
        """
        <div class='pricing-panel'>
            <div class='eyebrow'>{name}</div>
            <h2>{price} <span style='font-size:0.9rem;color:#52616b'>{cadence}</span></h2>
            <p>{summary}</p>
        </div>
        """.format(
            name=escape(plan["name"]),
            price=escape(plan["price"]),
            cadence=escape(plan["cadence"]),
            summary=escape(plan["summary"]),
        ),
        unsafe_allow_html=True,
    )
    for feature in plan["features"]:
        st.markdown(f"- {feature}")
    disabled = current_tier == plan_key or plan_key == "free"
    if st.button(plan["cta"], key=f"upgrade_{plan_key}", disabled=disabled):
        _upgrade_intent(plan_key, "pricing")


def _run_match_pipeline():
    import config_runtime as config
    from matcher import match_jobs, reload_resume
    from sources import fetch_all_jobs

    config.RESUME_TEXT = user_data.get("resume", "")
    config.SEARCH_QUERIES = user_data.get("queries", [])
    config.SIMILARITY_THRESHOLD = user_data.get("threshold", 0.55)
    config.REMOTE_ONLY = user_data.get("remote_only", True)
    config.SALARY_FLOOR = int(user_data.get("target_salary", 150000) * 0.85)

    reload_resume()
    jobs = fetch_all_jobs()
    matched = match_jobs(jobs)
    return jobs, matched


def _visible_matches(matched):
    max_matches = summary.get("max_matches_per_scan", -1)
    return matched if max_matches == -1 else matched[:max_matches]


def _activate_auto_apply_now(settings):
    jobs, matched = _run_match_pipeline()
    visible_matches = _visible_matches(matched)
    queue_result = enqueue_matches(
        username,
        visible_matches,
        settings=settings,
        existing_applications=list_applications(username),
    )
    st.session_state["responsive_targets"] = rank_responsive_targets(
        visible_matches,
        applications=list_applications(username),
    )
    result = {
        **queue_result,
        "fetched_count": len(jobs),
        "matched_count": len(matched),
        "evaluated_count": len(visible_matches),
    }
    track_event(
        username,
        "auto_apply_immediate_activation",
        {
            "fetched": result["fetched_count"],
            "matched": result["matched_count"],
            "evaluated": result["evaluated_count"],
            "queued": result["queued_count"],
            "skipped": result["skipped_count"],
            "duplicates": result["duplicates"],
        },
    )
    return result


def _store_auto_apply_notice(result):
    st.session_state["auto_apply_notice"] = {
        "fetched_count": result["fetched_count"],
        "matched_count": result["matched_count"],
        "evaluated_count": result["evaluated_count"],
        "queued_count": result["queued_count"],
        "skipped_count": result["skipped_count"],
        "duplicates": result["duplicates"],
        "skipped": result["skipped"][:3],
    }


with st.sidebar:
    st.markdown("## Trovly AI")
    st.caption(f"Logged in as {username}")
    if is_admin:
        st.caption("Admin access")
    st.markdown("---")

    st.markdown("**Plan:** {}".format(summary["tier_label"]))
    if summary.get("tier_price"):
        st.caption(summary["tier_price"])

    if tier == "free":
        if summary["scans_remaining"] == 0:
            st.error("Scans: {} / {}".format(summary["scans_used"], summary["scans_limit"]))
        else:
            st.info("Scans: {} / {}".format(summary["scans_used"], summary["scans_limit"]))
        st.caption(
            "Resume analyses: {} / {}".format(summary["tailors_used"], summary["tailors_limit"])
        )
        prompt = UPGRADE_PROMPTS["scan_limit"]
        st.markdown("**{}**".format(prompt["headline"]))
        st.caption(prompt["body"])
        if st.button(prompt["cta"], key="sidebar_upgrade"):
            _upgrade_intent("pro", "sidebar")
    else:
        st.success("Premium career acceleration active")

    st.markdown("---")
    st.metric("Resume strength", "{}%".format(resume_strength["score"]))
    st.caption(resume_strength["level"])
    st.metric("Match quality", "{}%".format(career_metrics["match_quality"]))
    st.markdown("---")
    if st.button("Log out"):
        logout()


st.markdown(
    """
    <div class='app-hero'>
        <div class='eyebrow'>{eyebrow}</div>
        <h1>{headline}</h1>
        <p>{subheadline}</p>
        {roles}
    </div>
    """.format(
        eyebrow=escape(HOMEPAGE_COPY["eyebrow"]),
        headline=escape("Your Command Center for $150k+ Tech Roles"),
        subheadline=escape(
            "Track match quality, resume readiness, alerts, applications, and upgrade paths from one revenue-focused career workspace."
        ),
        roles=_pill_row(
            user_data.get("target_roles") or ["Cloud", "DevOps", "AI", "Security", "Remote"]
        ),
    ),
    unsafe_allow_html=True,
)

tab_labels = [
    "Command Center",
    "Onboarding",
    "Match Scan",
    "Auto Apply",
    "Responsive Targets",
    "Resume AI",
    "Applications",
    "Alerts",
    "Pricing",
]
if is_admin:
    tab_labels.append("Analytics")
tab_labels.append("Recruiter Mode")

tab_map = dict(zip(tab_labels, st.tabs(tab_labels), strict=False))
tab_dashboard = tab_map["Command Center"]
tab_setup = tab_map["Onboarding"]
tab_scan = tab_map["Match Scan"]
tab_auto_apply = tab_map["Auto Apply"]
tab_targets = tab_map["Responsive Targets"]
tab_tailor = tab_map["Resume AI"]
tab_apps = tab_map["Applications"]
tab_alerts = tab_map["Alerts"]
tab_pricing = tab_map["Pricing"]
tab_admin = tab_map.get("Analytics")
tab_recruiter = tab_map["Recruiter Mode"]

with tab_dashboard:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Interviews generated", career_metrics["interviews_generated"])
    with col2:
        st.metric("Applications saved", career_metrics["applications_saved"])
    with col3:
        st.metric(
            "Estimated salary uplift", "${:,}".format(career_metrics["estimated_salary_uplift"])
        )
    with col4:
        st.metric("Readiness level", resume_strength["level"])

    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("### Career acceleration signals")
        st.markdown(
            """
            <div class='premium-panel'>
                <div class='eyebrow'>Retention widget</div>
                <h3>Weekly focus</h3>
                <p>Prioritize roles above your match threshold, tailor every high-fit application, and follow up on active opportunities older than 7 days.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for action in resume_strength["next_actions"]:
            st.markdown(f"- {action}")

        st.markdown("### Top companies matching you")
        companies = [job.get("company", "Unknown") for job in tracked_jobs[:8]]
        if companies:
            st.markdown(_pill_row(companies), unsafe_allow_html=True)
        else:
            st.info("Run your first scan to populate company fit signals.")

        st.markdown("### Companies likely to respond")
        responsive_companies = [target["company"] for target in stored_responsive_targets[:6]]
        if responsive_companies:
            st.markdown(_pill_row(responsive_companies), unsafe_allow_html=True)
        else:
            st.info("Track applications or run a scan to build responsiveness signals.")

    with right:
        st.markdown("### Growth loops")
        readiness_level = "Offer-ready" if resume_strength["score"] >= 85 else "Building momentum"
        st.markdown(
            """
            <div class='copy-card'>
                <strong>Shareable career insight</strong>
                <p>{user} is {level} for {roles}. Resume strength: {score}%.</p>
            </div>
            """.format(
                user=escape(username),
                level=escape(readiness_level),
                roles=escape(
                    ", ".join(user_data.get("target_roles") or ["high-paying tech roles"])
                ),
                score=resume_strength["score"],
            ),
            unsafe_allow_html=True,
        )
        st.caption("Referral rewards: 1 free premium tailoring pack per qualified invite.")
        st.caption(
            "LinkedIn share card: Top companies matching you, resume strength, and salary target."
        )

with tab_setup:
    st.markdown("### Onboarding for higher-paying tech roles")
    st.markdown(
        "Set the ICP, salary target, and role lane so every scan is aimed at interviews and offers."
    )

    preset_names = list(ONBOARDING_PRESETS.keys())
    selected_preset = st.selectbox("Search strategy preset", preset_names)
    preset = ONBOARDING_PRESETS[selected_preset]

    uploaded_resume = st.file_uploader(
        "Upload resume (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"]
    )
    parsed_resume = None
    if uploaded_resume is not None:
        ok, parsed_or_error = parse_resume_file(uploaded_resume.getvalue(), uploaded_resume.name)
        if ok:
            parsed_resume = parsed_or_error
            st.success("Resume parsed. Review the extracted text below before saving.")
        else:
            st.error(parsed_or_error)

    resume = st.text_area(
        "Resume",
        value=parsed_resume if parsed_resume else user_data.get("resume", ""),
        height=300,
        placeholder="Paste your full resume here. Include measurable outcomes, tools, systems, and seniority signals.",
    )

    default_queries = user_data.get("queries") or preset["queries"]
    queries_str = st.text_area(
        "Target roles (one per line)",
        value="\n".join(default_queries),
        height=150,
        placeholder="senior cloud engineer\nplatform engineer\nremote devops engineer",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        threshold = st.slider(
            "Match threshold",
            0.3,
            0.95,
            float(user_data.get("threshold", preset["threshold"])),
            0.05,
            format="%.0f%%",
        )
    with col2:
        target_salary = st.number_input(
            "Target salary",
            min_value=80000,
            max_value=300000,
            value=int(user_data.get("target_salary", preset["target_salary"])),
            step=5000,
        )
    with col3:
        remote_only = st.checkbox(
            "Remote-first search",
            value=user_data.get("remote_only", True),
        )

    target_roles = st.multiselect(
        "Primary career lanes",
        options=["Cloud", "DevOps", "Platform", "SRE", "AI", "Cybersecurity", "Remote"],
        default=user_data.get("target_roles") or [selected_preset.split(" / ")[0]],
    )

    if st.button("Save career profile", type="primary"):
        queries_list = [q.strip() for q in queries_str.strip().split("\n") if q.strip()]
        save_user_data(
            username,
            {
                "resume": resume,
                "queries": queries_list,
                "threshold": threshold,
                "remote_only": remote_only,
                "target_salary": target_salary,
                "target_roles": target_roles,
                "onboarding_completed": True,
            },
        )
        track_event(
            username,
            "profile_saved",
            {
                "queries": len(queries_list),
                "target_salary": target_salary,
                "target_roles": target_roles,
                "resume_chars": len(resume),
            },
        )
        st.success("Career profile saved. Your scans are now salary- and role-targeted.")
        st.rerun()

with tab_scan:
    st.markdown("### Match scan")
    st.markdown("Find roles that deserve a tailored application, not just another blind submit.")

    if not user_data.get("resume"):
        st.warning("Complete onboarding first so Trovly can compare jobs against your resume.")
    else:
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Resume loaded", "{} chars".format(len(user_data.get("resume", ""))))
        with col_b:
            st.metric("Match threshold", "{:.0%}".format(user_data.get("threshold", 0.55)))
        with col_c:
            st.metric("Salary target", "${:,}".format(int(user_data.get("target_salary", 150000))))

        if st.button("Run high-fit scan", type="primary"):
            allowed, msg = can_scan(username, tier)
            if not allowed:
                st.error(msg)
                prompt = UPGRADE_PROMPTS["scan_limit"]
                st.info("{} {}".format(prompt["headline"], prompt["body"]))
                st.stop()
            increment_scans(username)
            with st.spinner(
                "Scanning fresh roles, scoring fit, salary, gaps, and interview likelihood..."
            ):
                try:
                    jobs, matched = _run_match_pipeline()
                    track_event(
                        username,
                        "scan_completed",
                        {"fetched": len(jobs), "matched": len(matched), "tier": tier},
                    )

                    if matched:
                        st.success(f"Found {len(matched)} matches worth reviewing.")
                        max_matches = summary.get("max_matches_per_scan", -1)
                        visible_matches = _visible_matches(matched)
                        if auto_apply_settings["enabled"] and auto_apply_settings["consent"]:
                            queue_result = enqueue_matches(
                                username,
                                visible_matches,
                                settings=auto_apply_settings,
                                existing_applications=application_records,
                            )
                            track_event(
                                username,
                                "auto_apply_matches_evaluated",
                                {
                                    "queued": queue_result["queued_count"],
                                    "skipped": queue_result["skipped_count"],
                                    "duplicates": queue_result["duplicates"],
                                },
                            )
                            if queue_result["queued_count"]:
                                st.info(
                                    "Auto Apply queued {} eligible role{} for submission.".format(
                                        queue_result["queued_count"],
                                        "" if queue_result["queued_count"] == 1 else "s",
                                    )
                                )
                        st.session_state["responsive_targets"] = rank_responsive_targets(
                            visible_matches,
                            applications=application_records,
                        )
                        if max_matches != -1 and len(matched) > max_matches:
                            st.info(
                                f"Free plan shows your top {max_matches} matches. Upgrade to unlock the full list."
                            )

                        for idx, (job, score) in enumerate(visible_matches):
                            intelligence = build_match_intelligence(
                                job,
                                score,
                                resume_text=user_data.get("resume", ""),
                                target_salary=int(user_data.get("target_salary", 150000)),
                            )
                            responsiveness = build_responsiveness_intelligence(
                                job,
                                score,
                                applications=application_records,
                                peer_jobs=visible_matches,
                            )
                            with st.expander(
                                "{}% match - {} at {}".format(
                                    intelligence["match_percent"],
                                    job.title,
                                    job.company,
                                ),
                                expanded=idx < 2,
                            ):
                                st.markdown(
                                    """
                                    <div class='match-card'>
                                        <div class='match-header'>
                                            <div>
                                                <div class='eyebrow'>{source}</div>
                                                <h3>{title} at {company}</h3>
                                                <p>{urgency}</p>
                                            </div>
                                            <div class='match-score'>{score}%</div>
                                        </div>
                                    </div>
                                    """.format(
                                        source=escape(job.source),
                                        title=escape(job.title),
                                        company=escape(job.company),
                                        urgency=escape(intelligence["urgency"]),
                                        score=intelligence["match_percent"],
                                    ),
                                    unsafe_allow_html=True,
                                )
                                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                                with col_m1:
                                    st.metric(
                                        "Interview likelihood",
                                        "{}%".format(intelligence["interview_probability"]),
                                    )
                                with col_m2:
                                    st.metric(
                                        "Readiness score",
                                        "{}%".format(intelligence["readiness_score"]),
                                    )
                                with col_m3:
                                    salary_signal = intelligence["salary_competitiveness"]["label"]
                                    st.metric("Salary competitiveness", salary_signal)
                                with col_m4:
                                    st.metric(
                                        "Responsiveness",
                                        "{}%".format(responsiveness["score"]),
                                    )

                                if job.salary:
                                    st.markdown(f"**Salary:** {job.salary}")
                                st.markdown(
                                    "**Location:** {}".format(
                                        job.location or "Remote / not specified"
                                    )
                                )
                                st.markdown("**Why it fits**")
                                for reason in intelligence["why_fit"]:
                                    st.markdown(f"- {reason}")
                                st.markdown("**Why it may not**")
                                for reason in intelligence["why_not"]:
                                    st.markdown(f"- {reason}")
                                if intelligence["missing_skills"]:
                                    st.markdown(
                                        "**Missing skills:** {}".format(
                                            ", ".join(intelligence["missing_skills"])
                                        )
                                    )
                                if intelligence["matched_skills"]:
                                    st.markdown(
                                        "**Matched skills:** {}".format(
                                            ", ".join(intelligence["matched_skills"])
                                        )
                                    )

                                st.markdown("**Responsive targeting**")
                                st.markdown(
                                    "**{}:** {}".format(
                                        responsiveness["label"],
                                        responsiveness["action"],
                                    )
                                )
                                for reason in responsiveness["reasons"]:
                                    st.markdown(f"- {reason}")
                                for risk in responsiveness["risks"]:
                                    st.markdown(f"- Risk: {risk}")

                                st.markdown("**Who to target**")
                                st.markdown(
                                    _pill_row(responsiveness["recruiter_targets"]),
                                    unsafe_allow_html=True,
                                )
                                link_cols = st.columns(4)
                                for link_col, link in zip(
                                    link_cols,
                                    responsiveness["search_links"],
                                    strict=False,
                                ):
                                    with link_col:
                                        st.link_button(link["label"], link["url"])

                                with st.expander("Recruiter outreach draft", expanded=False):
                                    st.text_area(
                                        "Message",
                                        value=responsiveness["outreach_note"],
                                        height=120,
                                        key=f"outreach_{job.uid}",
                                    )

                                alert_payload = build_alert_message(
                                    job, intelligence, channel="email"
                                )
                                with st.expander("Alert copy preview", expanded=False):
                                    st.markdown("**{}**".format(alert_payload["subject"]))
                                    st.markdown(alert_payload["body"])

                                col_apply, col_track = st.columns(2)
                                with col_apply:
                                    if st.link_button("Apply", job.url):
                                        track_event(
                                            username,
                                            "job_apply_clicked",
                                            {"title": job.title, "company": job.company},
                                        )
                                with col_track:
                                    if st.button("Track application", key=f"track_{job.uid}"):
                                        success, app_msg, _ = add_application(
                                            username,
                                            job.title,
                                            job.company,
                                            url=job.url,
                                            location=job.location or "",
                                            salary=job.salary or "",
                                            source=job.source,
                                            notes=f"Matched at {score:.0%}",
                                        )
                                        if success:
                                            track_event(
                                                username,
                                                "application_tracked",
                                                {"source": "scan", "score": score},
                                            )
                                            st.success(app_msg)
                                        else:
                                            st.warning(app_msg)
                    else:
                        st.warning(
                            "No roles cleared your threshold. Try a lower threshold or broader target role list."
                        )

                except Exception as e:
                    st.error(f"Scan failed: {e}")

with tab_auto_apply:
    st.markdown("### Auto Apply control center")
    st.markdown(
        "Automatically queue fresh, high-fit roles immediately while keeping identity, legal, and screening answers under your control."
    )

    auto_apply_notice = st.session_state.pop("auto_apply_notice", None)
    if auto_apply_notice:
        if auto_apply_notice.get("message"):
            st.success(auto_apply_notice["message"])
        else:
            st.success(
                "Auto Apply is live. Scanned {fetched_count} jobs, found {matched_count} matches, evaluated {evaluated_count}, and queued {queued_count} eligible role{suffix} now.".format(
                    suffix="" if auto_apply_notice["queued_count"] == 1 else "s",
                    **auto_apply_notice,
                )
            )
        if auto_apply_notice["duplicates"]:
            st.info(
                "{} role{} already existed in the queue and was not duplicated.".format(
                    auto_apply_notice["duplicates"],
                    "" if auto_apply_notice["duplicates"] == 1 else "s",
                )
            )
        if auto_apply_notice["skipped_count"]:
            with st.expander("Why some roles were skipped", expanded=False):
                for skipped in auto_apply_notice["skipped"]:
                    st.markdown(
                        "**{} at {}**: {}".format(
                            skipped["title"] or "Untitled role",
                            skipped["company"] or "Unknown company",
                            "; ".join(skipped["blockers"]),
                        )
                    )

    auto_apply_error = st.session_state.pop("auto_apply_error", None)
    if auto_apply_error:
        st.error(auto_apply_error)

    progress = weekly_progress(username, auto_apply_settings)
    progress_columns = st.columns(5)
    progress_columns[0].metric(
        "Submitted this week",
        progress["submitted_this_week"],
        "Target {}".format(progress["weekly_target"]),
    )
    progress_columns[1].metric("Remaining", progress["remaining"])
    progress_columns[2].metric("Daily pace", progress["daily_pace"])
    progress_columns[3].metric("Queued", progress["queued"])
    progress_columns[4].metric("Needs review", progress["needs_review"])

    if progress["submitted_this_week"] < progress["weekly_target"]:
        available = progress["queued"] + progress["needs_review"]
        if available < progress["remaining"]:
            st.warning(
                "The current queue is {} roles short of the weekly target. Run fresh scans to add more eligible postings.".format(
                    progress["remaining"] - available
                )
            )
    else:
        st.success("Weekly application target reached. The hard cap still prevents runaway volume.")

    run_now_disabled = not (auto_apply_settings["enabled"] and auto_apply_settings["consent"])
    if st.button(
        "Run Auto Apply now",
        type="primary",
        disabled=run_now_disabled,
        help="Immediately scan fresh jobs and queue roles that clear your saved Auto Apply rules.",
    ):
        missing_profile = validate_application_profile(application_profile)
        if not user_data.get("resume"):
            st.error("Add a resume in Onboarding before running Auto Apply.")
        elif missing_profile:
            st.error("Complete: {}.".format(", ".join(missing_profile)))
        else:
            with st.spinner("Auto Apply is scanning and queueing eligible roles now..."):
                try:
                    activation_result = _activate_auto_apply_now(auto_apply_settings)
                    _store_auto_apply_notice(activation_result)
                    st.rerun()
                except Exception as e:
                    st.error(f"Immediate Auto Apply run failed: {e}")
    if run_now_disabled:
        st.caption("Enable Auto Apply, complete consent, and save settings to run it immediately.")

    st.markdown("#### Rules and safeguards")
    settings_left, settings_right = st.columns(2)
    with settings_left:
        auto_apply_enabled = st.toggle(
            "Enable Auto Apply",
            value=auto_apply_settings["enabled"],
            help="Eligible matches are queued immediately when saved, then after each future scan.",
        )
        auto_min_match_percent = st.slider(
            "Match score must be over",
            min_value=80,
            max_value=95,
            value=max(int(auto_apply_settings["min_match_score"] * 100), 80),
            step=1,
            format="%d%%",
            help="A score equal to the threshold does not qualify.",
        )
        max_post_age = st.number_input(
            "Maximum posting age in hours",
            min_value=1,
            max_value=72,
            value=auto_apply_settings["max_post_age_hours"],
            step=1,
        )
    with settings_right:
        weekly_target = st.number_input(
            "Weekly application target",
            min_value=50,
            max_value=500,
            value=auto_apply_settings["weekly_target"],
            step=25,
        )
        weekly_hard_cap = st.number_input(
            "Weekly hard cap",
            min_value=int(weekly_target),
            max_value=750,
            value=max(auto_apply_settings["weekly_hard_cap"], int(weekly_target)),
            step=25,
            help="Trovly never submits above this limit without a new setting change.",
        )
        daily_hard_cap = st.number_input(
            "Daily hard cap",
            min_value=10,
            max_value=100,
            value=auto_apply_settings["daily_hard_cap"],
            step=5,
        )

    excluded_keywords = st.text_input(
        "Never apply when the posting contains",
        value=", ".join(auto_apply_settings["excluded_keywords"]),
        placeholder="commission only, unpaid, active clearance required",
        help="Separate phrases with commas.",
    )

    st.markdown("#### Application identity")
    identity_left, identity_right = st.columns(2)
    with identity_left:
        full_name = st.text_input("Full legal name", value=application_profile["full_name"])
        application_email = st.text_input("Application email", value=application_profile["email"])
        phone = st.text_input("Phone", value=application_profile["phone"])
        location = st.text_input("Location", value=application_profile["location"])
    with identity_right:
        authorization_options = [
            "",
            "Authorized to work in the United States",
            "Requires employer sponsorship",
            "Review each application",
        ]
        saved_authorization = application_profile["work_authorization"]
        authorization_index = (
            authorization_options.index(saved_authorization)
            if saved_authorization in authorization_options
            else 0
        )
        work_authorization = st.selectbox(
            "Work authorization",
            authorization_options,
            index=authorization_index,
        )
        linkedin_url = st.text_input("LinkedIn URL", value=application_profile["linkedin_url"])
        portfolio_url = st.text_input("Portfolio URL", value=application_profile["portfolio_url"])

    consent = st.checkbox(
        "I confirm this information is accurate and authorize Trovly to submit applications that meet these rules.",
        value=auto_apply_settings["consent"],
    )
    st.caption(
        "Trovly never answers demographic questions, invents qualifications, bypasses CAPTCHAs, or counts an application without confirmation from the job site."
    )

    if st.button(
        "Save Auto Apply settings",
        type="primary",
        help="Save eligibility rules, identity, consent, and weekly limits.",
    ):
        updated_profile = {
            "full_name": full_name.strip(),
            "email": application_email.strip(),
            "phone": phone.strip(),
            "location": location.strip(),
            "work_authorization": work_authorization,
            "linkedin_url": linkedin_url.strip(),
            "portfolio_url": portfolio_url.strip(),
        }
        missing_profile = validate_application_profile(updated_profile)
        if auto_apply_enabled and not user_data.get("resume"):
            st.error("Add a resume in Onboarding before enabling Auto Apply.")
        elif auto_apply_enabled and missing_profile:
            st.error("Complete: {}.".format(", ".join(missing_profile)))
        elif auto_apply_enabled and not consent:
            st.error("Authorization is required before Auto Apply can be enabled.")
        else:
            updated_settings = normalize_auto_apply_settings(
                {
                    "enabled": auto_apply_enabled,
                    "min_match_score": auto_min_match_percent / 100,
                    "max_post_age_hours": int(max_post_age),
                    "weekly_target": int(weekly_target),
                    "weekly_hard_cap": int(weekly_hard_cap),
                    "daily_hard_cap": int(daily_hard_cap),
                    "consent": consent,
                    "consent_at": (
                        auto_apply_settings.get("consent_at") or datetime.now(UTC).isoformat()
                        if consent
                        else None
                    ),
                    "excluded_keywords": [
                        value.strip() for value in excluded_keywords.split(",") if value.strip()
                    ],
                }
            )
            save_user_data(
                username,
                {
                    "auto_apply_settings": updated_settings,
                    "application_profile": updated_profile,
                },
            )
            track_event(
                username,
                "auto_apply_settings_saved",
                {
                    "enabled": auto_apply_enabled,
                    "weekly_target": int(weekly_target),
                    "min_match_score": auto_min_match_percent / 100,
                },
            )
            if updated_settings["enabled"] and updated_settings["consent"]:
                with st.spinner("Auto Apply is taking effect immediately..."):
                    try:
                        activation_result = _activate_auto_apply_now(updated_settings)
                        _store_auto_apply_notice(activation_result)
                    except Exception as e:
                        st.session_state["auto_apply_error"] = (
                            f"Settings saved, but the immediate Auto Apply run failed: {e}"
                        )
            else:
                st.session_state["auto_apply_notice"] = {
                    "fetched_count": 0,
                    "matched_count": 0,
                    "evaluated_count": 0,
                    "queued_count": 0,
                    "skipped_count": 0,
                    "duplicates": 0,
                    "skipped": [],
                    "message": "Auto Apply settings saved.",
                }
            st.rerun()

    st.markdown("#### Submission queue")
    queue_filter = st.segmented_control(
        "Queue status",
        options=["Active", "Submitted", "Skipped", "All"],
        default="Active",
    )
    status_filters = {
        "Active": ACTIVE_QUEUE_STATUSES,
        "Submitted": {"submitted"},
        "Skipped": {"skipped"},
        "All": None,
    }
    queue_items = list_queue(username, status_filters.get(queue_filter))
    if not queue_items:
        st.info("No jobs in this queue yet. Enable Auto Apply and run a Match Scan.")
    else:
        st.dataframe(
            [
                {
                    "Status": item["status"].replace("_", " ").title(),
                    "Match": "{:.0%}".format(item["match_score"]),
                    "Role": item["title"],
                    "Company": item["company"],
                    "Age when queued": "{}h".format(item["age_hours_at_queue"]),
                    "Source": item["source"],
                }
                for item in queue_items
            ],
            use_container_width=True,
            hide_index=True,
        )
        selected_id = st.selectbox(
            "Manage queue item",
            options=[item["id"] for item in queue_items],
            format_func=lambda item_id: next(
                "{} at {}".format(item["title"], item["company"])
                for item in queue_items
                if item["id"] == item_id
            ),
        )
        selected_item = next(item for item in queue_items if item["id"] == selected_id)
        if selected_item.get("review_reason"):
            st.warning(selected_item["review_reason"])
        action_open, action_submit, action_skip = st.columns(3)
        with action_open:
            st.link_button(
                "Open application",
                selected_item["url"],
                help="Open the employer application page in a new tab.",
                use_container_width=True,
            )
        with action_submit:
            if st.button(
                "Confirm submitted",
                help="Use only after the employer confirms the application.",
                use_container_width=True,
            ):
                update_queue_item(username, selected_id, "submitted")
                add_application(
                    username,
                    selected_item["title"],
                    selected_item["company"],
                    url=selected_item["url"],
                    location=selected_item["location"],
                    salary=selected_item["salary"],
                    source="auto-apply: {}".format(selected_item["source"]),
                    notes="Confirmed from Auto Apply at {:.0%} match".format(
                        selected_item["match_score"]
                    ),
                )
                track_event(
                    username,
                    "auto_apply_submission_confirmed",
                    {"source": selected_item["source"]},
                )
                st.rerun()
        with action_skip:
            if st.button(
                "Skip role",
                help="Remove this role from the active queue without applying.",
                use_container_width=True,
            ):
                update_queue_item(username, selected_id, "skipped")
                st.rerun()

    st.info(
        "Submission adapters are the next connection layer. Until an employer source confirms a submission, Trovly keeps the role queued for review and does not add it to your weekly total."
    )

with tab_targets:
    st.markdown("### Responsive company and recruiter targets")
    st.markdown(
        "Prioritize companies where the role is fresh, the source is closer to the hiring team, and your own tracker shows response momentum."
    )

    scan_targets = st.session_state.get("responsive_targets", [])
    targets = scan_targets or stored_responsive_targets

    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric("Responsive targets", len(targets))
    with col_t2:
        high_targets = sum(1 for target in targets if target["score"] >= 80)
        st.metric("High response", high_targets)
    with col_t3:
        warm_targets = sum(1 for target in targets if target["score"] >= 65)
        st.metric("Worth outreach", warm_targets)

    if scan_targets:
        st.caption("Showing targets from your most recent scan in this session.")
    elif stored_responsive_targets:
        st.caption("Showing targets from tracked jobs and application history.")

    if not targets:
        st.info(
            "Run a high-fit scan or track applications first. Trovly will use freshness, source quality, salary transparency, and your outcome history to rank responsive targets."
        )
    else:
        for idx, target in enumerate(targets[:10]):
            best_job = target["best_job"]
            with st.expander(
                "{}% - {} ({})".format(
                    target["score"],
                    target["company"],
                    target["label"],
                ),
                expanded=idx < 3,
            ):
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown("**Best role:** {}".format(best_job.get("title") or "Target role"))
                    if best_job.get("location"):
                        st.markdown("**Location:** {}".format(best_job["location"]))
                    if best_job.get("source"):
                        st.markdown("**Source:** {}".format(best_job["source"]))
                    st.markdown("**Action:** {}".format(target["action"]))
                with col_b:
                    st.metric("Open target roles", target["job_count"])
                    if best_job.get("url"):
                        st.link_button("Open posting", best_job["url"])

                st.markdown("**Why this target is responsive**")
                for reason in target["reasons"]:
                    st.markdown(f"- {reason}")

                if target["risks"]:
                    st.markdown("**Risks to verify**")
                    for risk in target["risks"]:
                        st.markdown(f"- {risk}")

                st.markdown("**Recruiter personas to search**")
                st.markdown(_pill_row(target["recruiter_targets"]), unsafe_allow_html=True)

                search_cols = st.columns(4)
                for search_col, link in zip(search_cols, target["search_links"], strict=False):
                    with search_col:
                        st.link_button(link["label"], link["url"])

                st.text_area(
                    "Outreach note",
                    value=target["outreach_note"],
                    height=120,
                    key=f"target_note_{idx}_{target['company']}",
                )

with tab_tailor:
    st.markdown("### AI Resume Tailoring and ATS Optimization")
    st.markdown(
        "Paste a job description to see what to emphasize, what to de-prioritize, and what to add before applying."
    )

    if not user_data.get("resume"):
        st.warning("Complete onboarding first.")
    else:
        jd_input = st.text_area(
            "Job description",
            height=250,
            placeholder="Paste the full job description here...",
        )

        if st.button("Analyze and tailor", type="primary"):
            allowed, msg = can_tailor(username, tier)
            if not allowed:
                st.error(msg)
                prompt = UPGRADE_PROMPTS["tailor_limit"]
                st.info("{} {}".format(prompt["headline"], prompt["body"]))
                st.stop()
            if jd_input and len(jd_input) > 30:
                increment_tailors(username)
                with st.spinner(
                    "Scoring resume bullets, ATS keywords, and cover letter structure..."
                ):
                    try:
                        import config_runtime as config
                        from matcher import reload_resume
                        from tailor import tailor_resume

                        config.RESUME_TEXT = user_data.get("resume", "")
                        reload_resume()
                        result = tailor_resume(jd_input, verbose=False)

                        if "error" in result:
                            st.error(result["error"])
                        else:
                            total = result["total_bullets"]
                            strong_pct = len(result["strong_bullets"]) / total * 100 if total else 0
                            ats_score = min(
                                100, int((strong_pct * 0.65) + (result["jd_keywords_found"] * 4))
                            )
                            track_event(
                                username,
                                "tailor_completed",
                                {
                                    "strong_bullets": len(result["strong_bullets"]),
                                    "skill_gaps": result["jd_keywords_missing"],
                                    "ats_score": ats_score,
                                },
                            )

                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Resume relevance", f"{strong_pct:.0f}%")
                            with col2:
                                st.metric("ATS readiness", f"{ats_score}%")
                            with col3:
                                st.metric("Keywords matched", result["jd_keywords_found"])
                            with col4:
                                st.metric("Skill gaps", result["jd_keywords_missing"])

                            if result["strong_bullets"]:
                                st.markdown("#### Emphasize these bullets")
                                for b in result["strong_bullets"][:10]:
                                    st.markdown("**{:.0%}** - {}".format(b["relevance"], b["text"]))

                            if result["moderate_bullets"]:
                                st.markdown("#### Reword for stronger alignment")
                                for b in result["moderate_bullets"][:8]:
                                    st.markdown("**{:.0%}** - {}".format(b["relevance"], b["text"]))

                            if result["weak_bullets"]:
                                with st.expander("Lower-priority bullets", expanded=False):
                                    for b in result["weak_bullets"][:8]:
                                        st.markdown(
                                            "**{:.0%}** - {}".format(b["relevance"], b["text"])
                                        )

                            if result["skill_gaps"]:
                                st.markdown("#### Skill gap analysis")
                                for gap in result["skill_gaps"]:
                                    st.markdown(f"- **{gap}**")
                            else:
                                st.success("No detected ATS skill gaps.")

                            mock_job = {
                                "title": "Target role",
                                "company": "Target company",
                                "description": jd_input,
                                "salary": "",
                                "location": "",
                            }
                            intelligence = build_match_intelligence(
                                mock_job,
                                (
                                    strong_pct / 100
                                    if strong_pct
                                    else user_data.get("threshold", 0.55)
                                ),
                                resume_text=user_data.get("resume", ""),
                                target_salary=int(user_data.get("target_salary", 150000)),
                            )
                            st.markdown("#### AI cover letter structure")
                            for line in cover_letter_outline(mock_job, intelligence):
                                st.markdown(f"- {line}")

                    except Exception as e:
                        st.error(f"Analysis failed: {e}")

with tab_apps:
    st.markdown("### Application analytics")
    stats = get_stats(username)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total applications", stats["total"])
    with col2:
        st.metric("Active", stats["active"])
    with col3:
        st.metric("Interview rate", "{}%".format(stats["interview_rate"]))
    with col4:
        st.metric("Offer rate", "{}%".format(stats["offer_rate"]))

    follow_ups = get_follow_ups(username, days_threshold=7)
    if follow_ups:
        with st.expander(f"Follow-ups needed ({len(follow_ups)})", expanded=True):
            for app in follow_ups[:10]:
                st.markdown(
                    "**{}** at {} - {} days since last update".format(
                        app["title"],
                        app["company"],
                        app["days_since_update"],
                    )
                )

    with st.expander("Add new application", expanded=False):
        col_t, col_c = st.columns(2)
        with col_t:
            new_title = st.text_input("Job title", key="new_app_title", max_chars=200)
            new_url = st.text_input("URL", key="new_app_url", max_chars=500)
            new_location = st.text_input("Location", key="new_app_location", max_chars=100)
        with col_c:
            new_company = st.text_input("Company", key="new_app_company", max_chars=100)
            new_salary = st.text_input("Salary", key="new_app_salary", max_chars=100)
            new_notes_short = st.text_input("Initial notes", key="new_app_notes", max_chars=500)

        if st.button("Add to tracker", type="primary"):
            success, msg, _ = add_application(
                username,
                new_title,
                new_company,
                url=new_url,
                location=new_location,
                salary=new_salary,
                notes=new_notes_short,
            )
            if success:
                track_event(username, "application_tracked", {"source": "manual"})
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filter_status = st.multiselect(
            "Filter by status",
            options=STATUS_OPTIONS,
            default=[],
            key="app_filter_status",
        )
    with col_f2:
        sort_options = {
            "date_applied": "Date applied (newest first)",
            "last_updated": "Last updated",
            "company": "Company A-Z",
            "status": "Status",
        }
        sort_choice = st.selectbox(
            "Sort by",
            options=list(sort_options.keys()),
            format_func=lambda x: sort_options[x],
            key="app_sort",
        )

    apps = list_applications(
        username,
        status_filter=filter_status if filter_status else None,
        sort_by=sort_choice,
        reverse=(sort_choice in ["date_applied", "last_updated"]),
    )

    if not apps:
        st.info("No applications tracked yet. Add one above or track from scan results.")
    else:
        st.markdown(f"**{len(apps)} applications**")

        for app in apps:
            with st.expander("{} at {} - {}".format(app["title"], app["company"], app["status"])):
                col_l, col_r = st.columns([3, 1])

                with col_l:
                    if app.get("url"):
                        st.markdown("[Open posting]({})".format(app["url"]))
                    if app.get("location"):
                        st.markdown("**Location:** {}".format(app["location"]))
                    if app.get("salary"):
                        st.markdown("**Salary:** {}".format(app["salary"]))
                    st.caption("Applied: {}".format(app.get("date_applied", "")[:10]))
                    st.caption("Last updated: {}".format(app.get("last_updated", "")[:10]))

                with col_r:
                    new_status = st.selectbox(
                        "Status",
                        options=STATUS_OPTIONS,
                        index=(
                            STATUS_OPTIONS.index(app["status"])
                            if app["status"] in STATUS_OPTIONS
                            else 0
                        ),
                        key="status_{}".format(app["id"]),
                    )
                    if new_status != app["status"]:
                        update_application(username, app["id"], {"status": new_status})
                        track_event(username, "application_status_updated", {"status": new_status})
                        st.rerun()

                current_notes = app.get("notes", "")
                new_notes = st.text_area(
                    "Notes",
                    value=current_notes,
                    height=100,
                    key="notes_{}".format(app["id"]),
                    placeholder="Recruiter name, salary discussions, interview feedback, etc.",
                )

                col_save, col_del = st.columns([1, 1])
                with col_save:
                    if new_notes != current_notes and st.button(
                        "Save notes", key=f"save_notes_{app['id']}"
                    ):
                        update_application(username, app["id"], {"notes": new_notes})
                        st.success("Notes saved")
                        st.rerun()
                with col_del:
                    confirm_key = "confirm_del_{}".format(app["id"])
                    if st.button("Delete", key="del_{}".format(app["id"]), type="secondary"):
                        if st.session_state.get(confirm_key):
                            delete_application(username, app["id"])
                            st.session_state[confirm_key] = False
                            st.rerun()
                        else:
                            st.session_state[confirm_key] = True
                            st.warning("Click Delete again to confirm")

                history = app.get("status_history", [])
                if len(history) > 1:
                    st.markdown("**Status history:**")
                    for h in history:
                        st.caption("{}: {}".format(h.get("date", "")[:10], h.get("status", "")))

with tab_alerts:
    st.markdown("### Premium alerts")
    st.markdown(
        "Control urgency thresholds for high-fit roles, newly posted jobs, salary matches, remote roles, and interview likelihood."
    )

    prefs = normalize_alert_preferences(user_data.get("alert_preferences", DEFAULT_ALERT_PREFS))
    alerts_enabled = st.checkbox("Enable alerts", value=prefs["enabled"])

    col_a, col_b = st.columns(2)
    with col_a:
        min_match = st.slider(
            "High-fit match threshold", 0.5, 0.95, prefs["min_match"], 0.01, format="%.0f%%"
        )
        salary_target_only = st.checkbox(
            "Only alert when salary target is met", value=prefs["salary_target_only"]
        )
        remote_alerts = st.checkbox("Only alert for remote-first roles", value=prefs["remote_only"])
    with col_b:
        min_interview_probability = st.slider(
            "Interview likelihood threshold",
            20,
            90,
            prefs["min_interview_probability"],
            5,
            format="%d%%",
        )
        newly_posted_only = st.checkbox(
            "Prioritize newly posted roles", value=prefs["newly_posted_only"]
        )

    st.markdown("#### Channels")
    channel_values = {}
    channel_cols = st.columns(3)
    for idx, channel in enumerate(ALERT_CHANNELS):
        with channel_cols[idx % 3]:
            channel_values[channel["key"]] = st.checkbox(
                "{} - {}".format(channel["label"], channel["best_for"]),
                value=prefs["channels"].get(channel["key"], False),
                key="channel_{}".format(channel["key"]),
            )

    if st.button("Save alert rules", type="primary"):
        new_prefs = {
            "enabled": alerts_enabled,
            "channels": channel_values,
            "min_match": min_match,
            "min_interview_probability": min_interview_probability,
            "salary_target_only": salary_target_only,
            "remote_only": remote_alerts,
            "newly_posted_only": newly_posted_only,
        }
        save_user_data(username, {"alert_preferences": new_prefs})
        track_event(username, "alert_preferences_saved", new_prefs)
        st.success("Alert rules saved.")
        st.rerun()

    st.markdown("#### Urgency copy examples")
    st.markdown("- Be among the first 50 applicants.")
    st.markdown("- High match detected.")
    st.markdown("- New $185k remote role matched your profile.")

with tab_pricing:
    st.markdown("### Pricing built for speed to offer")
    st.markdown(
        "Free validates fit. Pro removes limits. Career Hunter accelerates the search. Offer Accelerator upgrades the whole package."
    )

    plan_cols = st.columns(4)
    for col, plan_key in zip(
        plan_cols, ["free", "pro", "career_hunter", "offer_accelerator"], strict=False
    ):
        with col:
            _render_plan(plan_key, tier)

    st.markdown("### Upgrade prompts")
    for prompt in UPGRADE_PROMPTS.values():
        st.markdown("**{}** {}".format(prompt["headline"], prompt["body"]))

if tab_admin is not None:
    with tab_admin:
        st.markdown("### Admin analytics")
        st.markdown(
            "Funnel, retention, conversion, and alert engagement concepts for the current JSON-backed app."
        )

        funnel = get_funnel_metrics(days=30)
        retention = get_retention_metrics(days=30)
        st.markdown("#### Funnel")
        st.table(funnel)
        st.markdown("#### Retention")
        if retention:
            st.line_chart({row["date"]: row["active_users"] for row in retention})
        else:
            st.info("No retention events yet.")

        st.markdown("#### Events to productionize")
        for event in [
            "resume_uploaded",
            "match_clicked",
            "application_tracked",
            "subscription_upgraded",
            "alert_engaged",
            "interview_outcome_logged",
        ]:
            st.markdown(f"- {event}")

with tab_recruiter:
    st.markdown("### Recruiter Mode")
    st.markdown(
        "A B2B layer for staffing teams: candidate semantic search, resume ranking, fit explanations, and pipeline management."
    )

    col_left, col_right = st.columns([1.1, 0.9])
    with col_left:
        st.markdown("#### Recruiter features")
        for feature in [
            "Candidate semantic search across resumes and role requirements",
            "Resume ranking with explainable fit scores",
            "Talent pipeline boards by role, stage, and recruiter",
            "API access for ATS ingestion",
            "White-label match reports for clients",
        ]:
            st.markdown(f"- {feature}")

        st.markdown("#### SEO/content engine")
        for category in SEO_CATEGORIES:
            st.markdown("- **{}:** {}".format(category["title"], category["description"]))

    with col_right:
        for plan in B2B_PLANS:
            st.markdown(
                """
                <div class='pricing-panel'>
                    <div class='eyebrow'>{name}</div>
                    <h2>{price}</h2>
                    <p>{cadence}</p>
                    {features}
                </div>
                """.format(
                    name=escape(plan["name"]),
                    price=escape(plan["price"]),
                    cadence=escape(plan["cadence"]),
                    features="<br>".join(escape(feature) for feature in plan["features"]),
                ),
                unsafe_allow_html=True,
            )
