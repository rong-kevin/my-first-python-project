import os
from datetime import datetime, timedelta, timezone

import requests

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")


def parse_event_datetime(value):
    if not value:
        return None

    normalized_value = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized_value)
    except ValueError:
        return None


def format_ticketmaster_datetime(date_data):
    local_date = date_data.get("localDate")
    local_time = date_data.get("localTime")

    if local_date and local_time:
        return f"{local_date} {local_time[:5]}"

    return local_date or "日期未定"


def get_venue(event):
    venues = event.get("_embedded", {}).get("venues", [])
    return venues[0] if venues else {}


def get_upcoming_concerts(artist_name):
    if not artist_name or not TICKETMASTER_API_KEY:
        return []

    today = datetime.now(timezone.utc)
    one_year_later = today + timedelta(days=365)

    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    params = {
        "apikey": TICKETMASTER_API_KEY,
        "keyword": artist_name,
        "classificationName": "music",
        "startDateTime": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": one_year_later.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sort": "date,asc",
        "size": 12
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Ticketmaster events unavailable for {artist_name}: {error}")
        return []

    events = response.json().get("_embedded", {}).get("events", [])
    concerts = []

    for event in events:
        venue = get_venue(event)
        location = venue.get("location", {})
        latitude = location.get("latitude")
        longitude = location.get("longitude")
        city = venue.get("city", {}).get("name") or ""
        region = venue.get("state", {}).get("name") or ""
        country = venue.get("country", {}).get("name") or ""

        concerts.append({
            "title": event.get("name") or artist_name,
            "date": format_ticketmaster_datetime(event.get("dates", {}).get("start", {})),
            "venue": venue.get("name") or "場館未定",
            "city": city,
            "region": region,
            "country": country,
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "url": event.get("url") or "#"
        })

    return concerts
