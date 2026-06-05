import os
from datetime import datetime, timedelta, timezone

import requests

TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
TICKETMASTER_BASE_URL = "https://app.ticketmaster.com/discovery/v2"


def ticketmaster_status(message, events=None):
    return {
        "events": events or [],
        "message": message
    }


def ticketmaster_get(path, params):
    if not TICKETMASTER_API_KEY:
        return None, "請在 .env 加上 TICKETMASTER_API_KEY"

    query = {
        "apikey": TICKETMASTER_API_KEY,
        **params
    }

    try:
        response = requests.get(f"{TICKETMASTER_BASE_URL}/{path}", params=query, timeout=10)
    except requests.RequestException as error:
        print(f"Ticketmaster request failed: {error}")
        return None, "Ticketmaster 暫時無法連線"

    if response.status_code in {401, 403}:
        return None, "Ticketmaster API key 尚未生效或未授權"

    if response.status_code == 404:
        return {}, None

    try:
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Ticketmaster request failed: {error}")
        return None, "Ticketmaster 查詢失敗"

    return response.json(), None


def format_ticketmaster_datetime(date_data):
    local_date = date_data.get("localDate")
    local_time = date_data.get("localTime")

    if local_date and local_time:
        return f"{local_date} {local_time[:5]}"

    return local_date or "日期未定"


def get_venue(event):
    venues = event.get("_embedded", {}).get("venues", [])
    return venues[0] if venues else {}


def normalize_event(event, artist_name):
    venue = get_venue(event)
    location = venue.get("location", {})
    latitude = location.get("latitude")
    longitude = location.get("longitude")

    return {
        "title": event.get("name") or artist_name,
        "date": format_ticketmaster_datetime(event.get("dates", {}).get("start", {})),
        "venue": venue.get("name") or "場館未定",
        "city": venue.get("city", {}).get("name") or "",
        "region": venue.get("state", {}).get("name") or "",
        "country": venue.get("country", {}).get("name") or "",
        "latitude": float(latitude) if latitude else None,
        "longitude": float(longitude) if longitude else None,
        "url": event.get("url") or "#"
    }


def get_attraction_ids(artist_name):
    data, error = ticketmaster_get("attractions.json", {
        "keyword": artist_name,
        "classificationName": "music",
        "size": 5
    })

    if error:
        return [], error

    attractions = data.get("_embedded", {}).get("attractions", []) if data else []
    return [attraction.get("id") for attraction in attractions if attraction.get("id")], None


def search_events(params, artist_name):
    data, error = ticketmaster_get("events.json", params)
    if error:
        return [], error

    events = data.get("_embedded", {}).get("events", []) if data else []
    return [normalize_event(event, artist_name) for event in events], None


def get_upcoming_concerts(artist_name):
    if not artist_name:
        return ticketmaster_status("請先輸入歌手名稱")

    today = datetime.now(timezone.utc)
    one_year_later = today + timedelta(days=365)
    date_params = {
        "classificationName": "music",
        "startDateTime": today.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "endDateTime": one_year_later.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sort": "date,asc",
        "size": 12
    }

    attraction_ids, attraction_error = get_attraction_ids(artist_name)
    if attraction_error:
        return ticketmaster_status(attraction_error)

    for attraction_id in attraction_ids:
        events, event_error = search_events({
            **date_params,
            "attractionId": attraction_id
        }, artist_name)

        if event_error:
            return ticketmaster_status(event_error)

        if events:
            return ticketmaster_status("Ticketmaster 已找到未來一年場次", events)

    events, keyword_error = search_events({
        **date_params,
        "keyword": artist_name
    }, artist_name)

    if keyword_error:
        return ticketmaster_status(keyword_error)

    if events:
        return ticketmaster_status("Ticketmaster 已找到未來一年場次", events)

    return ticketmaster_status("Ticketmaster 目前沒有這位歌手未來一年的公開場次")
