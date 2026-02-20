# #!/usr/bin/env python3
# """
# South Gloucestershire Council - Bin Collection Calendar Generator
# Fetches live bin collection dates and saves them as a .ics file.

# Your UPRN is read from an environment variable so it is never stored in the
# code. Set it as a GitHub Actions Secret, or export it locally before running:


# """

# import os
# import requests
# import json
# import uuid
# from datetime import datetime, timedelta
# from pathlib import Path

# # ─── CONFIGURATION ────────────────────────────────────────────────────────────
# # Read UPRN from environment variable — set as a GitHub Actions Secret
# # named SGC_UPRN, or export it in your terminal before running locally.
# UPRN = os.environ.get("SGC_UPRN", "").strip()

# OUTPUT_FILE = "docs/bin_collections.ics"   # served by GitHub Pages
# # ──────────────────────────────────────────────────────────────────────────────

# BIN_LABELS = {
#     "REFUSE":    "🗑️ Black Bin",
#     "RECYCLING": "♻️ Recycling",
#     "FOOD":      "🍎 Food Bin",
#     "GARDEN":    "🌿 Garden Waste",
# }

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (compatible; BinCalendarBot/1.0)",
#     "Accept": "application/json",
#     "Origin": "https://apps.southglos.gov.uk",
#     "Referer": "https://apps.southglos.gov.uk/",
# }


# def get_collections(uprn: str) -> list[dict]:
#     """Fetch bin collection dates from the SGC API."""
#     if not uprn:
#         raise ValueError(
#             "No UPRN supplied. Set SGC_UPRN as an environment variable "
#             "or GitHub Actions Secret."
#         )

#     url = "https://api.southglos.gov.uk/wastecomp/GetCollectionDetails"
#     params = {"uprn": uprn}

#     print("Fetching collection dates ...")
#     resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
#     resp.raise_for_status()
#     data = resp.json()

#     items = data.get("value", [])
#     if not items:
#         raise ValueError(
#             "No collection dates returned. The API may have changed.\n"
#             f"Raw response: {json.dumps(data, indent=2)[:500]}"
#         )

#     collections = []
#     for item in items:
#         raw_type = item.get("hso_servicename", "").strip().upper()
#         raw_date = item.get("hso_nextcollection", "")

#         if not raw_date:
#             continue

#         try:
#             # Date arrives as e.g. "2026-02-23T00:00:00+00:00"
#             collection_date = datetime.fromisoformat(raw_date).date()
#         except ValueError:
#             print(f"  Warning: couldn't parse date '{raw_date}' — skipping")
#             continue

#         collections.append({"type": raw_type, "date": collection_date})

#     # Deduplicate — same service/date can appear more than once
#     # (the API returns both a Task and a RoundLegInstance entry per service)
#     seen = set()
#     unique = []
#     for c in collections:
#         key = (c["type"], c["date"])
#         if key not in seen:
#             seen.add(key)
#             unique.append(c)

#     unique.sort(key=lambda x: x["date"])
#     print(f"Found {len(unique)} collection event(s).")
#     return unique


# def build_ics(collections: list[dict]) -> str:
#     """Build an iCalendar (.ics) string from collection events.
#     No address or identifying information is included in the output.
#     """
#     now = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
#     lines = [
#         "BEGIN:VCALENDAR",
#         "VERSION:2.0",
#         "PRODID:-//SGC Bin Calendar//EN",
#         "CALSCALE:GREGORIAN",
#         "METHOD:PUBLISH",
#         "X-WR-CALNAME:Bin Collections",
#         "X-WR-TIMEZONE:Europe/London",
#     ]

#     for item in collections:
#         raw_type = item["type"]
#         label = BIN_LABELS.get(raw_type, f"🗑 {raw_type.title()}")
#         d = item["date"]
#         date_str = d.strftime("%Y%m%d")

#         lines += [
#             "BEGIN:VEVENT",
#             f"UID:{uuid.uuid4()}@sgc-bin-calendar",
#             f"DTSTAMP:{now}",
#             f"DTSTART;VALUE=DATE:{date_str}",
#             f"DTEND;VALUE=DATE:{(d + timedelta(days=1)).strftime('%Y%m%d')}",
#             f"SUMMARY:{label}",
#             "DESCRIPTION:Put your bin out by 7am.",
#             "TRANSP:TRANSPARENT",
#             "BEGIN:VALARM",
#             "TRIGGER:-PT480M",
#             "ACTION:DISPLAY",
#             f"DESCRIPTION:Reminder: {label} collection tomorrow",
#             "END:VALARM",
#             "END:VEVENT",
#         ]

