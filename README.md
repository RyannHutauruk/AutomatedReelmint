# Auto-Shorts Pipeline

Fully automated pipeline that **finds trending long-form videos**, **clips the best moments into 9:16 shorts** with captions, and outputs them **ready to upload** — zero manual input.

```
Trend Scout (YouTube API) → Cobalt Downloader → Reelmint Engine → Output Shorts
```

## How It Works

1. **Scout** — Queries YouTube Data API for currently trending long-form videos (filtered by category, region, duration)
2. **Dedup** — Skips any video that's already been processed (tracked in `data/processed.txt`)
3. **Download** — Downloads via self-hosted Cobalt API (bypasses YouTube bot detection), with yt-dlp fallback
4. **Clip** — Reelmint engine analyzes audio + motion, finds best moments, generates 9:16 shorts with:
   - Auto-subtitles (Whisper, per-word highlighting, emoji decoration)
   - Speaker-aware face-tracking crop
   - Monetization-safety transforms (mirror, zoom, speed/pitch shifts)
5. **Output** — Finished shorts saved to `output/<video_id>/` with metadata

## Quick Start

### 1. Prerequisites

- Python 3.12+
- ffmpeg (`sudo apt install ffmpeg`)
- Docker (for Cobalt)
- YouTube Data API key ([get one free](https://console.cloud.google.com/apis/credentials))

### 2. Setup

```bash
# Clone the repo
git clone https://github.com/RyannHutauruk/auto-shorts-pipeline.git
cd auto-shorts-pipeline

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env and add your YOUTUBE_API_KEY
```

### 3. Set Up Cobalt (YouTube downloader)

Cobalt requires YouTube cookies to download videos (YouTube blocks unauthenticated server-side downloads).

**One-time cookie setup:**
```bash
# 1. Clone Cobalt repo to generate cookies
git clone https://github.com/imputnet/cobalt /tmp/cobalt
cd /tmp/cobalt/api && npm install

# 2. Generate YouTube cookies (use a throwaway Google account!)
#    This opens a browser flow — follow the on-screen instructions
npm run token:youtube

# 3. Copy the generated cookies.json to your pipeline directory
cp cookies.json /path/to/auto-shorts-pipeline/cookies.json
```

**Start Cobalt:**
```bash
cd /path/to/auto-shorts-pipeline
docker compose up -d
# Cobalt API will be available at http://localhost:9000
# Verify: curl http://localhost:9000/ | python3 -c "import sys,json; print(json.load(sys.stdin)['cobalt']['version'])"
```

> **⚠️ Without cookies.json, YouTube downloads will fail** with `error.api.youtube.login`. The rest of the pipeline (scout, clipping) still works.

### 4. Run the Pipeline

```bash
# One-shot: find trending → download → clip → output
source .env && python -m pipeline.run

# Daemon mode: run every 6 hours automatically
source .env && python -m pipeline.run --daemon --interval 6
```

### 5. Find Your Shorts

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
| `REGION_CODE` | `US` | Trending region (US, ID, GB, etc.) |
| `VIDEO_CATEGORY_ID` | `20` | YouTube category (20=Gaming, 22=People&Blogs — best for long-form) |
| `MIN_DURATION_S` | `300` | Min source video length (5 min) |
| `MAX_DURATION_S` | `3600` | Max source video length (60 min) |
| `CLIPS_PER_VIDEO` | `3` | Shorts to generate per video |
| `CLIP_LENGTH_S` | `30` | Target clip duration |
| `SUBTITLES` | `true` | Auto-subtitles via Whisper |
| `FACE_TRACK` | `true` | Speaker-aware crop |
| `SAFETY_BOOST` | `true` | Monetization-safety transforms |
| `COBALT_API_URL` | `http://localhost:9000` | Self-hosted Cobalt endpoint |

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
│   Cobalt API (primary) → yt-dlp (fallback)│
│   Dedup: skip already-processed IDs       │
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
|----|----------|--------------------|
| 20 | Gaming | ✅ Best (37/49 videos are 5-60min) |
| 22 | People & Blogs | ✅ Great (34/50 are long-form) |
| 0  | All | ✅ Good (11/49 are long-form) |
| 17 | Sports | ⚠️ Few (2/50 are long-form) |
| 10 | Music | ⚠️ Few (5/30 are long-form) |
| 24 | Entertainment | ❌ None (all <2min, max=124s) |
| 1  | Film & Animation | — |
| 23 | Comedy | — |
| 25 | News & Politics | — |
| 27 | Education | — |
| 28 | Science & Technology | — |

## Powered By

- [Reelmint](https://github.com/RyannHutauruk/video-momentum-clipper) — Video clipping engine
- [Cobalt](https://github.com/imputnet/cobalt) — Media downloader (handles YouTube anti-bot)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — Speech-to-text
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) — Video downloader (fallback)
- [YouTube Data API v3](https://developers.google.com/youtube/v3) — Trending video discovery

## License

MIT
