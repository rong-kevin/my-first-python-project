import re

import requests
from urllib.parse import quote


WIKI_LANGUAGES = ["zh", "en"]
MUSIC_KEYWORDS = [
    "歌手",
    "音樂",
    "音樂家",
    "藝人",
    "樂團",
    "饒舌",
    "rapper",
    "singer",
    "songwriter",
    "musician",
    "artist",
    "band",
    "record producer",
    "唱片",
]
DISAMBIGUATION_HINTS = [
    "may refer to",
    "can refer to",
    "可以指",
    "可能指",
    "消歧義",
]


def clean_wiki_text(text):
    text = re.sub(r"<.*?>", "", text or "")
    return text.strip()


def search_wikipedia_titles(artist_name, language):
    search_url = f"https://{language}.wikipedia.org/w/api.php"
    headers = {
        "User-Agent": "ArtistExplorer/1.0"
    }
    query_terms = {
        "zh": [f"{artist_name} 歌手", f"{artist_name} 音樂", artist_name],
        "en": [f"{artist_name} musician", f"{artist_name} singer", artist_name],
    }

    candidates = []
    seen_titles = set()

    for query in query_terms.get(language, [artist_name]):
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 5,
        }
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        for result in response.json().get("query", {}).get("search", []):
            title = result.get("title")
            if not title or title in seen_titles:
                continue

            seen_titles.add(title)
            candidates.append({
                "title": title,
                "snippet": clean_wiki_text(result.get("snippet", "")),
            })

    return candidates


def get_wikipedia_summary(title, language):
    summary_url = f"https://{language}.wikipedia.org/api/rest_v1/page/summary/{quote(title)}"
    headers = {
        "User-Agent": "ArtistExplorer/1.0"
    }

    response = requests.get(summary_url, headers=headers, timeout=10)
    response.raise_for_status()

    data = response.json()
    if data.get("type") == "disambiguation":
        return None

    summary = data.get("extract", "").strip()
    if len(summary) < 30:
        return None

    lowered_summary = summary.lower()
    if any(hint in lowered_summary for hint in DISAMBIGUATION_HINTS):
        return None

    return summary


def score_candidate(candidate, summary):
    text = f"{candidate.get('title', '')} {candidate.get('snippet', '')} {summary}".lower()
    score = 0

    for keyword in MUSIC_KEYWORDS:
        if keyword.lower() in text:
            score += 3

    title = candidate.get("title", "").lower()
    if "musician" in title or "singer" in title or "rapper" in title or "歌手" in title:
        score += 5

    if any(hint in text for hint in DISAMBIGUATION_HINTS):
        score -= 10

    return score


def get_artist_bio(artist_name):
    best_summary = None
    best_score = -1

    for language in WIKI_LANGUAGES:
        try:
            candidates = search_wikipedia_titles(artist_name, language)
        except Exception:
            continue

        for candidate in candidates:
            try:
                summary = get_wikipedia_summary(candidate["title"], language)
                if not summary:
                    continue

                score = score_candidate(candidate, summary)
                if score > best_score:
                    best_score = score
                    best_summary = summary
            except Exception:
                continue

    if best_summary and best_score > 0:
        return best_summary

    return "暫時無法取得生平簡介。"
