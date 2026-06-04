import base64
import os
import random
from datetime import date
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
MIN_NEW_RELEASE_YEAR = date.today().year - 2


@lru_cache(maxsize=1)
def get_access_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(url, headers=headers, data=data, timeout=8)
    response.raise_for_status()

    return response.json()["access_token"]


def search_artist(artist_name):
    token = get_access_token()

    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }

    response = requests.get(search_url, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    json_result = response.json()
    items = json_result.get("artists", {}).get("items", [])

    if not items:
        return None

    basic_artist = items[0]
    artist_id = basic_artist.get("id")

    detail_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    detail_response = requests.get(detail_url, headers=headers, timeout=10)
    detail_response.raise_for_status()

    artist = detail_response.json()

    spotify_url = artist.get("external_urls", {}).get("spotify", "#")
    embed_url = spotify_url.replace("open.spotify.com/", "open.spotify.com/embed/") if spotify_url != "#" else "#"

    return {
        "name": artist.get("name", "無資料"),
        "followers": artist.get("followers", {}).get("total", "無資料"),
        "genres": artist.get("genres", []),
        "image": artist.get("images", [{}])[0].get("url") if artist.get("images") else None,
        "spotify_url": spotify_url,
        "embed_url": embed_url
    }


def fallback_artist_preview(artist_name):
    return {
        "name": artist_name,
        "image": None,
        "spotify_url": "#"
    }


def build_artist_preview(artist_name, token):
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }

    response = requests.get(search_url, headers=headers, params=params, timeout=4)
    response.raise_for_status()

    items = response.json().get("artists", {}).get("items", [])
    if not items:
        return fallback_artist_preview(artist_name)

    artist = items[0]
    return {
        "name": artist.get("name", artist_name),
        "image": artist.get("images", [{}])[0].get("url") if artist.get("images") else None,
        "spotify_url": artist.get("external_urls", {}).get("spotify", "#")
    }


@lru_cache(maxsize=64)
def get_artist_preview(artist_name):
    try:
        token = get_access_token()
        return build_artist_preview(artist_name, token)
    except Exception:
        return fallback_artist_preview(artist_name)


@lru_cache(maxsize=16)
def get_artist_previews_cached(artist_names):
    return tuple(get_artist_preview(artist_name) for artist_name in artist_names)


def get_artist_previews(artist_names):
    return list(get_artist_previews_cached(tuple(artist_names)))


def get_artist_top_tracks(artist_name):
    token = get_access_token()

    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }

    search_response = requests.get(search_url, headers=headers, params=params, timeout=10)
    search_response.raise_for_status()

    search_data = search_response.json()
    items = search_data.get("artists", {}).get("items", [])

    if not items:
        return []

    artist_id = items[0]["id"]

    top_tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    top_tracks_response = requests.get(
        top_tracks_url,
        headers=headers,
        params={"market": "TW"},
        timeout=10
    )
    top_tracks_response.raise_for_status()

    top_tracks_data = top_tracks_response.json()
    tracks = top_tracks_data.get("tracks", [])

    return [
        {
            "name": track.get("name", "無資料"),
            "album": track.get("album", {}).get("name", "無資料")
        }
        for track in tracks[:5]
    ]


def get_artist_albums(artist_name):
    token = get_access_token()

    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }

    search_response = requests.get(search_url, headers=headers, params=params, timeout=10)
    search_response.raise_for_status()

    search_data = search_response.json()
    items = search_data.get("artists", {}).get("items", [])

    if not items:
        return []

    artist_id = items[0]["id"]

    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    albums_response = requests.get(
        albums_url,
        headers=headers,
        params={
            "include_groups": "album,single",
            "limit": 10
        },
        timeout=10
    )
    albums_response.raise_for_status()

    albums_data = albums_response.json()
    albums = albums_data.get("items", [])

    result = []
    seen = set()

    for album in albums[:8]:
        album_name = album.get("name", "無資料")

        if album_name in seen:
            continue
        seen.add(album_name)

        result.append({
            "name": album_name,
            "release_date": album.get("release_date", "無資料"),
            "album_type": album.get("album_type", "album"),
            "spotify_url": album.get("external_urls", {}).get("spotify", "#")
        })

    return result


def get_artist_recent_singles(artist_name, limit=2):
    token = get_access_token()

    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": artist_name,
        "type": "artist",
        "limit": 1
    }

    search_response = requests.get(search_url, headers=headers, params=params, timeout=10)
    search_response.raise_for_status()

    items = search_response.json().get("artists", {}).get("items", [])
    if not items:
        return []

    artist = items[0]
    artist_id = artist["id"]
    resolved_artist_name = artist.get("name", artist_name)

    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    albums_response = requests.get(
        albums_url,
        headers=headers,
        params={
            "include_groups": "single",
            "limit": 10,
            "market": "TW"
        },
        timeout=10
    )
    albums_response.raise_for_status()

    songs = []
    seen = set()
    for album in albums_response.json().get("items", []):
        song_name = album.get("name")
        release_date = album.get("release_date", "")
        release_year = release_date[:4]
        if not song_name or song_name in seen:
            continue

        if not release_year.isdigit() or int(release_year) < MIN_NEW_RELEASE_YEAR:
            continue

        seen.add(song_name)
        songs.append({
            "name": song_name,
            "artist": resolved_artist_name,
            "release_date": release_date,
            "image": album.get("images", [{}])[0].get("url") if album.get("images") else None,
            "spotify_url": album.get("external_urls", {}).get("spotify", "#")
        })

        if len(songs) >= limit:
            break

    return songs


def get_new_song_recommendations(artist_names, count=6):
    token = get_access_token()
    search_url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    years = list(range(MIN_NEW_RELEASE_YEAR, date.today().year + 1))
    random.shuffle(years)
    recommendations = []
    seen = set()

    for year in years:
        try:
            response = requests.get(
                search_url,
                headers=headers,
                params={
                    "q": f"year:{year}",
                    "type": "track",
                    "market": "TW",
                    "limit": 30,
                    "offset": random.randint(0, 20)
                },
                timeout=10
            )
            response.raise_for_status()
        except Exception:
            continue

        tracks = response.json().get("tracks", {}).get("items", [])
        random.shuffle(tracks)

        for track in tracks:
            album = track.get("album", {})
            release_date = album.get("release_date", "")
            release_year = release_date[:4]
            song_name = track.get("name", "")
            artist_text = ", ".join(
                artist.get("name", "")
                for artist in track.get("artists", [])
                if artist.get("name")
            )

            if not release_year.isdigit() or int(release_year) < MIN_NEW_RELEASE_YEAR:
                continue

            key = (artist_text, song_name)
            if not artist_text or not song_name or key in seen:
                continue

            seen.add(key)
            recommendations.append({
                "name": song_name,
                "artist": artist_text,
                "release_date": release_date,
                "image": album.get("images", [{}])[0].get("url") if album.get("images") else None,
                "spotify_url": track.get("external_urls", {}).get("spotify", "#")
            })

            if len(recommendations) >= count:
                return recommendations

    return recommendations
