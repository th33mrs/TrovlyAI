# Trovly AI

AI Career Copilot for landing high-paying tech jobs faster.

Trovly AI helps mid-to-senior tech professionals target better roles, waste fewer applications, and move faster toward interviews and offers. It monitors job sources, compares postings against your resume with semantic matching, explains fit and gaps, supports resume tailoring, tracks applications, and sends alerts for high-fit roles.

Built for cloud engineers, DevOps engineers, platform engineers, AI engineers, cybersecurity professionals, and remote-first candidates targeting $120k-$300k roles.

## Architecture

```txt
config.py               -> Settings, API keys, resume text, thresholds
sources.py              -> Job source plugins
matcher.py              -> Sentence-transformer cosine similarity engine
job_intelligence.py     -> Fit explanations, salary signal, interview likelihood
tailor.py               -> Resume tailoring and ATS keyword analysis
notification_engine.py  -> Alert preferences and channel templates
analytics.py            -> Funnel, usage, and retention event tracking
alerts.py               -> Discord and Telegram delivery
app_hosted.py           -> Hosted Streamlit SaaS app
main.py                 -> Scheduler, deduplication, CLI entry point
```

## Quick Start

```bash
# 1. Create venv
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Edit config.py or use the hosted app onboarding:
#    - Paste/upload your resume
#    - Set SEARCH_QUERIES for your target roles
#    - Set a salary floor for the roles you want
#    - Add API keys (Adzuna is free, Remotive/Arbeitnow need no keys)
#    - Add Discord webhook URL and/or Telegram bot token for alerts

# 4. Run diagnostic first to tune your threshold
python main.py --stats

# 5. Single scan test
python main.py --once

# 6. Run on schedule (every 30 min by default)
python main.py
```

## Tuning the Threshold

85% is aggressive. Run `--stats` first to see your score distribution. If you get zero matches, try lowering to 0.60-0.70 and work up. Semantic similarity at 0.85 means "nearly identical topic and skill set" — most real job matches land in 0.55-0.80.

**Recommended approach:**
1. Start with `SIMILARITY_THRESHOLD = 0.55`
2. Run `--stats`, examine the histogram
3. Raise the threshold until you're getting 5-15 matches per scan

## Alert Channels

The current delivery layer supports Discord and Telegram. The product UI and configuration template now include email, SMS, Slack, Discord, Telegram, and push preferences so production adapters can be connected without changing the user-facing contract.

### Discord
1. Open your Discord server
2. Channel Settings → Integrations → Webhooks → New Webhook
3. Copy the webhook URL into `config.py`

### Telegram
1. Message @BotFather on Telegram → `/newbot` → follow prompts
2. Copy the bot token into `config.py`
3. Message @userinfobot to get your chat ID
4. Copy your chat ID into `config.py`

## Running as a Background Service

### tmux / screen
```bash
tmux new -s jobscan
python main.py
# Ctrl+B, D to detach
```

### systemd (Linux)
```ini
# /etc/systemd/system/jobscanner.service
[Unit]
Description=Job Scanner Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/job_scanner
ExecStart=/path/to/job_scanner/venv/bin/python main.py
Restart=on-failure
RestartSec=60

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable jobscanner
sudo systemctl start jobscanner
```

## Adding New Job Sources

Create a function in `sources.py`:

```python
def fetch_my_source(queries: list[str]) -> list[JobPosting]:
    jobs = []
    # ... fetch logic ...
    jobs.append(JobPosting(
        title="...", company="...", description="...",
        url="...", source="my_source", uid="my_source:unique_id"
    ))
    return jobs
```

Then register it in `SOURCE_MAP` and `ENABLED_SOURCES`.

## CLI Reference

| Command | Description |
|---|---|
| `python main.py` | Run continuous scanner (default 30 min interval) |
| `python main.py --once` | Single scan, then exit |
| `python main.py --stats` | Score distribution diagnostic |
| `python main.py --reset` | Clear seen-jobs database |

## Growth and Monetization Plan

See `docs/trovly_career_acceleration_plan.md` for the full roadmap, homepage copy, future monetization strategy, onboarding flows, SEO engine, notification flows, dashboard wireframes, admin analytics, and recruiter platform architecture.

See `docs/database_schema.sql` for the recommended Supabase/Postgres schema with pgvector.
