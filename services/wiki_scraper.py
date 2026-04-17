import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def get_artist_bio(artist_name):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    candidate_urls = [
        f"https://en.wikipedia.org/wiki/{quote(artist_name.replace(' ', '_'))}",
        f"https://zh.wikipedia.org/wiki/{quote(artist_name.replace(' ', '_'))}",
    ]

    for url in candidate_urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            content = soup.select_one("div.mw-parser-output")
            if not content:
                continue

            paragraphs = content.find_all("p", recursive=False)

            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 30:
                    return text

        except Exception:
            continue

    return "暫時無法取得生平簡介。"