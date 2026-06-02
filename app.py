from flask import Flask, render_template, request, redirect, url_for
import random
from collections import Counter
from services.spotify_api import search_artist, get_artist_albums, get_artist_top_tracks
from services.lastfm_api import get_similar_artists, get_artist_tags
from services.wiki_scraper import get_artist_bio

app = Flask(__name__)
POPULAR_ARTISTS = [
    "Taylor Swift",
    "周杰倫",
    "Ed Sheeran",
    "Drake",
    "Travis Scott",
    "Ariana Grande",
    "The Weeknd",
    "Bruno Mars"
]

MOOD_RECOMMENDATIONS = {
    "study": {
        "label": "讀書 / 寫作業",
        "description": "節奏穩定、旋律舒服，適合需要專心但不想太安靜的時候。",
        "artists": ["Laufey", "IU", "Keshi", "Jay Chou", "Ed Sheeran"],
        "tags": ["lo-fi", "acoustic", "r&b", "soft pop"]
    },
    "workout": {
        "label": "運動 / 健身",
        "description": "節奏強、能量高，適合跑步、重訓或需要提振精神。",
        "artists": ["Dua Lipa", "BLACKPINK", "Travis Scott", "The Weeknd", "Bruno Mars"],
        "tags": ["dance pop", "hip-hop", "edm", "k-pop"]
    },
    "commute": {
        "label": "通勤 / 走路",
        "description": "旋律好入口、情緒不太重，適合在路上輕鬆聽。",
        "artists": ["Ed Sheeran", "NewJeans", "告五人", "Taylor Swift", "Ariana Grande"],
        "tags": ["pop", "indie", "easy listening"]
    },
    "sad": {
        "label": "失戀 / 難過",
        "description": "歌詞情緒感強，適合想整理心情或被音樂陪伴的時候。",
        "artists": ["Adele", "Taylor Swift", "田馥甄", "Joji", "Billie Eilish"],
        "tags": ["ballad", "sad pop", "singer-songwriter"]
    },
    "night": {
        "label": "睡前 / 深夜",
        "description": "聲音柔和、氛圍放鬆，適合睡前、深夜或一個人放空。",
        "artists": ["Laufey", "Keshi", "Frank Ocean", "Billie Eilish", "Aimer"],
        "tags": ["jazz pop", "r&b", "ambient", "slow"]
    },
    "rainy": {
        "label": "下雨天",
        "description": "帶一點電影感和情緒厚度，適合雨天、咖啡廳或窗邊時間。",
        "artists": ["周杰倫", "deca joins", "告五人", "Aimer", "Lana Del Rey"],
        "tags": ["indie", "city pop", "ballad", "dream pop"]
    }
}


@app.route("/")
def home():
    return render_template("index.html", popular_artists=POPULAR_ARTISTS)


@app.route("/random")
def random_artist():
    artist_name = random.choice(POPULAR_ARTISTS)
    return redirect(url_for("artist_page", name=artist_name))


@app.route("/mood")
def mood_page():
    selected_mood = request.args.get("type", "").strip()
    selected_recommendation = MOOD_RECOMMENDATIONS.get(selected_mood)

    return render_template(
        "mood.html",
        moods=MOOD_RECOMMENDATIONS,
        selected_mood=selected_mood,
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
        top_tracks = get_artist_top_tracks(artist_name)
        similar_artists = get_similar_artists(artist_name)
        artist_tags = get_artist_tags(artist_name)
        artist_bio = get_artist_bio(artist_name)

        years = []
        for album in albums:
            release_date = album.get("release_date", "")
            if release_date:
                year = release_date[:4]
                if year.isdigit():
                    years.append(year)

        year_counts = Counter(years)
        chart_labels = sorted(year_counts.keys())
        chart_values = [year_counts[year] for year in chart_labels]

        return render_template(
            "artist.html",
            artist=artist,
            albums=albums,
            top_tracks=top_tracks,
            similar_artists=similar_artists,
            artist_tags=artist_tags,
            artist_bio=artist_bio,
            chart_labels=chart_labels,
            chart_values=chart_values,
            error=None
        )

    except Exception as e:
        return render_template(
            "artist.html",
            error="系統暫時無法取得部分外部資料，請稍後再試。"
        )

if __name__ == "__main__":
    app.run(debug=True)