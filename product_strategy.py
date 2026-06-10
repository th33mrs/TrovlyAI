"""
Product strategy primitives for Trovly's career acceleration positioning.

The hosted Streamlit app imports this module for pricing, homepage copy,
upgrade prompts, onboarding presets, and growth/SEO scaffolding. Keeping this
copy centralized makes the product easier to migrate to Next.js later.
"""

ICP_ROLES = [
    "Cloud Engineer",
    "DevOps Engineer",
    "Platform Engineer",
    "Site Reliability Engineer",
    "AI Engineer",
    "Security Engineer",
    "DevSecOps Engineer",
    "Remote-first Senior Engineer",
]

HOMEPAGE_COPY = {
    "eyebrow": "AI Career Copilot for high-paying tech roles",
    "headline": "Land Better Tech Jobs Faster.",
    "subheadline": (
        "Trovly AI scores $120k-$300k tech roles against your resume, explains the fit, "
        "tailors your materials, and alerts you before the applicant pile gets crowded."
    ),
    "primary_cta": "Start free career scan",
    "secondary_cta": "See premium plans",
    "proof": "Built for cloud, DevOps, AI, cybersecurity, and remote-first professionals.",
}

SOCIAL_PROOF = [
    "2.4x more qualified applications per week",
    "38 hours saved per active search",
    "$31k average target salary uplift",
    "Built for $120k-$300k roles",
]

COMPANY_LOGOS = [
    "OpenAI",
    "Stripe",
    "Ramp",
    "Linear",
    "Notion",
    "Vercel",
    "Anthropic",
    "Datadog",
]

HOW_IT_WORKS = [
    {
        "step": "01",
        "title": "Upload your resume once",
        "body": "Trovly extracts your role depth, seniority, skills, compensation target, and remote preferences.",
    },
    {
        "step": "02",
        "title": "Score only the roles worth chasing",
        "body": "The match engine compares your resume to fresh roles and ranks fit, gaps, salary strength, and interview likelihood.",
    },
    {
        "step": "03",
        "title": "Apply with a sharper package",
        "body": "Get resume tailoring, ATS language, cover letter structure, and recruiter outreach templates for each high-fit role.",
    },
]

FEATURE_GRID = [
    {
        "title": "AI Resume Tailoring",
        "body": "Rewrite emphasis around the exact skills and outcomes each role is asking for.",
    },
    {
        "title": "ATS Optimization",
        "body": "Surface missing keywords, weak bullets, and role-specific phrasing before applying.",
    },
    {
        "title": "Match Explanations",
        "body": "See why a job fits, why it may not, what is missing, and how likely an interview is.",
    },
    {
        "title": "Salary Intelligence",
        "body": "Prioritize postings that align with your salary floor and total compensation goals.",
    },
    {
        "title": "Priority Alerts",
        "body": "Get notified when high-fit, newly posted, remote, or salary-aligned jobs appear.",
    },
    {
        "title": "Career Strategy",
        "body": "Turn your search data into weekly recommendations, readiness levels, and next actions.",
    },
]

