import os
import requests
from dotenv import load_dotenv

load_dotenv()

LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")


def get_similar_artists(artist_name):
    if not LASTFM_API_KEY:
        return []

    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getsimilar",
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        artists = data.get("similarartists", {}).get("artist", [])

        result = []
        for artist in artists[:8]:
            result.append(artist.get("name", "無資料"))

        return result
    except Exception:
        return []

def get_artist_tags(artist_name):
    if not LASTFM_API_KEY:
        return []

    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getTopTags",
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        tags = data.get("toptags", {}).get("tag", [])

        result = []
        for tag in tags[:5]:
            name = tag.get("name")
            if name:
                result.append(name)

        return result
    except Exception:
        return []

    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getTopTags",
        "artist": artist_name,
        "api_key": LASTFM_API_KEY,
        "format": "json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()
    tags = data.get("toptags", {}).get("tag", [])

    result = []
    for tag in tags[:5]:
        name = tag.get("name")
        if name:
            result.append(name)

    return result