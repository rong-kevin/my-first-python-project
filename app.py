import os
import random
from collections import Counter
from itertools import combinations

from flask import Flask, render_template, request, redirect, session, url_for
from services.spotify_api import search_artist, get_artist_albums, get_artist_previews
from services.lastfm_api import get_similar_artists, get_artist_tags
from services.wiki_scraper import get_artist_bio

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "artist-explorer-dev-secret")

POPULAR_ARTISTS = [
    "Taylor Swift",
    "周杰倫",
    "NewJeans",
    "Laufey",
    "告五人",
    "YOASOBI",
    "Billie Eilish",
    "Ariana Grande",
    "The Weeknd",
    "林俊傑",
    "落日飛車",
    "Dua Lipa"
]

DISCOVER_FILTERS = {
    "mandarin": {
        "label": "中文歌手",
        "description": "華語流行、抒情與樂團作品，適合想聽中文歌詞和熟悉語感時。",
        "artists": ["周杰倫", "林俊傑", "田馥甄", "告五人", "落日飛車", "林宥嘉", "孫燕姿", "蔡依林", "韋禮安", "五月天"],
        "tags": ["Mandopop", "中文", "抒情", "樂團"]
    },
    "english": {
        "label": "英文歌手",
        "description": "從流行到創作歌手，適合想探索英文主流與個人風格強烈的音樂人。",
        "artists": ["Taylor Swift", "Ed Sheeran", "Adele", "Billie Eilish", "Bruno Mars", "Dua Lipa", "Olivia Rodrigo", "Harry Styles", "Ariana Grande", "Coldplay"],
        "tags": ["pop", "singer-songwriter", "ballad"]
    },
    "korean": {
        "label": "韓文 / K-pop",
        "description": "節奏感、舞台感與流行製作完整，適合想聽韓文或高能量歌曲時。",
        "artists": ["NewJeans", "BLACKPINK", "IVE", "IU", "BTS", "LE SSERAFIM", "TWICE", "SEVENTEEN", "aespa", "Stray Kids"],
        "tags": ["K-pop", "dance", "idol", "韓文"]
    },
    "japanese": {
        "label": "日文 / J-pop",
        "description": "旋律線鮮明、情緒細膩，適合想聽日文流行、動畫感或城市感音樂時。",
        "artists": ["YOASOBI", "Aimer", "Vaundy", "椎名林檎", "米津玄師", "宇多田光", "King Gnu", "Official Hige Dandism", "藤井風", "Aimyon"],
        "tags": ["J-pop", "日文", "anime", "city pop"]
    },
    "rnb": {
        "label": "R&B / 深夜感",
        "description": "聲線柔和、節奏放鬆，適合深夜、放空或想聽氛圍感時。",
        "artists": ["SZA", "Frank Ocean", "Daniel Caesar", "The Weeknd", "Keshi", "HONNE", "H.E.R.", "Khalid", "Giveon", "Summer Walker"],
        "tags": ["R&B", "soul", "slow", "night"]
    },
    "indie": {
        "label": "Indie / 樂團感",
        "description": "帶有獨立音樂與現場感，適合想聽不那麼商業、比較有個性的聲音。",
        "artists": ["deca joins", "No Party For Cao Dong", "Men I Trust", "Beach House", "Bon Iver", "Radiohead", "The 1975", "Arctic Monkeys", "Cigarettes After Sex", "Vampire Weekend"],
        "tags": ["indie", "band", "dream pop", "alternative"]
    },
    "dance": {
        "label": "舞曲 / 健身",
        "description": "鼓點明確、能量高，適合派對、運動或需要讓精神上線時。",
        "artists": ["Calvin Harris", "Doja Cat", "Travis Scott", "Ariana Grande", "Post Malone", "Imagine Dragons", "David Guetta", "The Chainsmokers", "Martin Garrix", "Rihanna"],
        "tags": ["dance", "edm", "hip-hop", "workout"]
    },
    "acoustic": {
        "label": "Acoustic / 放鬆",
        "description": "編曲簡單、聲音溫暖，適合讀書、睡前或需要降低壓力時。",
        "artists": ["Laufey", "Norah Jones", "Rex Orange County", "Mac Ayres", "HYBS", "Wave to Earth", "Jack Johnson", "John Mayer", "beabadoobee", "Novo Amor"],
        "tags": ["acoustic", "soft", "jazz pop", "chill"]
    }
}

