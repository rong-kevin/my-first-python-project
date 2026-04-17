import sys
from collections import Counter
import matplotlib.pyplot as plt

from services.spotify_api import get_artist_albums


def main():
    if len(sys.argv) < 2:
        print("請輸入歌手名稱")
        print('用法：python visualize_artist.py "Travis Scott"')
        sys.exit(1)

    artist_name = " ".join(sys.argv[1:])
    albums = get_artist_albums(artist_name)

    if not albums:
        print("找不到專輯資料")
        sys.exit(1)

    years = []
    for album in albums:
        release_date = album.get("release_date", "")
        if release_date:
            year = release_date[:4]
            if year.isdigit():
                years.append(year)

    if not years:
        print("沒有可視覺化的年份資料")
        sys.exit(1)

    year_counts = Counter(years)

    sorted_years = sorted(year_counts.keys())
    counts = [year_counts[year] for year in sorted_years]

    plt.figure(figsize=(10, 6))
    plt.bar(sorted_years, counts)
    plt.title(f"{artist_name} 專輯 / 單曲發行年份分布")
    plt.xlabel("年份")
    plt.ylabel("數量")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()