#     lines.append("END:VCALENDAR")
#     return "\r\n".join(lines)


# def main():
#     collections = get_collections(UPRN)

#     print("\n── Upcoming collections ──────────────────────────")
#     for item in collections:
#         label = BIN_LABELS.get(item["type"], item["type"].title())
#         print(f"  {item['date'].strftime('%a %d %b %Y')}  {label}")
#     print()

#     output_path = Path(OUTPUT_FILE)
#     output_path.parent.mkdir(parents=True, exist_ok=True)

#     ics_content = build_ics(collections)
#     output_path.write_text(ics_content, encoding="utf-8")
#     print(f"✅  Calendar saved to: {output_path.resolve()}")


# if __name__ == "__main__":
#     main()



# ----------------

#!/usr/bin/env python3
"""
Fetches bin collection dates from South Gloucestershire Council API
and generates a subscribable iCal file.
"""

import os
import requests
from datetime import datetime, timedelta, timezone
from icalendar import Calendar, Event
from pathlib import Path

# --- Config ---
UPRN = os.environ.get("SGC_UPRN", "").strip()
API_URL = f"https://api.southglos.gov.uk/wastecomp/GetCollectionDetails?uprn={UPRN}"
OUTPUT_PATH = Path("docs/bin_collections.ics")

# Emoji/labels for each service type
SERVICE_LABELS = {
    "Recycling": "♻️ Recycling collection",
    "Refuse":    "🗑️ Refuse (black bin) collection",
    "Food":      "🍎 Food waste collection",
    "Garden":    "🌿 Garden waste collection",
}

REMINDER_HOURS_BEFORE = 12  # Reminder the evening before


def fetch_collections():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    return response.json()


def build_calendar(collections):
    cal = Calendar()
    cal.add("prodid", "-//South Glos Bin Collections//EN")
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("x-wr-calname", "South Glos Bin Collections")
    cal.add("x-wr-timezone", "Europe/London")
    cal.add("refresh-interval;value=duration", "P1D")  # suggest daily refresh
    cal.add("x-published-ttl", "P1D")

    # The API returns one entry per service with hso_nextcollection date
    # We use the schedule description to project future dates too
    seen = set()

    for item in collections:
        service = item.get("hso_servicename", "Unknown")
        next_collection_str = item.get("hso_nextcollection")
        schedule = item.get("hso_scheduledescription", "")

        if not next_collection_str:
            continue

        next_date = datetime.fromisoformat(next_collection_str).date()
        label = SERVICE_LABELS.get(service, f"🗑️ {service} collection")

        # Determine recurrence interval from schedule description
        # e.g. "Monday every week" or "Monday every other week"
        if "every other week" in schedule.lower():
            interval_days = 14
        elif "every week" in schedule.lower():
            interval_days = 7
        else:
            interval_days = None  # single event only

        # Generate events: next collection + 26 weeks forward
        current_date = next_date
        weeks_ahead = 26
        end_date = next_date + timedelta(weeks=weeks_ahead)

        while current_date <= end_date:
            key = (service, current_date)
            if key not in seen:
                seen.add(key)
                event = Event()
                event.add("summary", label)
                event.add("dtstart", current_date)
                event.add("dtend", current_date + timedelta(days=1))
                event.add("description", f"Schedule: {schedule}\nRound: {item.get('hso_round', '')}")
                # UID ensures calendar apps update rather than duplicate
                uid = f"{service.lower()}-{current_date.isoformat()}@southglos-bins"
                event.add("uid", uid)
                event.add("dtstamp", datetime.now(timezone.utc))

                # Add a reminder alarm the evening before
                from icalendar import Alarm
                alarm = Alarm()
                alarm.add("action", "DISPLAY")
                alarm.add("description", f"Tomorrow: {label}")
                alarm.add("trigger", timedelta(hours=-(24 - REMINDER_HOURS_BEFORE)))
                event.add_component(alarm)

                cal.add_component(event)

            if interval_days:
                current_date += timedelta(days=interval_days)
            else:
                break

    return cal


def main():
    print(f"Fetching collection data for UPRN: {UPRN}")
    collections = fetch_collections()
    print(f"Got {len(collections)} services: {[c.get('hso_servicename') for c in collections]}")

    cal = build_calendar(collections)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_bytes(cal.to_ical())
    print(f"Written {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
