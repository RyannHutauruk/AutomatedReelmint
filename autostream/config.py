"""Global configuration loaded from environment / config.json."""

from __future__ import annotations

import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Directories
LIBRARY_DIR = BASE_DIR / "library"
VISUALS_DIR = BASE_DIR / "visuals"
CREDENTIALS_DIR = BASE_DIR / "credentials"
DB_PATH = BASE_DIR / "autostream" / "db" / "autostream.db"

# Ensure critical dirs exist
for d in (LIBRARY_DIR, VISUALS_DIR, CREDENTIALS_DIR, DB_PATH.parent):
    d.mkdir(parents=True, exist_ok=True)

# YouTube defaults
DEFAULT_RTMP_URL = "rtmp://a.rtmp.youtube.com/live2"

# Streaming defaults
DEFAULT_VIDEO_BITRATE = "2500k"
DEFAULT_AUDIO_BITRATE = "128k"
DEFAULT_RESOLUTION = "1920x1080"
DEFAULT_FPS = 30

# Generator defaults
MUSIC_GEN_INTERVAL_HOURS = 24
VISUAL_GEN_INTERVAL_HOURS = 24


def load_config() -> dict:
    """Load config.json from project root, returning empty dict if missing."""
    config_path = BASE_DIR / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}


def save_config(data: dict) -> None:
    config_path = BASE_DIR / "config.json"
    with open(config_path, "w") as f:
        json.dump(data, f, indent=2)
