import os
from datetime import datetime, timedelta, timezone

import requests

BANDSINTOWN_APP_ID = os.getenv("BANDSINTOWN_APP_ID", "my-first-python-project")


def parse_event_datetime(value):
    if not value:
        return None

    normalized_value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized_value)
    except ValueError:
        return None


def format_event_date(event_datetime):
    if not event_datetime:
        return "日期未定"

    return event_datetime.strftime("%Y-%m-%d")


def get_upcoming_concerts(artist_name):
    if not artist_name:
        return []

    url = f"https://rest.bandsintown.com/artists/{artist_name}/events"
    params = {
        "app_id": BANDSINTOWN_APP_ID
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Bandsintown events unavailable for {artist_name}: {error}")
        return []

    today = datetime.now(timezone.utc)
    one_year_later = today + timedelta(days=365)
    concerts = []

    for event in response.json():
        event_datetime = parse_event_datetime(event.get("datetime"))
        if not event_datetime:
            continue

        if event_datetime.tzinfo is None:
            event_datetime = event_datetime.replace(tzinfo=timezone.utc)

        if event_datetime < today or event_datetime > one_year_later:
            continue

        venue = event.get("venue", {})
        latitude = venue.get("latitude")
        longitude = venue.get("longitude")

        concerts.append({
            "title": event.get("title") or artist_name,
            "date": format_event_date(event_datetime),
            "venue": venue.get("name") or "場館未定",
            "city": venue.get("city") or "",
            "region": venue.get("region") or "",
            "country": venue.get("country") or "",
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "url": event.get("url") or "#"
        })

    concerts.sort(key=lambda concert: concert["date"])
    return concerts[:12]
