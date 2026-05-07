# Auto-Shorts Pipeline

Fully automated pipeline that **finds trending long-form videos**, **clips the best moments into 9:16 shorts** with captions, and outputs them **ready to upload** — zero manual input.

```
Trend Scout (YouTube API) → yt-dlp Download → Reelmint Engine → Output Shorts
```

## How It Works

1. **Scout** — Queries YouTube Data API for currently trending long-form videos (filtered by category, region, duration)
2. **Dedup** — Skips any video that's already been processed (tracked in `data/processed.txt`)
3. **Download** — Downloads via yt-dlp with browser cookies for YouTube authentication
4. **Clip** — Reelmint engine analyzes audio + motion, finds best moments, generates 9:16 shorts with:
   - Auto-subtitles (Whisper, per-word highlighting, emoji decoration)
   - Speaker-aware face-tracking crop
   - Monetization-safety transforms (mirror, zoom, speed/pitch shifts)
5. **Output** — Finished shorts saved to `output/<video_id>/` with metadata

## Quick Start

### 1. Prerequisites

- Python 3.12+
- ffmpeg
- yt-dlp
- YouTube Data API key ([get one free](https://console.cloud.google.com/apis/credentials))

**Windows (CMD as Administrator):**
```cmd
choco install python3 ffmpeg git -y
pip install yt-dlp
```

**macOS:**
```bash
brew install python@3.12 ffmpeg yt-dlp
```

**Linux:**
```bash
sudo apt install -y python3 python3-venv ffmpeg
pip install yt-dlp
```

### 2. Clone & Install

```bash
git clone https://github.com/RyannHutauruk/AutomatedReelmint.git
cd AutomatedReelmint
python3 -m venv .venv

# Linux/macOS:
source .venv/bin/activate
# Windows CMD:
# .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Export YouTube Cookies (one-time)

YouTube blocks downloads without authentication. You need to export cookies from your browser.

1. Install Chrome extension: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Go to https://www.youtube.com and make sure you're **logged in** (use a throwaway account)
3. Click the extension icon → **Export** → save as `cookies.txt`
4. Move `cookies.txt` to your `AutomatedReelmint` folder

> **Note:** Cookies expire every few weeks. If downloads start failing, repeat steps 2-4 to refresh them.

### 4. Configure

```bash
# Linux/macOS:
cp .env.example .env
# Windows CMD:
# copy .env.example .env
```

Edit `.env` and set your API key:
```
YOUTUBE_API_KEY=your_key_here
COOKIES_FILE=cookies.txt
```

### 5. Run

```bash
# Linux/macOS:
source .venv/bin/activate && source .env && python -m pipeline.run

# Windows CMD:
.venv\Scripts\activate
for /f "tokens=1,2 delims==" %a in (.env) do set %a=%b
python -m pipeline.run

# Daemon mode (runs every 6 hours):
python -m pipeline.run --daemon --interval 6
```

### 6. Find Your Shorts

```
output/
  ├── VIDEO_ID_1/
  │   ├── clip_01.mp4
  │   ├── clip_02.mp4
  │   ├── clip_03.mp4
  │   └── metadata.json
  ├── VIDEO_ID_2/
  │   ├── clip_01.mp4
  │   ├── ...
```

## Configuration

All settings via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `YOUTUBE_API_KEY` | *required* | Free API key from Google Cloud Console |
| `COOKIES_FILE` | | Path to cookies.txt for YouTube authentication |
| `REGION_CODE` | `US` | Trending region (US, ID, GB, etc.) |
| `VIDEO_CATEGORY_ID` | `20` | YouTube category (20=Gaming, 22=People&Blogs — best for long-form) |
| `MIN_DURATION_S` | `300` | Min source video length (5 min) |
| `MAX_DURATION_S` | `3600` | Max source video length (60 min) |
| `CLIPS_PER_VIDEO` | `3` | Shorts to generate per video |
| `CLIP_LENGTH_S` | `30` | Target clip duration |
| `SUBTITLES` | `true` | Auto-subtitles via Whisper |
| `FACE_TRACK` | `true` | Speaker-aware crop |
| `SAFETY_BOOST` | `true` | Monetization-safety transforms |
| `COBALT_API_URL` | | Optional: self-hosted Cobalt API endpoint |

## Architecture

```
┌────────────────────────────────────────────┐
│           pipeline/scout.py                │
│   YouTube Data API → trending videos       │
│   Filter by category, region, duration     │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│         pipeline/downloader.py             │
│   yt-dlp + cookies (primary)              │
│   Cobalt API (optional fallback)          │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│         backend/ (Reelmint engine)         │
│   analyzer.py → subtitler.py → clipper.py │
│   + face_tracker.py + emojis.py           │
└──────────────────┬─────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────┐
│              output/                       │
│   <video_id>/clip_01.mp4, clip_02.mp4...  │
│   metadata.json                           │
└────────────────────────────────────────────┘
```

## YouTube Category IDs

| ID | Category | Long-form trending? |
|----|----------|-------------------|
| 20 | Gaming | Best (37/49 videos are 5-60min) |
| 22 | People & Blogs | Great (34/50 are long-form) |
| 0  | All | Good (11/49 are long-form) |
| 17 | Sports | Few (2/50 are long-form) |
| 10 | Music | Few (5/30 are long-form) |
| 24 | Entertainment | None (all <2min) |

---

# YouTube Auto Stream System

24/7 automated YouTube live streaming of music content across multiple channels. Manages music generation, visual creation, and continuous streaming from a single dashboard.

## Quick Start (Auto Stream)

### Prerequisites
- Python 3.12+, ffmpeg, Node.js 18+ (for dashboard)

### Backend Setup
```bash
cd AutomatedReelmint
python3 -m venv .venv && source .venv/bin/activate
pip install -r autostream/requirements.txt

# Start the API server
uvicorn autostream.main:app --host 0.0.0.0 --port 8000 --reload
```

### Dashboard Setup
```bash
cd dashboard
npm install
npm start          # Dev server at http://localhost:3000
# or
npm run build      # Production build (served by FastAPI)
```

### How It Works
1. **Add channels** via the dashboard — each has its own stream key, music folder, visual folder, genre, and schedule
2. **Populate libraries** — drop audio files in `library/<genre>/` and video loops in `visuals/<theme>/`
3. **Start streaming** — the engine randomly picks music + visuals, merges them with ffmpeg, and pushes RTMP to YouTube
4. **Auto-rotation** — when a song ends, the next one plays automatically; titles rotate via YouTube API

### Architecture
```
┌──────────────────────────────────────────────────┐
│           Dashboard (React)                       │
│  Channels │ Stream Control │ Library │ Logs       │
└────────────────────┬─────────────────────────────┘
                     │ REST API
┌────────────────────▼─────────────────────────────┐
│           Backend (FastAPI)                        │
│  stream_engine/ │ youtube_api/ │ generators/       │
│  scheduler/     │ db/          │ api/              │
└────────────────────┬─────────────────────────────┘
                     │ ffmpeg RTMP
                     ▼
            YouTube Live Stream
```

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/channels` | GET/POST | List / create channels |
| `/api/channels/{id}` | GET/PUT/DELETE | Manage channel |
| `/api/channels/{id}/start` | POST | Start streaming |
| `/api/channels/{id}/stop` | POST | Stop streaming |
| `/api/library/music/{genre}` | GET | List tracks |
| `/api/library/visuals/{theme}` | GET | List visuals |
| `/api/generators/music/generate` | POST | Trigger music generation |
| `/api/generators/visuals/generate` | POST | Trigger visual generation |
| `/api/logs/stream` | GET | Stream logs |
| `/api/health` | GET | System status |

### File Structure
```
autostream/
  main.py              ← FastAPI app entry
  config.py            ← Global configuration
  api/                 ← REST endpoints
  stream_engine/       ← ffmpeg RTMP controller
  youtube_api/         ← OAuth2 + broadcast management
  generators/          ← Music & visual generators
  scheduler/           ← APScheduler cron jobs
  db/                  ← SQLite models
dashboard/             ← React UI
library/               ← Music files by genre
visuals/               ← Video loops by theme
credentials/           ← OAuth tokens per channel
config.json            ← App settings
```

---

## Powered By

- [Reelmint](https://github.com/RyannHutauruk/video-momentum-clipper) — Video clipping engine
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Video downloader
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Speech-to-text
- [YouTube Data API v3](https://developers.google.com/youtube/v3) — Trending video discovery

## License

MIT
