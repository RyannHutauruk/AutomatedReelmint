"""Central configuration for the auto-shorts pipeline."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Paths ────────────────────────────────────────────────────────────
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ARCHIVE_FILE = DATA_DIR / "processed.txt"

for d in (DATA_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── YouTube Data API ─────────────────────────────────────────────────
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# Region code for trending (ISO 3166-1 alpha-2)
REGION_CODE = os.environ.get("REGION_CODE", "US")

# Video category ID (default: Gaming=20, best for long-form content)
# Common: 1=Film, 10=Music, 17=Sports, 20=Gaming, 22=People&Blogs,
#          23=Comedy, 24=Entertainment, 25=News, 27=Education, 28=Science
# Note: Entertainment (24) trending is mostly short-form (<2min), not useful
VIDEO_CATEGORY_ID = os.environ.get("VIDEO_CATEGORY_ID", "20")

# Min/max duration in seconds for source videos
MIN_DURATION_S = int(os.environ.get("MIN_DURATION_S", "300"))    # 5 min
MAX_DURATION_S = int(os.environ.get("MAX_DURATION_S", "3600"))   # 60 min

# How many trending videos to fetch per run
MAX_TRENDING_RESULTS = int(os.environ.get("MAX_TRENDING_RESULTS", "20"))

# ── Cobalt ───────────────────────────────────────────────────────────
COBALT_API_URL = os.environ.get("COBALT_API_URL", "http://localhost:9000")

# ── Clipping ─────────────────────────────────────────────────────────
CLIPS_PER_VIDEO = int(os.environ.get("CLIPS_PER_VIDEO", "3"))
CLIP_LENGTH_S = float(os.environ.get("CLIP_LENGTH_S", "30"))
GOAL_PRESET = os.environ.get("GOAL_PRESET", "tiktok")

# Add-ons (all on by default)
SUBTITLES = os.environ.get("SUBTITLES", "true").lower() in ("1", "true", "on", "yes")
FACE_TRACK = os.environ.get("FACE_TRACK", "true").lower() in ("1", "true", "on", "yes")
SAFETY_BOOST = os.environ.get("SAFETY_BOOST", "true").lower() in ("1", "true", "on", "yes")
CAPTION_STYLE = os.environ.get("CAPTION_STYLE", "hype_emoji")
SUBTITLE_LANGUAGE = os.environ.get("SUBTITLE_LANGUAGE", "auto")
