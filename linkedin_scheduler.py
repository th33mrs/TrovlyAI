"""
Trovly - LinkedIn Post Scheduler
Nudges you to post at optimal times.
"""

import argparse
import random
from datetime import datetime, timedelta


OPTIMAL_SLOTS = [
    (1, 7, 9, "Tuesday morning"),
    (1, 12, 13, "Tuesday lunch"),
    (1, 17, 18, "Tuesday evening"),
    (2, 7, 9, "Wednesday morning"),
    (2, 12, 13, "Wednesday lunch"),
    (2, 17, 18, "Wednesday evening"),
    (3, 7, 9, "Thursday morning"),
    (3, 12, 13, "Thursday lunch"),
    (3, 17, 18, "Thursday evening"),
]

POST_IDEAS = [
    "Share a feature you just built and why it matters",
    "Tell a story about a problem Trovly solves",
    "Compare Trovly to a competitor (one specific feature)",
    "Share a metric: scans run, users signed up, jobs surfaced",
    "Post a screenshot of the dashboard or a match result",
    "Ask your network a question about their job search experience",
    "Share something you learned while building this week",
    "Announce a new job source or integration",
    "Write about why you chose a specific technical approach",
    "Share user feedback (with permission) and what you changed",
]


def get_next_optimal_slot(now=None):
    if now is None:
        now = datetime.now()

    for days_ahead in range(8):
        check_date = now + timedelta(days=days_ahead)
        weekday = check_date.weekday()

        for slot_day, start_hr, end_hr, label in OPTIMAL_SLOTS:
            if slot_day != weekday:
                continue

            slot_start = check_date.replace(hour=start_hr, minute=0, second=0, microsecond=0)

            if days_ahead == 0 and slot_start <= now:
                continue

            return {
                "datetime": slot_start,
                "label": label,
                "hours_away": (slot_start - now).total_seconds() / 3600,
            }

    return None


def get_all_slots_this_week(now=None):
    if now is None:
        now = datetime.now()

    slots = []
    for days_ahead in range(8):
        check_date = now + timedelta(days=days_ahead)
        weekday = check_date.weekday()

        for slot_day, start_hr, end_hr, label in OPTIMAL_SLOTS:
            if slot_day != weekday:
                continue

            slot_start = check_date.replace(hour=start_hr, minute=0, second=0, microsecond=0)

            if slot_start <= now:
                continue

            slots.append({
                "datetime": slot_start,
                "label": label,
                "hours_away": (slot_start - now).total_seconds() / 3600,
            })

    return slots


def format_slot(slot):
    dt = slot["datetime"]
    hours = slot["hours_away"]

    if hours < 1:
        time_str = "in {} minutes".format(int(hours * 60))
    elif hours < 24:
        time_str = "in {:.1f} hours".format(hours)
    else:
        days = int(hours / 24)
        time_str = "in {} day{}".format(days, "s" if days != 1 else "")

    return "{} ({}) - {}".format(
        dt.strftime("%A %b %d at %-I:%M %p"),
        slot["label"],
        time_str,
    )


def print_post_idea():
    idea = random.choice(POST_IDEAS)
    print("\n  POST IDEA")
    print("  " + "-" * 60)
    print("    {}".format(idea))


def show_next():
    slot = get_next_optimal_slot()
    if not slot:
        print("No optimal slots found. Post anytime.")
        return

    print("\n" + "=" * 65)
    print("  NEXT OPTIMAL LINKEDIN POSTING SLOT")
    print("=" * 65)
    print()
    print("  {}".format(format_slot(slot)))
    print()

    if slot["hours_away"] < 2:
        print("  Time to post! Hit it now while engagement is highest.")
    elif slot["hours_away"] < 24:
        print("  Plan ahead - draft your post today, post then.")
    else:
        print("  Plenty of time to draft something thoughtful.")

    print_post_idea()
    print("\n" + "=" * 65)


def show_week():
    slots = get_all_slots_this_week()
    if not slots:
        print("No optimal slots this week.")
        return

    print("\n" + "=" * 65)
    print("  OPTIMAL LINKEDIN SLOTS - NEXT 7 DAYS")
    print("=" * 65)
    print()

    for i, slot in enumerate(slots[:9], 1):
        print("  {}. {}".format(i, format_slot(slot)))

    print_post_idea()
    print("\n  Best practices:")
    print("    - Post and reply to comments in the first hour")
    print("    - Hook in first 3 lines (mobile truncates)")
    print("    - Soft CTA, not a sales pitch")
    print("    - 1-2 hashtags max")
    print("    - Add a screenshot if relevant - 2x engagement")
    print("\n" + "=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Trovly LinkedIn Post Scheduler")
    parser.add_argument("--week", action="store_true", help="Show all slots this week")
    args = parser.parse_args()

    if args.week:
        show_week()
    else:
        show_next()


if __name__ == "__main__":
    main()
