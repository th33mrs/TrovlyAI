# Trovly AI Career Acceleration Platform Plan

## 1. Product Roadmap

### Days 0-14: Speed to Revenue
- Ship premium positioning in the hosted app: "AI Career Copilot for landing high-paying tech jobs faster."
- Convert the current signup screen into a landing page with hero, social proof, match preview, resume example, testimonials, FAQ, and pricing.
- Add new tiers: Free, Pro at $29/month, Career Hunter at $79/month, Offer Accelerator at $199 one-time.
- Add upgrade-intent tracking now, then wire Stripe Checkout in the next billing sprint.
- Add job-level premium signals: match percent, missing skills, why fit, why not, interview likelihood, salary competitiveness.
- Add salary target onboarding and role-lane presets for cloud, DevOps, AI, and cybersecurity.
- Add alerts UI for email, SMS, Slack, Discord, Telegram, and push.
- Add analytics event logging for signup, profile save, scans, tailoring, applications, alert settings, and upgrade intent.

### Days 15-30: Conversion and Retention
- Add Stripe Checkout, customer portal, webhooks, plan gating, annual billing, and trial conversion emails.
- Add lifecycle email/SMS: onboarding incomplete, scan reminder, high-match digest, tailor-before-apply, interview prep, upgrade nudges.
- Persist match explanations and alerts per user so weekly digests have useful history.
- Add resume versioning and saved tailored versions per job.
- Add application outcome logging: interview, final, offer, rejected, salary, source.
- Add admin funnel: signup -> profile -> scan -> apply click -> application tracked -> upgrade.

### Days 31-60: Growth Loops and SEO
- Add referral codes, invite rewards, and premium-tailoring credits.
- Generate share cards: resume strength, top companies matching you, salary target, weekly match streak.
- Launch SEO pages for remote AI jobs, cloud engineering salaries, DevOps compensation, ATS optimization, and AI career pivots.
- Add salary trend pages and hiring reports based on collected job data.
- Add content templates with structured metadata and internal linking.

### Days 61-90: Scale and B2B
- Move from JSON files to Supabase/Postgres.
- Add pgvector embeddings for resumes, job descriptions, and candidate search.
- Add a background job queue for scans, alerts, content refresh, and digest generation.
- Add recruiter mode: candidate semantic search, resume ranking, fit explanations, pipeline management, B2B pricing, API access, and white-label reports.
- Add Redis caching for frequent searches and landing page data.

## 2. Updated Information Architecture

Public:
- `/` -> landing page
- `/pricing` -> pricing and offer comparison
- `/resume-optimization` -> ATS and tailoring guide
- `/salary-trends/[role]` -> salary intelligence pages
- `/remote-tech-jobs/[category]` -> SEO job trend pages
- `/recruiters` -> B2B recruiter landing page
- `/case-studies/[slug]` -> success stories
- `/blog/[slug]` -> SEO content

Authenticated candidate app:
- `/app` -> command center
- `/app/onboarding` -> resume, target roles, salary, alerts
- `/app/matches` -> job matches with explanations
- `/app/resume-ai` -> tailoring, ATS optimization, versions
- `/app/applications` -> pipeline and outcomes
- `/app/alerts` -> notification rules
- `/app/billing` -> plan, invoices, annual billing
- `/app/referrals` -> invite rewards and share cards

Admin:
- `/admin` -> MRR, activation, retention, funnels
- `/admin/users` -> user search, plan state, health score
- `/admin/content` -> content engine and SEO pages
- `/admin/alerts` -> alert delivery and engagement

Recruiter:
- `/recruiter` -> dashboard
- `/recruiter/search` -> candidate semantic search
- `/recruiter/pipelines` -> talent pipeline
- `/recruiter/api` -> API keys and docs

## 3. Landing Page Redesign

Implemented in `auth.py` as the public auth screen:
- Hero headline: "Land Better Tech Jobs Faster."
- Subhead: "Trovly AI scores $120k-$300k tech roles against your resume, explains the fit, tailors your materials, and alerts you before the applicant pile gets crowded."
- CTA: "Start free career scan"
- Social proof: "2.4x more qualified applications per week", "38 hours saved per active search", "$31k average target salary uplift", "Built for $120k-$300k roles"
- Sections: social proof, how it works, premium features, match engine preview, resume optimization example, success stories, testimonials, pricing, FAQ, final CTA.

Visual direction:
- Neutral SaaS base, sharp 8px radius, dense but clean surfaces.
- No broad consumer-job-search language.
- Match score cards make the product tangible in the first viewport.

## 4. Database Schema Recommendations

Use Supabase Postgres with pgvector. See `docs/database_schema.sql` for a concrete schema.

