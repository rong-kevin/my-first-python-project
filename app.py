import os
import random
from collections import Counter

from flask import Flask, render_template, request, redirect, session, url_for
from services.spotify_api import search_artist, get_artist_albums, get_artist_previews
from services.lastfm_api import get_similar_artists, get_artist_tags
from services.wiki_scraper import get_artist_bio
from services.concert_api import get_upcoming_concerts

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

STYLE_TAG_DESCRIPTIONS = {
    "pop": "流行音樂，旋律容易記住、編曲清楚，通常適合大眾聆聽。",
    "c-pop": "華語流行音樂，常見於中文抒情、流行與創作歌手作品。",
    "chinese": "中文語系音樂，重視歌詞理解與華語聽眾熟悉的語感。",
    "mandopop": "華語流行音樂，包含中文流行、抒情與創作歌手作品。",
    "taiwan": "與台灣音樂圈或華語流行文化關聯較高的標籤。",
    "jay chou": "與周杰倫相關的風格標記，常和華語流行、R&B、嘻哈與中國風元素連結。",
    "indie": "獨立音樂，通常較重視個人風格、樂團質感與非主流製作。",
    "r&b": "R&B 重視節奏律動與聲線情緒，常帶有深夜、放鬆或靈魂樂氛圍。",
    "rnb": "R&B 重視節奏律動與聲線情緒，常帶有深夜、放鬆或靈魂樂氛圍。",
    "k-pop": "韓國流行音樂，常結合舞曲、偶像團體、強節奏和完整舞台感。",
    "j-pop": "日本流行音樂，旋律線明顯，常見細膩情緒、動畫感或城市流行元素。",
    "ballad": "抒情歌曲，通常節奏較慢、情緒明確，重視歌詞和旋律。",
    "dance": "舞曲取向，節奏明確、能量高，適合運動或派對情境。",
    "hip-hop": "嘻哈音樂，重視節奏、押韻和口語表達。",
    "rock": "搖滾音樂，常以吉他、鼓和強烈現場感作為核心。",
    "acoustic": "原音或不插電風格，編曲較簡潔，聲音自然溫暖。",
    "singer-songwriter": "創作歌手風格，通常由歌手本人參與詞曲創作，個人敘事感較強。",
    "city pop": "城市流行，常帶有復古、都會、輕快或夜晚感。",
    "dream pop": "夢幻流行，聲響朦朧、氛圍感強，常適合放空或雨天。",
    "alternative": "另類音樂，通常不完全走主流流行公式，風格較有實驗或個性。",
    "idol": "偶像流行風格，常結合舞台表演、團體形象和完整視覺企劃。",
    "anime": "常與動畫作品、日系流行和戲劇化旋律連結。",
    "edm": "電子舞曲，節奏強烈、段落堆疊明顯，適合派對或運動。",
    "jazz pop": "融合爵士和流行音樂，常有溫暖和弦、輕鬆節奏與細緻聲線。",
    "lo-fi": "低傳真或放鬆取向的聲音，常適合讀書、工作或背景播放。",
    "soft pop": "柔和流行，旋律順耳、壓力較低，適合長時間聆聽。",
    "soul": "靈魂樂取向，重視人聲情緒、律動和溫度。",
    "ambient": "氛圍音樂，重視空間感與聲響層次，適合放空或專注。",
    "band": "樂團取向，通常有較明顯的吉他、鼓與現場演奏感。",
    "workout": "適合運動或提振精神的高能量標籤。",
    "chill": "放鬆取向，通常節奏不急、聲音舒適，適合背景播放。"
}

DEFAULT_STYLE_DESCRIPTION = "這是 Last.fm 根據聽眾標記整理出的風格關鍵字，可用來理解這位歌手常被歸類的音樂方向。"

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


def build_style_insights(artist_tags, similar_artists):
    tag_insights = []
    for tag in artist_tags[:5]:
        key = tag.strip().lower()
        tag_insights.append({
            "name": tag,
            "description": STYLE_TAG_DESCRIPTIONS.get(key, DEFAULT_STYLE_DESCRIPTION)
        })

    return {
        "tags": tag_insights,
        "similar_artists": similar_artists[:6] if similar_artists else []
    }


def pick_recommendation_artists(session_key, last_session_key, group_key, candidates, count=5):
    pick_count = min(count, len(candidates))
    if pick_count == 0:
        return []

    used_by_group = session.get(session_key, {})
    last_by_group = session.get(last_session_key, {})
    used_artists = set(used_by_group.get(group_key, []))
    available_artists = [artist for artist in candidates if artist not in used_artists]

    if len(available_artists) < pick_count:
        used_artists = set()
        available_artists = list(candidates)

    selected_artists = random.sample(available_artists, pick_count)
    last_artists = set(last_by_group.get(group_key, []))

    if len(candidates) > pick_count and set(selected_artists) == last_artists:
        for _ in range(20):
            retry_artists = random.sample(available_artists, pick_count)
            if set(retry_artists) != last_artists:
                selected_artists = retry_artists
                break

    used_artists.update(selected_artists)
    used_by_group[group_key] = list(used_artists)
    last_by_group[group_key] = selected_artists
    session[session_key] = used_by_group
    session[last_session_key] = last_by_group
    return selected_artists


def build_mood_recommendation(mood_key):
    mood = MOOD_RECOMMENDATIONS.get(mood_key)
    if not mood:
        return None

    recommendation = mood.copy()
    recommendation["artists"] = pick_recommendation_artists(
        "used_mood_artists",
        "last_mood_recommendations",
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
        "used_discover_artists",
        "last_discover_recommendations",
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
        concert_data = get_upcoming_concerts(artist.get("name") or artist_name)
        concert_events = concert_data.get("events", [])
        style_insights = build_style_insights(artist_tags, similar_artists)

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
        album_total = sum(album_chart_values)
        single_total = sum(single_chart_values)
        if not chart_labels and albums:
            album_total = len([album for album in albums if album.get("album_type") != "single"])
            single_total = len([album for album in albums if album.get("album_type") == "single"])
        yearly_totals = {
            year: album_counts[year] + single_counts[year]
            for year in chart_labels
        }
        most_active_year = max(yearly_totals, key=yearly_totals.get) if yearly_totals else "Last.fm"
        chart_summary = {
            "total": album_total + single_total,
            "albums": album_total,
            "singles": single_total,
            "most_active_year": most_active_year
        }

        return render_template(
            "artist.html",
            artist=artist,
            albums=albums,
            similar_artists=similar_artists,
            artist_tags=artist_tags,
            artist_bio=artist_bio,
            style_insights=style_insights,
            concert_events=concert_events,
            concert_message=concert_data.get("message"),
            chart_labels=chart_labels,
            album_chart_values=album_chart_values,
            single_chart_values=single_chart_values,
            chart_summary=chart_summary,
            error=None
        )

    except Exception:
        return render_template(
            "artist.html",
            error="系統暫時無法取得部分外部資料，請稍後再試。"
        )


if __name__ == "__main__":
    app.run(debug=True)
