import requests
from urllib.parse import quote


WIKI_LANGUAGES = ["zh", "en"]


def search_wikipedia_title(artist_name, language):
    search_url = f"https://{language}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": artist_name,
        "format": "json",
        "srlimit": 1,
    }
    headers = {
        "User-Agent": "ArtistExplorer/1.0"
    }

    response = requests.get(search_url, params=params, headers=headers, timeout=10)
    response.raise_for_status()

    results = response.json().get("query", {}).get("search", [])
    if not results:
        return None

    return results[0].get("title")


def get_wikipedia_summary(title, language):
    summary_url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
    headers = {
        "User-Agent": "ArtistExplorer/1.0"
    }

    response = requests.get(summary_url, headers=headers, timeout=10)
    response.raise_for_status()

    summary = response.json().get("extract", "").strip()
    if len(summary) < 30:
        return None

    return summary


def get_artist_bio(artist_name):
    for language in WIKI_LANGUAGES:
        try:
            title = search_wikipedia_title(artist_name, language)
            if not title:
                continue

            summary = get_wikipedia_summary(title, language)
            if summary:
                return summary
        except Exception:
            continue

    return "暫時無法取得生平簡介。"