Core entities:
- `profiles`: user ICP, target salary, plan, onboarding state.
- `resumes`: uploaded parsed resumes and embeddings.
- `resume_versions`: tailored resume snapshots by job.
- `jobs`: normalized job postings.
- `job_embeddings`: semantic vectors for job descriptions.
- `matches`: user-job fit records, explanations, salary signal, interview probability.
- `applications`: pipeline tracking and outcomes.
- `alerts`: user alert preferences.
- `alert_deliveries`: delivery logs and engagement.
- `subscriptions`: Stripe plan state.
- `referrals`: invite rewards.
- `analytics_events`: funnel and retention events.
- `content_pages`: SEO content engine.
- `candidate_profiles` and `recruiter_pipelines`: B2B recruiter mode.

## 5. Feature Architecture

Candidate matching:
- Resume parser -> structured resume profile -> embedding -> role-lane skill extraction.
- Job ingestion -> normalized posting -> salary parser -> embedding.
- Match engine -> semantic similarity plus skill overlap, seniority signal, remote signal, salary signal.
- Explanation engine -> why fit, why not, missing skills, interview probability, salary competitiveness.

Resume AI:
- ATS keyword coverage.
- Bullet ranking and weak-bullet identification.
- Tailored resume version creation.
- Cover letter structure by job.
- LinkedIn optimization checklist.

Alerts:
- Rules: match threshold, salary target, remote-only, newly posted, interview likelihood.
- Channels: email, SMS, Slack, Discord, Telegram, push.
- Jobs: queue delivery, dedupe per user/job/channel, track opens/clicks.

Growth:
- Referral rewards.
- Shareable match cards.
- Resume strength score.
- Match streaks.
- Top companies matching you.
- Career readiness levels.

## 6. API Architecture

Next.js route examples:

```txt
POST /api/resumes/upload
POST /api/resumes/:id/tailor
POST /api/jobs/scan
GET  /api/matches
GET  /api/matches/:id
POST /api/applications
PATCH /api/applications/:id
POST /api/alerts/test
PATCH /api/alerts/preferences
POST /api/billing/checkout
POST /api/billing/portal
POST /api/stripe/webhook
POST /api/referrals/redeem
GET  /api/admin/funnel
GET  /api/admin/cohorts
POST /api/recruiter/search
POST /api/recruiter/pipelines/:id/candidates
```

Example match response:

```json
{
  "matchId": "match_123",
  "job": {
    "title": "Senior Cloud Platform Engineer",
    "company": "Ramp",
    "salaryMin": 165000,
    "salaryMax": 220000,
    "remote": true
  },
  "score": 0.86,
  "interviewProbability": 68,
  "salaryCompetitiveness": "Strong",
  "missingSkills": ["OpenTelemetry", "ArgoCD"],
  "whyFit": [
    "Strong AWS, Terraform, Kubernetes, and reliability overlap",
    "Remote-first role meets preference",
    "Salary range clears target"
  ],
  "whyNot": [
    "Observability tooling should be emphasized more directly"
  ]
}
```

## 7. UI/UX Improvements

Implemented:
- Public landing page replaces generic login-first screen.
- Auth copy now says "Career Copilot for $150k+ tech roles."
- Command Center dashboard shows interviews generated, applications saved, salary uplift, readiness level.
- Onboarding captures role lane, target salary, remote preference, threshold, and parsed resume upload.
- Scan results show match explanations, missing skills, salary signal, interview likelihood, and alert copy.
- Pricing tab exposes all monetization offers.
- Alerts tab exposes channel preferences and urgency thresholds.
- Admin analytics and Recruiter Mode tabs create concrete product surfaces.

Next:
- Add a dedicated billing page after Stripe is wired.
- Add visual share-card generator.
- Add saved tailored resume versions by job.

## 8. Monetization Implementation Plan

Free:
- 5 scans/month.
- 3 resume analyses/month.
- Limited matches per scan.
- Basic match score.

Pro at $29/month:
- Unlimited scans.
- AI resume tailoring.
- ATS insights.
- Alerts.
- Match explanations.
- Salary competitiveness.

Career Hunter at $79/month:
- Everything in Pro.
- Advanced optimization.
- Personalized career recommendations.
- Priority alerts.
- Application analytics.
- Recruiter targeting templates.
- Interview readiness scoring.

Offer Accelerator at $199 one-time:
- Resume rewrite workflow.
- LinkedIn optimization.
- Recruiter outreach templates.
- Interview prep.
- AI-generated networking strategy.
- Offer negotiation checklist.

Stripe implementation:
- Create Stripe products and recurring prices for Pro and Career Hunter.
- Create one-time price for Offer Accelerator.
- Add `/api/billing/checkout`.
- Add webhook handling for `checkout.session.completed`, `customer.subscription.updated`, `invoice.payment_failed`, and `customer.subscription.deleted`.
- Store `stripe_customer_id`, `subscription_id`, `plan`, `status`, `current_period_end`.
- Gate features from subscription state, not client-side UI.