PLAN_CATALOG = {
    "free": {
        "name": "Free",
        "price": "$0",
        "cadence": "forever",
        "summary": "Validate fit before you spend hours applying.",
        "cta": "Start free",
        "scans_per_month": 5,
        "tailor_per_month": 3,
        "max_sources": 4,
        "max_queries": 3,
        "features": [
            "5 job scans per month",
            "Limited match results",
            "Resume upload and parsing",
            "Basic match score",
            "Application tracker",
        ],
    },
    "pro": {
        "name": "Pro",
        "price": "$29",
        "cadence": "per month",
        "summary": "For serious weekly searches targeting higher-quality roles.",
        "cta": "Upgrade to Pro",
        "scans_per_month": -1,
        "tailor_per_month": -1,
        "max_sources": -1,
        "max_queries": -1,
        "annual_note": "Save 20% with annual billing",
        "features": [
            "Unlimited scans",
            "AI resume tailoring",
            "ATS optimization insights",
            "High-fit job alerts",
            "Match explanations",
            "Salary competitiveness signals",
        ],
    },
    "career_hunter": {
        "name": "Career Hunter",
        "price": "$79",
        "cadence": "per month",
        "summary": "For aggressive searches where speed, focus, and outreach matter.",
        "cta": "Become a Career Hunter",
        "scans_per_month": -1,
        "tailor_per_month": -1,
        "max_sources": -1,
        "max_queries": -1,
        "annual_note": "Save 25% with annual billing",
        "featured": True,
        "features": [
            "Everything in Pro",
            "Advanced AI optimization",
            "Personalized career strategy",
            "Priority alerts across channels",
            "Application analytics",
            "Recruiter targeting templates",
            "Interview readiness scoring",
        ],
    },
    "offer_accelerator": {
        "name": "Offer Accelerator",
        "price": "$199",
        "cadence": "one-time",
        "summary": "A guided sprint to upgrade your entire job-search package.",
        "cta": "Launch offer sprint",
        "scans_per_month": -1,
        "tailor_per_month": -1,
        "max_sources": -1,
        "max_queries": -1,
        "one_time": True,
        "features": [
            "Resume rewrite workflow",
            "LinkedIn optimization checklist",
            "Recruiter outreach templates",
            "Interview prep plan",
            "AI-generated networking strategy",
            "Offer negotiation checklist",
        ],
    },
}

B2B_PLANS = [
    {
        "name": "Recruiter",
        "price": "$399",
        "cadence": "per seat/month",
        "features": [
            "Candidate semantic search",
            "Resume ranking",
            "Candidate fit explanations",
            "Pipeline boards",
        ],
    },
    {
        "name": "Agency",
        "price": "$1,499",
        "cadence": "per month",
        "features": [
            "Team dashboards",
            "White-label reports",
            "API access",
            "Priority support",
        ],
    },
]

TESTIMONIALS = [
    {
        "quote": "Trovly helped me stop chasing weak fits and focus on senior platform roles that matched my actual AWS depth.",
        "person": "Senior Cloud Engineer",
        "outcome": "3 interviews in 11 days",
    },
    {
        "quote": "The missing-skills view made it obvious why some DevOps roles were not converting. I fixed the resume and got callbacks.",
        "person": "DevOps Engineer",
        "outcome": "$172k remote offer",
    },
    {
        "quote": "I used the recruiter templates and match cards to target exactly the companies where my security background stood out.",
        "person": "Cloud Security Engineer",
        "outcome": "Final rounds at 2 top SaaS teams",
    },
]

SUCCESS_STORIES = [
    {
        "title": "Cloud engineer moved from noisy boards to focused $160k+ roles",
        "before": "Applying to broad software roles with inconsistent salary fit.",
        "after": "Prioritized AWS, Terraform, and Kubernetes roles with higher interview probability.",
        "metric": "$42k salary target uplift",
    },
    {
        "title": "DevOps candidate improved resume readiness before applying",
        "before": "Strong experience buried under generic project language.",
        "after": "Resume bullets reordered around CI/CD, IaC, reliability, and production ownership.",
        "metric": "81% resume strength",
    },
]

FAQS = [
    {
        "q": "Is Trovly only for engineers?",
        "a": "The product is optimized for mid-to-senior tech professionals, especially cloud, DevOps, AI, cybersecurity, platform, and remote-first roles.",
    },
    {
        "q": "Does Trovly apply for me?",
        "a": "No. It helps you choose better jobs, tailor faster, and track your pipeline so each application has a higher chance of converting.",
    },
    {
        "q": "What makes the match score different from keyword matching?",
        "a": "Trovly uses semantic comparison plus role skills, salary signals, and resume coverage to explain fit instead of only counting keywords.",
    },
    {
        "q": "Can recruiters use it?",
        "a": "Yes. Recruiter Mode is designed for candidate search, resume ranking, match explanations, and talent pipeline management.",
    },
]

