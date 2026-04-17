from flask import Flask, render_template, request, redirect, url_for
import random
from collections import Counter
from services.spotify_api import search_artist, get_artist_albums
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



@app.route("/")
def home():
    return render_template("index.html", popular_artists=POPULAR_ARTISTS)

@app.route("/random")
def random_artist():
    artist_name = random.choice(POPULAR_ARTISTS)
    return redirect(url_for("artist_page", name=artist_name))


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