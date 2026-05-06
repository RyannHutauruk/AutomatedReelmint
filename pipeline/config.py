"""Central configuration for the auto-shorts pipeline."""

from __future__ import annotations

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _env(key: str, default: str = "") -> str:
    """Read an env var and strip any trailing inline comment."""
    val = os.environ.get(key, default)
    # Remove trailing  # comment  (but not inside the value itself)
    val = re.split(r"\s+#\s", val, maxsplit=1)[0].strip()
    return val

# ── Paths ────────────────────────────────────────────────────────────
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ARCHIVE_FILE = DATA_DIR / "processed.txt"

for d in (DATA_DIR, OUTPUT_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── YouTube Data API ─────────────────────────────────────────────────
YOUTUBE_API_KEY = _env("YOUTUBE_API_KEY", "")

# Region code for trending (ISO 3166-1 alpha-2)
REGION_CODE = _env("REGION_CODE", "US")

# Video category ID (default: Gaming=20, best for long-form content)
# Common: 1=Film, 10=Music, 17=Sports, 20=Gaming, 22=People&Blogs,
#          23=Comedy, 24=Entertainment, 25=News, 27=Education, 28=Science
# Note: Entertainment (24) trending is mostly short-form (<2min), not useful
VIDEO_CATEGORY_ID = _env("VIDEO_CATEGORY_ID", "20")

# Min/max duration in seconds for source videos
MIN_DURATION_S = int(_env("MIN_DURATION_S", "300"))    # 5 min
MAX_DURATION_S = int(_env("MAX_DURATION_S", "3600"))   # 60 min

# How many trending videos to fetch per run
MAX_TRENDING_RESULTS = int(_env("MAX_TRENDING_RESULTS", "20"))

# ── Download ─────────────────────────────────────────────────────────
# Path to cookies.txt file (Netscape format) for YouTube authentication
# Export from your browser using a cookie extension while logged into YouTube
COOKIES_FILE = _env("COOKIES_FILE", "")

# Cobalt API (optional, used as fallback if configured)
COBALT_API_URL = _env("COBALT_API_URL", "")

# ── Clipping ─────────────────────────────────────────────────────────
CLIPS_PER_VIDEO = int(_env("CLIPS_PER_VIDEO", "3"))
CLIP_LENGTH_S = float(_env("CLIP_LENGTH_S", "30"))
GOAL_PRESET = _env("GOAL_PRESET", "tiktok")

# Add-ons (all on by default)
SUBTITLES = _env("SUBTITLES", "true").lower() in ("1", "true", "on", "yes")
FACE_TRACK = _env("FACE_TRACK", "true").lower() in ("1", "true", "on", "yes")
SAFETY_BOOST = _env("SAFETY_BOOST", "true").lower() in ("1", "true", "on", "yes")
CAPTION_STYLE = _env("CAPTION_STYLE", "hype_emoji")
SUBTITLE_LANGUAGE = _env("SUBTITLE_LANGUAGE", "auto")