MOOD_RECOMMENDATIONS = {
    "study": {
        "label": "讀書 / 寫作業",
        "description": "節奏穩定、旋律舒服，適合需要專心但不想太安靜的時候。",
        "artists": ["Laufey", "IU", "Keshi", "Jay Chou", "Norah Jones", "Rex Orange County", "Mac Ayres", "FKJ", "林宥嘉", "HYBS"],
        "tags": ["lo-fi", "acoustic", "r&b", "soft pop"]
    },
    "workout": {
        "label": "運動 / 健身",
        "description": "節奏強、能量高，適合跑步、重訓或需要提振精神。",
        "artists": ["Dua Lipa", "BLACKPINK", "Travis Scott", "The Weeknd", "Bruno Mars", "Doja Cat", "Imagine Dragons", "Calvin Harris", "IVE", "Post Malone"],
        "tags": ["dance pop", "hip-hop", "edm", "k-pop"]
    },
    "commute": {
        "label": "通勤 / 走路",
        "description": "旋律好入口、情緒不太重，適合在路上輕鬆聽。",
        "artists": ["Ed Sheeran", "NewJeans", "告五人", "Ariana Grande", "Maroon 5", "Charlie Puth", "Vaundy", "Coldplay", "YOASOBI", "OneRepublic"],
        "tags": ["pop", "indie", "easy listening"]
    },
    "sad": {
        "label": "失戀 / 難過",
        "description": "歌詞情緒感強，適合想整理心情或被音樂陪伴的時候。",
        "artists": ["Adele", "Taylor Swift", "田馥甄", "Joji", "Olivia Rodrigo", "Sam Smith", "Lewis Capaldi", "林俊傑", "Phoebe Bridgers", "Conan Gray"],
        "tags": ["ballad", "sad pop", "singer-songwriter"]
    },
    "night": {
        "label": "睡前 / 深夜",
        "description": "聲音柔和、氛圍放鬆，適合睡前、深夜或一個人放空。",
        "artists": ["Frank Ocean", "Billie Eilish", "Aimer", "SZA", "Cigarettes After Sex", "Daniel Caesar", "The 1975", "HONNE", "beabadoobee", "Wave to Earth"],
        "tags": ["jazz pop", "r&b", "ambient", "slow"]
    },
    "rainy": {
        "label": "下雨天",
        "description": "帶一點電影感和情緒厚度，適合雨天、咖啡廳或窗邊時間。",
        "artists": ["deca joins", "Lana Del Rey", "Bon Iver", "Radiohead", "落日飛車", "No Party For Cao Dong", "Men I Trust", "Beach House", "椎名林檎", "Sufjan Stevens"],
        "tags": ["indie", "city pop", "ballad", "dream pop"]
    }
}


def recommendation_key(artists):
    return "|".join(sorted(artists))


def pick_recommendation_artists(session_key, group_key, candidates, count=5):
    used_by_group = session.get(session_key, {})
    used_keys = set(used_by_group.get(group_key, []))
    candidate_combinations = list(combinations(candidates, min(count, len(candidates))))
    unused_combinations = [
        combo for combo in candidate_combinations
        if recommendation_key(combo) not in used_keys
    ]

    if not unused_combinations:
        used_keys = set()
        unused_combinations = candidate_combinations

    selected_artists = list(random.choice(unused_combinations))
    random.shuffle(selected_artists)
    used_keys.add(recommendation_key(selected_artists))
    used_by_group[group_key] = list(used_keys)
    session[session_key] = used_by_group
    return selected_artists


def build_mood_recommendation(mood_key):
    mood = MOOD_RECOMMENDATIONS.get(mood_key)
    if not mood:
        return None

    recommendation = mood.copy()
    recommendation["artists"] = pick_recommendation_artists(
        "used_mood_recommendations",
        mood_key,
        mood["artists"]
    )
    return recommendation


def build_discover_recommendation(filter_key):
    filter_data = DISCOVER_FILTERS.get(filter_key)
    if not filter_data:
        return None

    recommendation = filter_data.copy()
    recommendation["artists"] = pick_recommendation_artists(
        "used_discover_recommendations",
        filter_key,
        filter_data["artists"]
    )
    return recommendation


@app.route("/")
def home():
    popular_artist_cards = get_artist_previews(POPULAR_ARTISTS)
    return render_template(
        "index.html",
        popular_artists=POPULAR_ARTISTS,
        popular_artist_cards=popular_artist_cards
    )


@app.route("/random")
def random_artist():
    artist_name = random.choice(POPULAR_ARTISTS)
    return redirect(url_for("artist_page", name=artist_name))


@app.route("/mood")
def mood_page():
    selected_mood = request.args.get("type", "").strip()
    selected_recommendation = build_mood_recommendation(selected_mood)

    return render_template(
        "mood.html",
        moods=MOOD_RECOMMENDATIONS,
        selected_mood=selected_mood,
        selected_recommendation=selected_recommendation
    )


@app.route("/discover")
def discover_page():
    selected_filter = request.args.get("type", "").strip()
    selected_recommendation = build_discover_recommendation(selected_filter)

    return render_template(
        "discover.html",
        filters=DISCOVER_FILTERS,
        selected_filter=selected_filter,
        selected_recommendation=selected_recommendation
    )


@app.route("/artist")
def artist_page():
    artist_name = request.args.get("name", "").strip()

    if not artist_name:
        return render_template(
            "artist.html",
            error="請先輸入歌手名稱"
        )

    try:
        artist = search_artist(artist_name)

        if not artist:
            return render_template(
                "artist.html",
                error="找不到這位歌手"
            )

        albums = get_artist_albums(artist_name)
        similar_artists = get_similar_artists(artist_name)
        artist_tags = get_artist_tags(artist_name)
        artist_bio = get_artist_bio(artist_name)

        album_years = []
        single_years = []
        for album in albums:
            release_date = album.get("release_date", "")
            album_type = album.get("album_type", "album")
            if release_date:
                year = release_date[:4]
                if year.isdigit():
                    if album_type == "single":
                        single_years.append(year)
                    else:
                        album_years.append(year)

        album_counts = Counter(album_years)
        single_counts = Counter(single_years)
        chart_labels = sorted(set(album_counts.keys()) | set(single_counts.keys()))
        album_chart_values = [album_counts[year] for year in chart_labels]
        single_chart_values = [single_counts[year] for year in chart_labels]

        return render_template(
            "artist.html",
            artist=artist,
            albums=albums,
            similar_artists=similar_artists,
            artist_tags=artist_tags,
            artist_bio=artist_bio,
            chart_labels=chart_labels,
            album_chart_values=album_chart_values,
            single_chart_values=single_chart_values,
            error=None
        )

    except Exception:
        return render_template(
            "artist.html",
            error="系統暫時無法取得部分外部資料，請稍後再試。"
        )


if __name__ == "__main__":
    app.run(debug=True)
