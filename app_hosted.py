"""
Trovly - Hosted App
Run with: streamlit run app_hosted.py
"""

import csv
from html import escape
from io import StringIO

import streamlit as st

from admin_tools import (
    build_admin_overview,
    build_application_rows,
    build_event_mix,
    build_event_rows,
    build_store_status,
    build_user_rows,
    is_admin_user,
    load_admin_state,
    reset_user_usage,
    update_user_admin_fields,
)
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
    HOMEPAGE_COPY,
    ONBOARDING_PRESETS,
    SEO_CATEGORIES,
)
from resume_parser import parse_resume_file
from tracker import JobTracker
from usage_limits import (
    can_scan,
    can_tailor,
    get_current_period,
    get_user_tier,
    increment_scans,
    increment_tailors,
)

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

button:focus-visible,
a:focus-visible {
    outline: 3px solid var(--blue) !important;
    outline-offset: 3px !important;
}

.app-hero, .premium-panel {
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
user_is_admin = is_admin_user(username, user_data)
tier = get_user_tier(user_data)
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


def _rows_to_csv(rows):
    if not rows:
        return ""
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


with st.sidebar:
    st.markdown("## Trovly AI")
    st.caption(f"Logged in as {username}")
    if user_is_admin:
        st.caption("Admin access")
    st.markdown("---")

    st.markdown("**Early access**")
    st.caption("All core career tools are currently available.")

    st.markdown("---")
    st.metric("Resume strength", "{}%".format(resume_strength["score"]))
    st.caption(resume_strength["level"])
    st.metric("Match quality", "{}%".format(career_metrics["match_quality"]))
    st.markdown("---")
    if st.button("Log out", help="Log out of your Trovly account"):
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
            "Track match quality, resume readiness, alerts, and applications from one focused career workspace."
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
    "Responsive Targets",
    "Resume AI",
    "Applications",
    "Alerts",
]
if user_is_admin:
    tab_labels.append("Admin")
tab_labels.append("Recruiter Mode")

tabs = st.tabs(tab_labels)
(
    tab_dashboard,
    tab_setup,
    tab_scan,
    tab_targets,
    tab_tailor,
    tab_apps,
    tab_alerts,
) = tabs[:7]

if user_is_admin:
    tab_admin = tabs[7]
    tab_recruiter = tabs[8]
else:
    tab_admin = None
    tab_recruiter = tabs[7]

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
        st.caption("Referral rewards are planned for early-access invites.")
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

    if st.button(
        "Save career profile",
        type="primary",
        help="Save your resume, target roles, salary target, and search preferences",
    ):
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

        if st.button(
            "Run high-fit scan",
            type="primary",
            help="Scan active job sources and rank roles against your career profile",
        ):
            allowed, msg = can_scan(username, tier)
            if not allowed:
                st.error(msg)
                st.stop()
            increment_scans(username)
            with st.spinner(
                "Scanning fresh roles, scoring fit, salary, gaps, and interview likelihood..."
            ):
                try:
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
                    track_event(
                        username,
                        "scan_completed",
                        {"fetched": len(jobs), "matched": len(matched), "tier": tier},
                    )

                    if matched:
                        st.success(f"Found {len(matched)} matches worth reviewing.")
                        visible_matches = matched
                        st.session_state["responsive_targets"] = rank_responsive_targets(
                            visible_matches,
                            applications=application_records,
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
                                        st.link_button(
                                            link["label"],
                                            link["url"],
                                            help="Open {} for {}".format(
                                                link["label"], job.company or "this company"
                                            ),
                                        )

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
                                    if st.link_button(
                                        "Apply to {}".format(job.company or "company"),
                                        job.url,
                                        help="Open the application page for {} at {}".format(
                                            job.title, job.company or "this company"
                                        ),
                                    ):
                                        track_event(
                                            username,
                                            "job_apply_clicked",
                                            {"title": job.title, "company": job.company},
                                        )
                                with col_track:
                                    if st.button(
                                        "Track application",
                                        key=f"track_{job.uid}",
                                        help="Add {} at {} to your application tracker".format(
                                            job.title, job.company or "this company"
                                        ),
                                    ):
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
                        st.link_button(
                            "Open {} posting".format(target["company"]),
                            best_job["url"],
                            help="Open the {} job posting in a new page".format(target["company"]),
                        )

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
                        st.link_button(
                            link["label"],
                            link["url"],
                            help="Open {} for {}".format(link["label"], target["company"]),
                        )

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

        if st.button(
            "Analyze and tailor",
            type="primary",
            help="Analyze your resume against the pasted job description",
        ):
            allowed, msg = can_tailor(username, tier)
            if not allowed:
                st.error(msg)
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

        if st.button(
            "Add to tracker",
            type="primary",
            help="Add this job application to your application tracker",
        ):
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
                        "Save notes",
                        key=f"save_notes_{app['id']}",
                        help="Save notes for {} at {}".format(app["title"], app["company"]),
                    ):
                        update_application(username, app["id"], {"notes": new_notes})
                        st.success("Notes saved")
                        st.rerun()
                with col_del:
                    confirm_key = "confirm_del_{}".format(app["id"])
                    delete_pending = st.session_state.get(confirm_key, False)
                    delete_label = "Confirm delete" if delete_pending else "Delete application"
                    if st.button(
                        delete_label,
                        key="del_{}".format(app["id"]),
                        type="secondary",
                        help="Delete the {} application at {}".format(app["title"], app["company"]),
                    ):
                        if delete_pending:
                            delete_application(username, app["id"])
                            st.session_state[confirm_key] = False
                            st.rerun()
                        else:
                            st.session_state[confirm_key] = True
                            st.warning("Select Confirm delete to remove this application.")

                history = app.get("status_history", [])
                if len(history) > 1:
                    st.markdown("**Status history:**")
                    for h in history:
                        st.caption("{}: {}".format(h.get("date", "")[:10], h.get("status", "")))

