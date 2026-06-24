# Trovly AI Living Change Doc

Last updated: June 22, 2026

## One-Minute Summary

I repositioned Trovly AI from a broad "AI job search tool" into a focused career acceleration platform for mid-to-senior tech professionals targeting higher-paying roles.

The work combined product strategy, conversion-focused UX, SaaS planning, and practical engineering. I upgraded the public landing page, onboarding flow, match explanations, resume optimization experience, alert preferences, analytics surfaces, and recruiter-mode direction. I also added implementation docs and schema recommendations for scaling the product into a more production-grade SaaS architecture.

The goal was simple: make Trovly easier to sell, easier to understand, and more useful for people trying to land better tech jobs faster.

## Current Product Decision: Pricing Paused

On June 22, 2026, I removed the public pricing tiers, upgrade prompts, and plan-based limits because checkout was not connected yet. Leaving those controls visible created a dead-end experience: users could see an upgrade path but could not complete it.

Trovly is currently open-access while the core workflow is validated. The underlying billing and tier architecture remains available for a future Stripe integration, but it is no longer exposed to users prematurely.

Interview talking point:

> I treated pricing as a product workflow, not just a design section. Because payment was not connected, I removed the visible tiers and temporarily opened access. That avoided frustrating users while preserving the technical foundation for monetization later.

## Accessibility Pass: Button and Link Controls

On June 22, 2026, I audited the public landing page, authenticated app, and legacy dashboard for accessible interactive controls.

I added explicit ARIA labels to custom HTML links, accessible help descriptions to Streamlit buttons, contextual names for repeated actions like Apply and Track, visible keyboard focus outlines, and a separate Confirm delete action for destructive application removal.

I also added an automated regression test that checks every Streamlit button or link has a non-empty name and description, every custom HTML link has an `aria-label`, and every app surface retains visible `:focus-visible` styling.

Interview talking point:

> I treated accessibility as a testable product requirement. Streamlit provides native button semantics, so I kept those controls and strengthened their accessible names, descriptions, focus states, and context. I then added a regression test so future UI changes cannot silently remove those protections.

## Why This Change Was Needed

The original product already had strong technical foundations:

- Resume upload and parsing.
- Semantic job matching.
- Match scoring.
- Job discovery.
- Application tracking.
- Subscription logic.
- Alerting through Discord and Telegram.

The problem was not that the product lacked functionality. The problem was that the positioning was too broad. "AI job search tool" could mean almost anything, and that makes it harder to convert users, price the product, retain customers, and explain the value clearly.

So I narrowed the audience and made the product speak directly to users with higher willingness to pay:

- Cloud engineers.
- DevOps engineers.
- Platform engineers.
- AI engineers.
- Cybersecurity professionals.
- Remote-first senior candidates.
- Users targeting $120k-$300k roles.

## Product Strategy Shift

### Before

Trovly felt like a useful job scanner with AI matching.

### After

Trovly is positioned as an AI Career Copilot for landing high-paying tech jobs faster.

That shift matters because the product is no longer just helping users "find jobs." It is helping them:

- Get more interviews.
- Waste fewer applications.
- Prioritize better-fit roles.
- Improve their resume before applying.
- Target higher salaries.
- Move faster when strong roles appear.

## What I Changed

## 1. Landing Page and Messaging

I redesigned the public experience around a stronger SaaS narrative.

The new landing page includes:

- A focused hero section.
- Outcome-driven headline and subheadline.
- Match engine preview cards.
- Social proof metrics.
- "How it works" section.
- Premium feature grid.
- Resume optimization example.
- Testimonials.
- Salary success stories.
- FAQ.
- Final conversion CTA.

Example messaging:

- "Land Better Tech Jobs Faster."
- "AI Career Copilot for high-paying tech roles."
- "Stop applying blindly."
- "Start free career scan."

Interview talking point:

> I wanted the first screen to immediately show who the product is for, what outcome it drives, and why it is different from a generic job board. The match preview cards make the value tangible before a user even signs up.

