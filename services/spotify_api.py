import base64
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


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

    response = requests.post(url, headers=headers, data=data)
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

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()

    json_result = response.json()
    items = json_result.get("artists", {}).get("items", [])

    if not items:
        return None

    basic_artist = items[0]
    artist_id = basic_artist.get("id")

    detail_url = f"https://api.spotify.com/v1/artists/{artist_id}"
    detail_response = requests.get(detail_url, headers=headers)
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

    search_response = requests.get(search_url, headers=headers, params=params)
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
        params={"market": "TW"}
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

    search_response = requests.get(search_url, headers=headers, params=params)
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
        }
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
            "release_date": album.get("release_date", "無資料")
        })

    return result