with tab_alerts:
    st.markdown("### Job alerts")
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

    if st.button(
        "Save alert rules",
        type="primary",
        help="Save your job alert channels and matching thresholds",
    ):
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

if user_is_admin and tab_admin is not None:
    with tab_admin:
        st.markdown("### Admin panel")
        current_period = get_current_period()
        admin_state = load_admin_state()
        admin_users = admin_state["users"]
        admin_usage = admin_state["usage"]
        admin_applications = admin_state["applications"]
        admin_events = admin_state["events"]

        overview = build_admin_overview(
            admin_users,
            admin_usage,
            admin_applications,
            admin_events,
            period=current_period,
        )

        metric_row = st.columns(4)
        with metric_row[0]:
            st.metric("Users", overview["total_users"], overview["new_users_30d"])
        with metric_row[1]:
            st.metric("Active 30d", overview["active_users_30d"])
        with metric_row[2]:
            st.metric("Applications", overview["applications_total"])
        with metric_row[3]:
            st.metric("Offers", overview["offers_total"])

        metric_row = st.columns(4)
        with metric_row[0]:
            st.metric("Admins", overview["admin_users"])
        with metric_row[1]:
            st.metric("Locked", overview["locked_accounts"])
        with metric_row[2]:
            st.metric("Scans", overview["scans_this_month"])
        with metric_row[3]:
            st.metric("Tailors", overview["tailors_this_month"])

        st.markdown("#### Users")
        user_rows = build_user_rows(
            admin_users,
            admin_usage,
            admin_applications,
            admin_events,
            period=current_period,
        )
        filter_cols = st.columns([1.4, 0.8])
        with filter_cols[0]:
            user_search = st.text_input("Search users", key="admin_user_search")
        with filter_cols[1]:
            state_filter = st.selectbox(
                "State",
                ["All", "Admins", "Locked", "Onboarded"],
                key="admin_state_filter",
            )

        filtered_user_rows = user_rows
        if user_search:
            needle = user_search.strip().lower()
            filtered_user_rows = [
                row
                for row in filtered_user_rows
                if needle in row["username"].lower() or needle in row["email"].lower()
            ]
        if state_filter == "Admins":
            filtered_user_rows = [row for row in filtered_user_rows if row["admin"]]
        elif state_filter == "Locked":
            filtered_user_rows = [row for row in filtered_user_rows if row["locked"]]
        elif state_filter == "Onboarded":
            filtered_user_rows = [row for row in filtered_user_rows if row["onboarded"]]

        if filtered_user_rows:
            st.dataframe(filtered_user_rows, width="stretch", hide_index=True)
            st.download_button(
                "Download users CSV",
                data=_rows_to_csv(filtered_user_rows),
                file_name="trovly_admin_users.csv",
                mime="text/csv",
                help="Download the filtered user list as a CSV file",
            )
        else:
            st.info("No users match those filters.")

        selected_options = [row["username"] for row in filtered_user_rows]
        if selected_options:
            selected_user = st.selectbox(
                "Manage account",
                selected_options,
                key="admin_selected_user",
            )
        else:
            selected_user = None

        if selected_user:
            selected_data = admin_users.get(selected_user, {})
            selected_row = next(
                (row for row in user_rows if row["username"] == selected_user),
                {},
            )
            st.markdown("#### Account controls")
            account_cols = st.columns(3)
            with account_cols[0]:
                st.metric("Applications", selected_row.get("applications", 0))
            with account_cols[1]:
                st.metric("Interviews", selected_row.get("interviews", 0))
            with account_cols[2]:
                st.metric("Resume chars", selected_row.get("resume_chars", 0))

            with st.form("admin_account_form"):
                form_cols = st.columns(2)
                with form_cols[0]:
                    grant_admin = st.checkbox(
                        "Admin role",
                        value=bool(
                            selected_data.get("is_admin")
                            or str(selected_data.get("role", "")).lower() in {"admin", "owner"}
                        ),
                    )
                with form_cols[1]:
                    onboarding_completed = st.checkbox(
                        "Onboarding complete",
                        value=bool(selected_data.get("onboarding_completed")),
                    )
                    unlock_account = st.checkbox(
                        "Unlock account",
                        value=False,
                        disabled=not selected_row.get("locked", False),
                    )

                save_account = st.form_submit_button(
                    "Save account changes",
                    type="primary",
                    help=f"Save access and onboarding changes for {selected_user}",
                )

            if save_account:
                ok, msg = update_user_admin_fields(
                    selected_user,
                    is_admin=grant_admin,
                    onboarding_completed=onboarding_completed,
                    unlock=unlock_account,
                    actor=username,
                )
                if ok:
                    track_event(
                        username,
                        "admin_user_updated",
                        {
                            "target_user": selected_user,
                            "admin": grant_admin,
                            "unlock": unlock_account,
                        },
                    )
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            if st.button(
                "Reset monthly usage",
                key=f"reset_usage_{selected_user}",
                help=f"Reset scan and resume-analysis usage for {selected_user}",
            ):
                ok, msg = reset_user_usage(selected_user, period=current_period)
                if ok:
                    track_event(
                        username,
                        "admin_usage_reset",
                        {"target_user": selected_user, "period": current_period},
                    )
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        st.markdown("#### Product analytics")
        analytics_cols = st.columns(2)
        with analytics_cols[0]:
            funnel = get_funnel_metrics(days=30)
            st.table(funnel)
        with analytics_cols[1]:
            retention = get_retention_metrics(days=30)
            if retention:
                st.line_chart({row["date"]: row["active_users"] for row in retention})
            else:
                st.info("No retention events yet.")

        event_mix = build_event_mix(admin_events, days=30)
        if event_mix:
            st.markdown("#### Event mix")
            st.bar_chart({row["event"]: row["events"] for row in event_mix})
            st.dataframe(event_mix, width="stretch", hide_index=True)

        recent_events = build_event_rows(admin_events, limit=50)
        st.markdown("#### Recent events")
        if recent_events:
            st.dataframe(recent_events, width="stretch", hide_index=True)
        else:
            st.info("No analytics events recorded yet.")

        recent_apps = build_application_rows(admin_applications, limit=50)
        st.markdown("#### Recent applications")
        if recent_apps:
            st.dataframe(recent_apps, width="stretch", hide_index=True)
        else:
            st.info("No applications tracked yet.")

        st.markdown("#### Storage")
        st.table(build_store_status())

with tab_recruiter:
    st.markdown("### Recruiter Mode")
    st.markdown(
        "A B2B layer for staffing teams: candidate semantic search, resume ranking, fit explanations, and pipeline management."
    )

    st.markdown("#### Recruiter features")
    for feature in [
        "Candidate semantic search across resumes and role requirements",
        "Resume ranking with explainable fit scores",
        "Talent pipeline boards by role, stage, and recruiter",
        "API access for ATS ingestion",
        "White-label match reports for clients",
    ]:
        st.markdown(f"- {feature}")

    st.info("Recruiter Mode is in private beta while the workflow is being validated.")

    st.markdown("#### SEO/content engine")
    for category in SEO_CATEGORIES:
        st.markdown("- **{}:** {}".format(category["title"], category["description"]))