## 9. SEO and Content Strategy

Content categories:
- Remote AI jobs.
- Cloud engineering salaries.
- Best-paying DevOps roles.
- Resume optimization tips.
- Interview prep.
- Career pivots into AI.

Programmatic pages:
- `/salary-trends/cloud-engineer`
- `/salary-trends/devops-engineer`
- `/remote-tech-jobs/ai-engineer`
- `/guides/ats-optimization-cloud-engineer`
- `/reports/tech-hiring-q2-2026`

Structured metadata:
- `JobPosting` for job pages.
- `FAQPage` for guides.
- `Article` for blog content.
- `BreadcrumbList` for content hubs.
- `SoftwareApplication` for product landing pages.

Content loop:
- Mine job data for salary ranges, skill demand, and remote share.
- Generate weekly hiring reports.
- Use internal links to push readers into free career scans.
- Add CTA blocks inside every guide: "Scan your resume against $150k+ roles."

## 10. Viral Growth Strategy

Referral system:
- Give referrer 1 premium tailoring pack per activated invite.
- Give invited user 2 extra scans.
- Unlock a Career Hunter trial after 3 qualified referrals.

Share loops:
- Shareable match score card.
- LinkedIn card: "Top companies matching my profile."
- Resume strength score card.
- Weekly match streak.
- Salary target progress.

Gamification:
- Resume strength score.
- Application efficiency score.
- Interview readiness level.
- Match streaks.
- Career readiness levels: Needs Rebuild, Needs Targeting, Interview-Ready, Offer-Ready.

## 11. Subscription Funnel Optimization

Activation event:
- User saves profile, runs first scan, sees at least one match explanation.

Upgrade triggers:
- Free scan limit reached.
- Free tailoring limit reached.
- High-fit job detected above 75%.
- Salary-aligned job detected.
- User tracks 3+ applications.
- User has low interview rate and needs optimization.

Trial conversion:
- 7-day Pro trial after first high-fit match.
- Annual discount prompt after second successful scan.
- Offer Accelerator prompt when resume strength is below 70% or user has high match but low interview rate.

## 12. Email/SMS Notification Flows

Lifecycle emails:
- Day 0: Welcome and first scan CTA.
- Day 1: Resume readiness checklist.
- Day 3: Weekly high-fit matches.
- Day 5: Tailor before applying reminder.
- Day 7: Upgrade nudge with missed matches.
- Weekly: Match digest, salary trends, application follow-ups.

SMS/push:
- "High match detected: 86% Senior Cloud Platform Engineer at Ramp."
- "New $185k remote role matched your profile."
- "Be among the first 50 applicants."
- "Interview prep due tomorrow for your final-round role."

Slack/Discord/Telegram:
- Rich match card.
- Apply URL.
- Missing skills.
- Salary signal.
- Interview likelihood.

## 13. Dashboard Wireframes

Candidate Command Center:

```txt
[Hero: Career target + role lanes]
[Interviews Generated] [Applications Saved] [Salary Uplift] [Readiness Level]

Left column:
- Weekly focus
- Resume strength actions
- High-fit matches
- Follow-ups due

Right column:
- Shareable career insight
- Referral reward
- Alert performance
```

Match Detail:

```txt
[Job title/company] [Match %]
[Interview likelihood] [Salary signal] [Readiness score]
Why it fits
Why it may not
Missing skills
Matched skills
[Apply] [Track application] [Tailor resume]
```

## 14. Admin Analytics Concepts

Metrics:
- Signups.
- Profile completion.
- First scan completion.
- Matches viewed.
- Apply clicks.
- Applications tracked.
- Upgrade intents.
- Paid conversions.
- Alert engagement.
- Interview outcomes.
- Retention by cohort.

Cohorts:
- Role lane.
- Target salary.
- Plan.
- Source.
- Resume strength score.
- Alert-enabled vs alert-disabled.

## 15. Recruiter Platform Architecture

B2B features:
- Candidate semantic search.
- Resume ranking.
- Match explanations.
- Candidate fit scoring.
- Talent pipeline management.
- Recruiter dashboard.
- API access.
- White-label reports.

Architecture:
- Candidate resumes embedded in pgvector.
- Recruiter query embeds role requirements.
- Rank by semantic similarity, required skills, seniority, location, salary target, and availability.
- Store recruiter pipelines and candidate stage history.
- Generate client-ready fit reports.

B2B pricing:
- Recruiter: $399/seat/month.
- Agency: $1,499/month.
- Enterprise: custom API and white-label contract.

