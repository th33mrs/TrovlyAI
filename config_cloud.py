"""Trovly - Cloud Config (no secrets)"""

RESUME_TEXT = "placeholder"
BOOST_KEYWORDS = []
BOOST_WEIGHT = 0.05
SIMILARITY_THRESHOLD = 0.55
SEARCH_QUERIES = []
LOCATION = ""
REMOTE_ONLY = True
SCAN_INTERVAL_MINUTES = 1440

DISCORD_WEBHOOK_URL = ""
TELEGRAM_BOT_TOKEN = ""
TELEGRAM_CHAT_ID = ""
SLACK_WEBHOOK_URL = ""
SENDGRID_API_KEY = ""
EMAIL_FROM = ""
TWILIO_ACCOUNT_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_FROM_NUMBER = ""
PUSH_VAPID_PUBLIC_KEY = ""
PUSH_VAPID_PRIVATE_KEY = ""

STRIPE_SECRET_KEY = ""
STRIPE_WEBHOOK_SECRET = ""
STRIPE_PRO_PRICE_ID = ""
STRIPE_CAREER_HUNTER_PRICE_ID = ""
STRIPE_OFFER_ACCELERATOR_PRICE_ID = ""

ENABLED_SOURCES = {
    "adzuna": False,
    "remotive": True,
    "arbeitnow": True,
    "usajobs": False,
    "the_muse": True,
    "jobicy": True,
    "lennys_jobs": True,
    "himalayas": True,
    "rss_feeds": True,
}
LENNYS_JOBS_HITS_PER_QUERY = 20

ADZUNA_APP_ID = ""
ADZUNA_APP_KEY = ""
ADZUNA_COUNTRY = "us"
USAJOBS_API_KEY = ""
USAJOBS_EMAIL = ""

RSS_FEEDS = [
    "https://weworkremotely.com/categories/remote-back-end-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-full-stack-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
]

SECTION_WEIGHTS = {}
DEFAULT_SECTION_WEIGHT = 1.0
NEGATIVE_KEYWORDS = []
SALARY_FLOOR = 0

SEEN_JOBS_DB = "seen_jobs.json"
MAX_POST_AGE_DAYS = 30
LOG_FILE = "trovly.log"

GREENHOUSE_COMPANIES = [
    "stripe", "airbnb", "discord", "reddit", "notion", "anthropic",
    "coinbase", "instacart", "doordash", "robinhood", "figma", "asana",
]
LEVER_COMPANIES = ["plaid", "github", "netflix", "mixpanel", "twitch", "loom", "intercom"]
ASHBY_COMPANIES = ["linear", "vanta", "ramp", "openai", "perplexity", "deel", "supabase"]

ENABLED_SOURCES["greenhouse"] = True
ENABLED_SOURCES["lever"] = True
ENABLED_SOURCES["ashby"] = True
ENABLED_SOURCES["himalayas_api"] = True
ENABLED_SOURCES["working_nomads"] = True