## 2. Monetization Exploration and Product Judgment

I designed a possible revenue model with Free, Pro, Career Hunter, and Offer Accelerator offers. Before connecting billing, I recognized that presenting those tiers would create an incomplete user journey.

I therefore removed the visible pricing UI, upgrade buttons, paid-plan prompts, and artificial free-plan limits. The product is currently operating as open early access while I validate activation, engagement, and user outcomes.

The dormant tier configuration and Stripe-ready architecture are preserved so monetization can return as a complete workflow rather than a placeholder.

Interview talking point:

> I initially mapped pricing to customer urgency, then deliberately hid it until checkout and entitlement management are complete. That decision protected user trust and gave me time to validate which features actually deserve paid packaging.

## 3. Onboarding Flow

I upgraded onboarding so it asks for the details that matter to job-search outcomes:

- Resume upload or pasted resume.
- Career lane preset.
- Target roles.
- Target salary.
- Remote-first preference.
- Match threshold.

Career presets now include:

- Cloud / Platform.
- DevOps / DevSecOps.
- AI Engineering.
- Cybersecurity.

Interview talking point:

> The onboarding is designed to collect enough signal to personalize the product immediately. Instead of asking generic profile questions, it asks about role lane, salary target, and search preferences that directly affect matching and alerts.

## 4. Job Match Intelligence

I added a job intelligence layer that turns a basic match score into a more useful explanation.

For each matched job, the product can now show:

- Match percent.
- Matched skills.
- Missing skills.
- Why it fits.
- Why it may not fit.
- Interview probability.
- Salary competitiveness.
- Readiness score.
- Urgency message.

This was implemented in `job_intelligence.py`.

Technical explanation:

The current version uses deterministic logic on top of the existing semantic score. It combines the match score with extracted skills, salary parsing, remote indicators, seniority signals, and resume strength scoring. This gives users more context without requiring every explanation to call an external AI API.

Interview talking point:

> A raw score is not enough for users to make decisions. I added explainability so a user can understand not just that a job matched, but why it matched, what gaps exist, and whether it is worth applying to quickly.

## 5. Resume AI and ATS Optimization

The resume tailoring experience now presents itself as a premium workflow instead of a simple analyzer.

It shows:

- Resume relevance.
- ATS readiness.
- Keywords matched.
- Skill gaps.
- Strong bullets to emphasize.
- Moderate bullets to reword.
- Lower-priority bullets.
- Cover letter structure.

Interview talking point:

> This helps close the loop between discovery and action. Once a user finds a strong job, the product helps them improve the application instead of sending them away with just a link.

## 6. Alerts and Notifications

I expanded the alert strategy beyond Discord and Telegram.

The UI now supports preferences for:

- Email.
- SMS.
- Slack.
- Discord.
- Telegram.
- Push notifications.

Users can set alert rules for:

- High-fit roles.
- Salary-target matches.
- Remote roles.
- Interview likelihood thresholds.
- Newly posted jobs.

Example alert copy:

- "High match detected."
- "Be among the first 50 applicants."
- "New $185k remote role matched your profile."

Technical explanation:

The current production delivery still uses existing Discord and Telegram paths, but the product contract now supports more channels. I added `notification_engine.py` so future providers like SendGrid, Twilio, Slack, and push notifications can plug into the same preference model.

Interview talking point:

> I separated notification preferences from delivery. That lets the product design support multiple channels now, while giving engineering a clean path to add providers later.

## 7. Analytics and Retention

I added lightweight product analytics so the app can track funnel and usage behavior.

Tracked events include:

- Signup completed.
- Login completed.
- Profile saved.
- Scan completed.
- Tailor completed.
- Apply click.
- Application tracked.
- Alert preferences saved.
- Feature engagement and repeat usage.

The app now has an admin analytics tab with funnel and retention concepts.

Technical explanation:

The current version uses JSON-backed analytics because the app is still Streamlit-based. The recommended production path is to move this into Supabase/Postgres or a dedicated analytics tool like PostHog.

Interview talking point:

> I wanted to make the product measurable. If we cannot see activation, scan completion, apply clicks, and repeat engagement, we cannot improve conversion or retention intelligently.

## 8. Recruiter Mode

I added a B2B direction for recruiter and staffing use cases.

Recruiter Mode includes concepts for:

- Candidate semantic search.
- Resume ranking.
- Candidate fit explanations.
- Recruiter dashboard.
- Talent pipeline management.
- API access.
- White-label readiness.

Interview talking point:

> This creates a second monetization path. The same matching engine that helps candidates find jobs can help recruiters rank candidates against roles.

## 9. SEO and Content Engine

I added a concrete SEO/content strategy for future growth.

Content categories include:

- Remote AI jobs.
- Cloud engineering salaries.
- Best-paying DevOps roles.
- ATS optimization guides.
- Interview prep.
- Career pivots into AI.

The product plan recommends structured metadata and programmatic pages for salary trends, job trends, and hiring reports.

Interview talking point:

> The SEO strategy is tied to product data. Instead of publishing generic blog posts, Trovly can turn job-market data into useful salary pages, hiring reports, and role-specific guides.

## 10. Architecture and Scale Planning

I documented a production architecture path using:

- Next.js.
- Tailwind.
- Supabase/Postgres.
- pgvector embeddings.
- Stripe.
- OpenAI API.
- Background jobs.
- Redis caching.

I also created a recommended database schema in `docs/database_schema.sql`.

Important tables include:

- Profiles.
- Resumes.
- Resume versions.
- Jobs.
- Job embeddings.
- Matches.
- Applications.
- Alert preferences.
- Alert deliveries.
- Subscriptions.
- Referrals.
- Analytics events.
- Content pages.
- Recruiter accounts.
- Candidate profiles.

Interview talking point:

> I kept the current Streamlit app working, but documented how I would scale it into a more production-grade SaaS stack. The schema separates resumes, jobs, matches, alerts, billing, analytics, and recruiter workflows so the system can grow cleanly.

## Technical Choices I Can Explain

### Why keep Streamlit for now?

Because it already worked and let me move fast. For this phase, the goal was speed to revenue and clearer product value, not a full rewrite.

### Why centralize product copy?

I created `product_strategy.py` so landing page copy, feature language, testimonials, FAQs, alert channels, future monetization concepts, and SEO categories are not scattered across the app.

This makes the product easier to update and migrate later.

### Why add deterministic job intelligence?

It gives users useful explanations immediately without making every match dependent on an AI API call. Later, this can be upgraded with OpenAI-generated recommendations.

### Why add analytics now?

Because future monetization decisions need data. Even simple event tracking makes it possible to see where users activate, stall, or return for repeated use.

### Why add schema docs before migration?

Because the product direction now includes subscriptions, alerts, referrals, recruiter workflows, content pages, and embeddings. Planning the data model early reduces rework later.

## Files Changed or Added

Core app:

- `auth.py`: public landing page, improved auth messaging, signup analytics.
- `app_hosted.py`: Command Center, onboarding, scanning, resume AI, alerts, analytics, and recruiter mode.
- `usage_limits.py`: open early-access limits with dormant tier compatibility.
- `alerts.py`: premium alert messaging and match intelligence.

New modules:

- `product_strategy.py`: centralized copy, features, FAQs, testimonials, and future product concepts.
- `job_intelligence.py`: match explanations, salary parsing, interview probability, readiness score.
- `notification_engine.py`: alert preferences and channel templates.
- `analytics.py`: lightweight funnel and retention tracking.

Docs:

- `docs/trovly_career_acceleration_plan.md`: full product roadmap and architecture plan.
- `docs/database_schema.sql`: recommended Supabase/Postgres schema.
- `docs/interview_living_change_doc.md`: this interview-ready change doc.

Config:

- `.env.example`: added Stripe, email, SMS, Slack, and push notification environment variables.
- `config.example.py`: added future notification and billing secrets.
- `config.py.template`: added future notification and billing secrets.

## Validation

I verified the work with:

- Python syntax compilation.
- Ruff lint checks.
- Existing pytest suite.
- Browser render check of the Streamlit app.

Current verification results:

- `venv/bin/python -m py_compile ...` passed.
- `venv/bin/ruff check ...` passed.
- `venv/bin/python -m pytest -q` passed with 13 tests.
- Landing page rendered successfully at local Streamlit URL.

## How I Would Explain This in an Interview

### Short version

I took an AI-powered job matching app and turned it into a more focused career acceleration SaaS. The original product had useful matching and tracking features, but the audience and value proposition were too broad. I narrowed the ICP to mid-to-senior tech professionals targeting high-paying roles, rebuilt the landing and onboarding experience, added explainable match intelligence, improved resume optimization workflows, expanded alert preferences, added analytics, and documented a scalable architecture for moving from Streamlit to a production SaaS stack. I also removed the proposed pricing UI when I realized payment was not connected, keeping the experience honest while preserving the billing architecture for later.

### More technical version

The app was originally a Streamlit-based job scanner with semantic matching using sentence-transformers. I kept that core intact, then added a product strategy layer, match intelligence layer, notification preference layer, and lightweight analytics layer. The match intelligence module takes the existing semantic score and enriches it with skill overlap, missing skills, salary parsing, remote and seniority signals, interview probability, and resume readiness. I also documented a future Supabase/Postgres schema with pgvector so resumes and jobs can be embedded and searched at scale.

### Product-focused version

The biggest change was moving from feature-based positioning to outcome-based positioning. Instead of saying "AI job search tool," the product now says "AI Career Copilot for landing high-paying tech jobs faster." That makes the product easier to sell because it connects directly to interviews, offers, salary targets, and reduced wasted applications.

## STAR Interview Answer

### Situation

Trovly already had useful AI job matching features, but the product was positioned too broadly and did not have a clear premium monetization story.

### Task

I needed to sharpen the target customer, improve conversion, add monetizable premium features, and create a path toward a scalable SaaS architecture.

### Action

I repositioned the product around mid-to-senior tech professionals targeting $120k-$300k roles. I rebuilt the landing page, added role-specific onboarding, match explanations, resume optimization signals, alert preferences, analytics, recruiter-mode concepts, and a future database schema. I evaluated paid tiers but removed them from the live product until the billing workflow is complete.

### Result

The product now has a clearer ICP, stronger conversion copy, more actionable match results, better retention hooks, an honest open-access experience, and a documented path toward Stripe, Supabase, pgvector, notification providers, SEO content, and B2B recruiter monetization.

## Metrics I Would Track Next

- Signup conversion rate.
- Profile completion rate.
- First scan completion rate.
- Match view rate.
- Apply click rate.
- Resume tailoring usage.
- Alert opt-in rate.
- Repeat weekly usage.
- Weekly active users.
- Four-week retention.
- Interview rate by user cohort.
- Offer rate by user cohort.
- Average target salary.
- Retention by alert-enabled users.

## Next Improvements

The next highest-impact work would be:

1. Connect Stripe Checkout and webhooks.
2. Move user, job, match, and analytics data from JSON files to Supabase.
3. Add background jobs for scans, alerts, and weekly digests.
4. Add real email/SMS providers.
5. Persist match explanations and resume versions.
6. Add referral rewards and shareable career cards.
7. Launch SEO salary and remote job trend pages.
8. Build recruiter semantic search as a B2B revenue path.

## Personal Talking Points

- I made the product more commercially focused without throwing away the existing working code.
- I used product strategy to guide engineering decisions.
- I added explainability because users need to trust AI recommendations.
- I added analytics because SaaS growth needs measurable funnels.
- I planned the future architecture without prematurely rewriting the app.
- I focused on speed to revenue, retention, and clearer user outcomes.
