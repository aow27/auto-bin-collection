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

REMINDER_HOURS_BEFORE = 8  # Reminder the evening before


def fetch_collections():
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return data["value"] 


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
