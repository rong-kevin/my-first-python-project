# 歌手資料探索網站 (Artist Explorer)

這是一個使用 Python Flask 製作的音樂資料探索網站。
使用者可以輸入歌手名稱，網站會整合 Spotify、Last.fm 與 Wikipedia 的資料，顯示歌手的基本資訊、專輯 / 單曲、相似歌手推薦、Spotify 播放器，以及作品年份分布圖。

此外，本專案也支援**終端機模式 (CLI)**，使用者可以直接在 Terminal 輸入歌手名稱，自動開啟對應的歌手網頁。

---

## 專案功能

- **搜尋歌手名稱**
- **顯示歌手圖片與 Spotify 連結**
- **內嵌 Spotify 官方播放器**
- **顯示歷年專輯 / 單曲列表**
- **顯示相似歌手推薦**
- **顯示 Wikipedia 生平簡介**
- **顯示作品發行年份分布圖 (資料視覺化)**
- **支援終端機指令，快速開啟歌手頁面**

---

##  使用技術

- **後端框架**：Python, Flask
- **前端介面**：HTML, CSS, Chart.js
- **API 串接**：Spotify Web API, Last.fm API
- **網頁爬蟲**：requests, BeautifulSoup (擷取 Wikipedia 資料)
- **環境管理**：python-dotenv

---

##  專案結構

```text
my-first-project/
├── app.py                  # Flask 主程式
├── run.py                  # 終端機快速執行腳本
├── visualize_artist.py     # 終端機視覺化腳本
├── requirements.txt        # 專案套件清單
├── README.md               # 專案說明文件
├── .gitignore              # Git 忽略清單
├── .env.example            # 環境變數範例檔
├── services/               # 外部服務邏輯
│   ├── spotify_api.py      # Spotify API 串接
│   ├── lastfm_api.py       # Last.fm API 串接
│   ├── wiki_scraper.py     # 維基百科爬蟲
│   └── wordcloud_generator.py # 文字雲生成
├── templates/              # HTML 模板
│   ├── index.html          # 首頁
│   └── artist.html         # 歌手資料頁
└── static/                 # 靜態檔案
    └── style.css           # 樣式表

##  安裝

1. 建立虛擬環境
請在終端機依序輸入以下指令，建立虛擬環境並安裝所需套件：
python -m venv .venv

2.安裝套件
.\.venv\Scripts\python -m pip install -r requirements.txt

## 環境變數設定
在專案根目錄建立一個 .env 檔案（可參考 .env.example），並填入你申請的 API 金鑰：

程式碼片段
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
LASTFM_API_KEY=your_lastfm_api_key

## 執行方式

A. 啟動網站模式
在終端機輸入以下指令啟動 Flask 伺服器：

.\.venv\Scripts\python app.py
啟動後，開啟瀏覽器並進入 http://127.0.0.1:5000 即可使用。

B. 終端機模式 (CLI)
本專案支援透過終端機指令直接查詢並開啟歌手頁面。請輸入：

.\.venv\Scripts\python run.py "Taylor Swift"
# 或
.\.venv\Scripts\python run.py "周杰倫"
程式將會自動開啟瀏覽器並導向該歌手的專屬頁面。

## 專案特色

1.多資料來源整合

Spotify：取得歌手基本資料、專輯清單，並內嵌播放器。
Last.fm：獲取相似歌手推薦與風格標籤。
Wikipedia：透過爬蟲技術抓取歌手生平簡介。

2.資料視覺化

根據歌手作品資料，將專輯 / 單曲的發行年份整理成圖表，直接顯示在網頁中。 
搜尋與探索功能

3. 搜尋與探索功能 

使用者不僅能搜尋單一歌手，還能透過「相似歌手」的推薦名單，不斷延伸探索其他潛力音樂人。

4.網頁與終端整合

除了提供美觀的 Web 介面，也支援命令列操作，符合課程中終端輸入與程式執行的概念。

AI 協助開發內容

發想專案主題

規劃網站架構

建立 Flask 專案基礎模板

協助串接 Spotify 與 Last.fm API，並處理 JSON 資料解析

撰寫 BeautifulSoup 爬蟲以獲取 Wikipedia 資料

協助資料視覺化（發行年份圖表）的邏輯撰寫

優化 HTML/CSS 的前端 UI 排版

協助 Debug 與排除執行期間的各項錯誤 (Error Handling)

⚠️ 注意事項
.env 檔案包含敏感金鑰，絕對不可上傳到 GitHub。

若外部 API（如 Spotify 或 Last.fm）暫時失效或更改驗證方式，部分資料可能無法正常顯示。

