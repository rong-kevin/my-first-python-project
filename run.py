import sys
import webbrowser
import urllib.parse


def main():
    if len(sys.argv) < 2:
        print("請輸入歌手名稱")
        print('用法：python run.py "Taylor Swift"')
        sys.exit(1)

    artist_name = " ".join(sys.argv[1:])
    encoded_name = urllib.parse.quote(artist_name)

    url = f"http://127.0.0.1:5000/artist?name={encoded_name}"

    print(f"正在開啟歌手頁面：{artist_name}")
    print(f"網址：{url}")

    webbrowser.open(url)


if __name__ == "__main__":
    main()