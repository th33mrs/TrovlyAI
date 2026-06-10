-- Trovly AI Supabase/Postgres schema recommendations
-- Enable pgvector in Supabase before running vector columns.

create extension if not exists vector;

create table profiles (
    id uuid primary key references auth.users(id) on delete cascade,
    email text not null,
    full_name text,
    plan text not null default 'free',
    target_salary integer not null default 150000,
    target_roles text[] not null default '{}',
    remote_only boolean not null default true,
    match_threshold numeric(4,3) not null default 0.55,
    onboarding_completed boolean not null default false,
    stripe_customer_id text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table resumes (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    source_filename text,
    raw_text text not null,
    parsed_json jsonb not null default '{}',
    embedding vector(1536),
    strength_score integer not null default 0,
    readiness_level text not null default 'Not started',
    is_primary boolean not null default true,
    created_at timestamptz not null default now()
);

create table resume_versions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    resume_id uuid not null references resumes(id) on delete cascade,
    job_id uuid,
    title text not null,
    tailored_text text not null,
    ats_score integer not null default 0,
    missing_skills text[] not null default '{}',
    created_at timestamptz not null default now()
);

create table jobs (
    id uuid primary key default gen_random_uuid(),
    external_uid text unique not null,
    source text not null,
    title text not null,
    company text not null,
    location text,
    remote boolean not null default false,
    salary_min integer,
    salary_max integer,
    posted_at timestamptz,
    url text not null,
    description text not null,
    normalized_skills text[] not null default '{}',
    created_at timestamptz not null default now()
);

create table job_embeddings (
    job_id uuid primary key references jobs(id) on delete cascade,
    embedding vector(1536) not null,
    created_at timestamptz not null default now()
);

create table matches (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    job_id uuid not null references jobs(id) on delete cascade,
    resume_id uuid references resumes(id) on delete set null,
    score numeric(5,4) not null,
    interview_probability integer not null,
    salary_competitiveness text not null,
    matched_skills text[] not null default '{}',
    missing_skills text[] not null default '{}',
    why_fit text[] not null default '{}',
    why_not text[] not null default '{}',
    urgency text,
    viewed_at timestamptz,
    dismissed_at timestamptz,
    created_at timestamptz not null default now(),
    unique(user_id, job_id, resume_id)
);

create table applications (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    match_id uuid references matches(id) on delete set null,
    job_id uuid references jobs(id) on delete set null,
    title text not null,
    company text not null,
    url text,
    salary text,
    status text not null default 'Applied',
    source text not null default 'manual',
    notes text,
    date_applied timestamptz not null default now(),
    last_updated timestamptz not null default now()
);

create table application_status_events (
    id uuid primary key default gen_random_uuid(),
    application_id uuid not null references applications(id) on delete cascade,
    status text not null,
    notes text,
    created_at timestamptz not null default now()
);

create table alert_preferences (
    user_id uuid primary key references profiles(id) on delete cascade,
    enabled boolean not null default true,
    channels jsonb not null default '{"email": true, "sms": false, "slack": false, "discord": true, "telegram": true, "push": true}',
    min_match numeric(4,3) not null default 0.72,
    min_interview_probability integer not null default 55,
    salary_target_only boolean not null default false,
    remote_only boolean not null default true,
    newly_posted_only boolean not null default false,
    updated_at timestamptz not null default now()
);

create table alert_deliveries (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    match_id uuid references matches(id) on delete cascade,
    channel text not null,
    subject text,
    body text,
    status text not null default 'queued',
    provider_message_id text,
    sent_at timestamptz,
    opened_at timestamptz,
    clicked_at timestamptz,
    created_at timestamptz not null default now()
);

create table subscriptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references profiles(id) on delete cascade,
    stripe_customer_id text not null,
    stripe_subscription_id text,
    plan text not null,
    status text not null,
    interval text,
    current_period_end timestamptz,
    cancel_at_period_end boolean not null default false,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table referrals (
    id uuid primary key default gen_random_uuid(),
    referrer_user_id uuid not null references profiles(id) on delete cascade,
    referred_user_id uuid references profiles(id) on delete set null,
    code text not null,
    status text not null default 'pending',
    reward text,
    created_at timestamptz not null default now(),
    redeemed_at timestamptz
);

create table analytics_events (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references profiles(id) on delete set null,
    event text not null,
    properties jsonb not null default '{}',
    created_at timestamptz not null default now()
);

create table content_pages (
    id uuid primary key default gen_random_uuid(),
    slug text unique not null,
    category text not null,
    title text not null,
    meta_description text not null,
    body_md text not null,
    structured_metadata jsonb not null default '{}',
    published_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create table recruiter_accounts (
    id uuid primary key default gen_random_uuid(),
    company_name text not null,
    plan text not null default 'recruiter',
    stripe_customer_id text,
    created_at timestamptz not null default now()
);

create table recruiter_users (
    recruiter_account_id uuid not null references recruiter_accounts(id) on delete cascade,
    user_id uuid not null references profiles(id) on delete cascade,
    role text not null default 'member',
    primary key (recruiter_account_id, user_id)
);

create table candidate_profiles (
    id uuid primary key default gen_random_uuid(),
    recruiter_account_id uuid not null references recruiter_accounts(id) on delete cascade,
    resume_id uuid references resumes(id) on delete set null,
    name text,
    email text,
    current_title text,
    target_roles text[] not null default '{}',
    target_salary integer,
    location text,
    remote_preference text,
    embedding vector(1536),
    created_at timestamptz not null default now()
);

create table recruiter_pipelines (
    id uuid primary key default gen_random_uuid(),
    recruiter_account_id uuid not null references recruiter_accounts(id) on delete cascade,
    name text not null,
    role_description text not null,
    created_at timestamptz not null default now()
);

create table recruiter_pipeline_candidates (
    pipeline_id uuid not null references recruiter_pipelines(id) on delete cascade,
    candidate_id uuid not null references candidate_profiles(id) on delete cascade,
    fit_score numeric(5,4) not null,
    stage text not null default 'sourced',
    fit_explanation jsonb not null default '{}',
    created_at timestamptz not null default now(),
    primary key (pipeline_id, candidate_id)
);

create index matches_user_score_idx on matches(user_id, score desc);
create index jobs_company_title_idx on jobs(company, title);
create index jobs_posted_at_idx on jobs(posted_at desc);
create index applications_user_status_idx on applications(user_id, status);
create index analytics_events_user_event_idx on analytics_events(user_id, event, created_at desc);
create index content_pages_category_idx on content_pages(category);
create index candidate_profiles_embedding_idx on candidate_profiles using ivfflat (embedding vector_cosine_ops);
create index job_embeddings_embedding_idx on job_embeddings using ivfflat (embedding vector_cosine_ops);