## 16. Exact Homepage Copy

Hero:
- Eyebrow: "AI Career Copilot for high-paying tech roles"
- Headline: "Land Better Tech Jobs Faster."
- Subhead: "Trovly AI scores $120k-$300k tech roles against your resume, explains the fit, tailors your materials, and alerts you before the applicant pile gets crowded."
- Primary CTA: "Start free career scan"
- Secondary CTA: "See premium plans"

Feature copy:
- "AI Resume Tailoring: Rewrite emphasis around the exact skills and outcomes each role is asking for."
- "ATS Optimization: Surface missing keywords, weak bullets, and role-specific phrasing before applying."
- "Match Explanations: See why a job fits, why it may not, what is missing, and how likely an interview is."
- "Salary Intelligence: Prioritize postings that align with your salary floor and total compensation goals."
- "Priority Alerts: Get notified when high-fit, newly posted, remote, or salary-aligned jobs appear."
- "Career Strategy: Turn your search data into weekly recommendations, readiness levels, and next actions."

## 17. Exact Pricing Page Copy

Free:
- "Validate fit before you spend hours applying."
- CTA: "Start free"

Pro:
- "$29/month"
- "For serious weekly searches targeting higher-quality roles."
- CTA: "Upgrade to Pro"
- Annual note: "Save 20% with annual billing"

Career Hunter:
- "$79/month"
- "For aggressive searches where speed, focus, and outreach matter."
- CTA: "Become a Career Hunter"
- Annual note: "Save 25% with annual billing"

Offer Accelerator:
- "$199 one-time"
- "A guided sprint to upgrade your entire job-search package."
- CTA: "Launch offer sprint"

## 18. Upgrade Prompts

- Scan limit: "You found the edge. Keep scanning. Upgrade to Pro for unlimited scans, match explanations, and priority alerts."
- Tailor limit: "Strong roles deserve tailored materials. Upgrade for unlimited resume tailoring, ATS optimization, and cover letter structure."
- High match: "High-fit role detected. Career Hunter adds recruiter targeting, priority alerts, and application analytics for roles like this."
- Offer sprint: "Turn your profile into an offer-ready package. The Offer Accelerator gives you a resume rewrite workflow, LinkedIn optimization, outreach templates, and interview prep."

## 19. Onboarding Flow

Step 1: Choose a career lane:
- Cloud / Platform.
- DevOps / DevSecOps.
- AI Engineering.
- Cybersecurity.

Step 2: Upload or paste resume.

Step 3: Confirm role queries.

Step 4: Set target salary.

Step 5: Set remote-first preference.

Step 6: Save profile and run first scan.

Step 7: Show first match explanation and prompt tailoring.

## 20. High-Converting CTA Copy

- "Start free career scan"
- "Stop applying blindly"
- "Unlock unlimited scans"
- "Tailor this resume"
- "See why this job fits"
- "Track this application"
- "Become a Career Hunter"
- "Launch offer sprint"
- "Get priority alerts"
- "Find my best-fit $150k+ roles"

## Suggested Folder Structure for Next.js Migration

```txt
apps/web/
  app/
    (public)/
      page.tsx
      pricing/page.tsx
      recruiters/page.tsx
      salary-trends/[role]/page.tsx
    app/
      page.tsx
      matches/page.tsx
      resume-ai/page.tsx
      applications/page.tsx
      alerts/page.tsx
      billing/page.tsx
    admin/
      page.tsx
    api/
      resumes/
      jobs/
      matches/
      alerts/
      billing/
      webhooks/
  components/
    pricing/
    matches/
    resume-ai/
    dashboard/
    alerts/
  lib/
    supabase.ts
    stripe.ts
    openai.ts
    embeddings.ts
    analytics.ts
    notifications.ts
  jobs/
    scan-jobs.ts
    send-alerts.ts
    weekly-digest.ts
    generate-content.ts
```

## Component Example

```tsx
export function MatchScoreCard({ match }) {
  return (
    <article className="rounded-lg border bg-white p-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase text-emerald-700">{match.job.company}</p>
          <h3 className="text-lg font-bold">{match.job.title}</h3>
          <p className="text-sm text-slate-600">{match.urgency}</p>
        </div>
        <div className="rounded-lg bg-slate-950 px-3 py-2 text-white">
          {Math.round(match.score * 100)}%
        </div>
      </div>
      <dl className="mt-4 grid grid-cols-3 gap-3 text-sm">
        <div><dt>Interview</dt><dd>{match.interviewProbability}%</dd></div>
        <div><dt>Salary</dt><dd>{match.salaryCompetitiveness}</dd></div>
        <div><dt>Readiness</dt><dd>{match.readinessScore}%</dd></div>
      </dl>
    </article>
  );
}
```

