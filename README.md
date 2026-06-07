# MeloMap.

> **Navigate Your Sonic Universe.**
>
> 導航你的聲音宇宙。

MeloMap. 是一張連結歌手、曲風與演唱會的音樂地圖。使用者可以搜尋歌手，也能從心情、語言與曲風開始探索音樂。我們透過 Spotify 延伸聽覺探索，並結合 Ticketmaster 與 Leaflet，引導使用者找到下一場演唱會。

網站以 Python Flask 製作，整合 Spotify、Last.fm、Wikipedia 與 Ticketmaster，集中顯示歌手資料、作品、播放器、相似歌手、作品年份、演唱會與地圖。

## 線上網站

- Render 網址：待部署後補上
- 使用者回饋表單：待網站上線後補上

## 主要功能

- 搜尋歌手並查看基本資料、圖片、風格標籤與生平簡介
- 顯示 Spotify 官方頁面、播放器、專輯與單曲
- 依作品年份產生專輯與單曲分布圖
- 顯示 Last.fm 相似歌手與音樂風格
- 使用情境推薦，依讀書、運動、通勤、失戀或睡前尋找歌手
- 使用語言與曲風分類探索歌手榜單
- 從熱門歌手中隨機推薦歌手
- 查詢未來一年 Ticketmaster 演唱會
- 使用 Leaflet 地圖顯示演唱會場館位置
- 依歌手圖片產生動態背景色彩
- 首頁隨機歌手圖片可顯示名稱並連到歌手資料頁
- 支援桌面與手機版響應式畫面

## 外部服務備援

網站不會因為單一外部服務暫時失效而直接中斷：

- Spotify 無法連線或被限流時，切換為 Last.fm 與 Wikipedia 備援資料
- `SPOTIFY_PAUSED=true` 可手動暫停 Spotify API 請求
- Ticketmaster 無法連線時，演唱會區顯示友善錯誤提示
- 沒有演唱會時，會清楚顯示目前沒有公開場次
- API 金鑰只放在本機 `.env` 或 Render Environment Variables

## 使用技術

- 後端：Python、Flask
- 前端：HTML、CSS、JavaScript、Jinja
- 圖表：Chart.js
- 地圖：Leaflet
- API：Spotify Web API、Last.fm API、Ticketmaster Discovery API
- 資料來源：Wikipedia
- 環境變數：python-dotenv

## 組員分工

| 組員 | Branch | 主要工作 |
| --- | --- | --- |
| 容可丞（rong-kevin） | `rkc`、`feature/final-integration` | 期中原始專案、功能整合、首頁互動、手機版、錯誤提示、網站品牌、README 與上線準備 |
| Shaung | `shaung` | Ticketmaster 演唱會、Leaflet 地圖、歌手圖片動態背景、風格探索歌手榜單 |
| Wendy（wseong000） | `Wendy` | Spotify 備援模式、`SPOTIFY_PAUSED`、資料來源狀態、專輯封面與 API 錯誤處理 |

協作流程使用獨立 branch 開發，完成後透過 Pull Request 合併到 `main`。

## 專案結構

```text
my-first-python-project/
├── app.py
├── run.py
├── visualize_artist.py
├── requirements.txt
├── render.yaml
├── README.md
├── .env.example
├── services/
│   ├── spotify_api.py
│   ├── lastfm_api.py
│   ├── wiki_scraper.py
│   └── concert_api.py
├── templates/
│   ├── index.html
│   ├── artist.html
│   ├── mood.html
│   └── discover.html
└── static/
    ├── favicon.png
    ├── home.css
    ├── melomap-wordmark.png
    └── style.css
```

## 本機安裝

以下指令適用於 Windows PowerShell。

```powershell
git clone https://github.com/rong-kevin/my-first-python-project.git
cd my-first-python-project
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 環境變數

在專案根目錄建立 `.env`，可先複製 `.env.example`：

```env
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
LASTFM_API_KEY=your_lastfm_api_key
TICKETMASTER_API_KEY=your_ticketmaster_consumer_key
SPOTIFY_PAUSED=false
```

`.env` 已加入 `.gitignore`，不可 commit 或 push 到 GitHub。

## 執行網站

```powershell
python app.py
```

啟動後開啟：

```text
http://127.0.0.1:5000
```

也可以在網站執行期間，透過終端機直接開啟指定歌手：

```powershell
python run.py "Taylor Swift"
python run.py "周杰倫"
```

## Git 協作方式

```powershell
git checkout main
git pull --ff-only origin main
git checkout -b feature/功能名稱

# 完成功能與測試後
git add .
git commit -m "描述本次修改"
git push -u origin feature/功能名稱
```

Push 後在 GitHub 建立 Pull Request，經檢查後再合併到 `main`。

## Render 上線設定

上線時將 GitHub repository 連接到 Render，並在 Render Dashboard 設定與 `.env` 相同的環境變數。不要把真實 API key 寫進 repository。

本專案已提供 `render.yaml`，Render 會使用：

```text
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
Health Check: /health
```

正式部署前需確認：

- Production 啟動指令
- 四組 API 環境變數
- 網站主要頁面與手機版
- Spotify 備援模式
- Ticketmaster 演唱會與地圖

## 使用者回饋

網站上線後，預計使用 Google 表單收集：

- 網站操作是否容易
- 搜尋歌手是否順利
- 演唱會與地圖是否實用
- 畫面設計評分
- 最喜歡的功能
- 建議改善內容

回饋統計與改善結果將整理到期末簡報。

## 安全提醒

- 不要上傳 `.env`
- 不要在 HTML、JavaScript、README 或截圖中公開 API key
- Render 請使用 Environment Variables
- 若金鑰曾公開，應立即到服務平台撤銷並重新建立