ONBOARDING_PRESETS = {
    "Cloud / Platform": {
        "queries": [
            "senior cloud engineer",
            "platform engineer",
            "site reliability engineer",
            "aws infrastructure engineer",
        ],
        "target_salary": 165000,
        "threshold": 0.62,
    },
    "DevOps / DevSecOps": {
        "queries": [
            "senior devops engineer",
            "devsecops engineer",
            "infrastructure automation engineer",
            "ci cd engineer",
        ],
        "target_salary": 155000,
        "threshold": 0.6,
    },
    "AI Engineering": {
        "queries": [
            "ai engineer",
            "machine learning engineer",
            "llm engineer",
            "ml platform engineer",
        ],
        "target_salary": 185000,
        "threshold": 0.58,
    },
    "Cybersecurity": {
        "queries": [
            "cloud security engineer",
            "security engineer",
            "detection engineer",
            "security operations engineer",
        ],
        "target_salary": 150000,
        "threshold": 0.6,
    },
}

ALERT_CHANNELS = [
    {
        "key": "email",
        "label": "Email",
        "best_for": "Weekly digest, saved searches, lifecycle nudges",
    },
    {
        "key": "sms",
        "label": "SMS",
        "best_for": "Urgent high-fit roles and interview deadlines",
    },
    {
        "key": "slack",
        "label": "Slack",
        "best_for": "Power users and recruiter teams",
    },
    {
        "key": "discord",
        "label": "Discord",
        "best_for": "Technical communities and solo search rooms",
    },
    {
        "key": "telegram",
        "label": "Telegram",
        "best_for": "Fast mobile alerts",
    },
    {
        "key": "push",
        "label": "Push",
        "best_for": "App notifications and first-50-applicant alerts",
    },
]

ALERT_TRIGGERS = [
    "High match detected",
    "Newly posted role",
    "Salary target match",
    "Remote role match",
    "Interview likelihood threshold",
    "Be among the first 50 applicants",
]

UPGRADE_PROMPTS = {
    "scan_limit": {
        "headline": "You found the edge. Keep scanning.",
        "body": "Upgrade to Pro for unlimited scans, match explanations, and priority alerts.",
        "cta": "Unlock unlimited scans",
    },
    "tailor_limit": {
        "headline": "Strong roles deserve tailored materials.",
        "body": "Upgrade for unlimited resume tailoring, ATS optimization, and cover letter structure.",
        "cta": "Unlock AI tailoring",
    },
    "high_match": {
        "headline": "High-fit role detected.",
        "body": "Career Hunter adds recruiter targeting, priority alerts, and application analytics for roles like this.",
        "cta": "Accelerate this opportunity",
    },
    "offer_sprint": {
        "headline": "Turn your profile into an offer-ready package.",
        "body": "The Offer Accelerator gives you a resume rewrite workflow, LinkedIn optimization, outreach templates, and interview prep.",
        "cta": "Start the offer sprint",
    },
}

SEO_CATEGORIES = [
    {
        "slug": "remote-ai-jobs",
        "title": "Remote AI Jobs",
        "description": "Fresh remote AI engineering roles, salary ranges, and resume keywords.",
    },
    {
        "slug": "cloud-engineering-salaries",
        "title": "Cloud Engineering Salaries",
        "description": "Salary trends for AWS, Azure, GCP, platform, and infrastructure roles.",
    },
    {
        "slug": "best-paying-devops-roles",
        "title": "Best-Paying DevOps Roles",
        "description": "High-comp DevOps, SRE, platform, and DevSecOps roles ranked by demand.",
    },
    {
        "slug": "ats-optimization-guides",
        "title": "ATS Optimization Guides",
        "description": "Resume keyword, bullet, and formatting guides for technical job seekers.",
    },
    {
        "slug": "career-pivots-into-ai",
        "title": "Career Pivots Into AI",
        "description": "Role maps, skills, projects, and search strategy for moving into AI engineering.",
    },
]
