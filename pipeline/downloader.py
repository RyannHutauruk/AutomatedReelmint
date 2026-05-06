"""Video Downloader — downloads videos via yt-dlp (primary) with Cobalt fallback."""

from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

import requests

from pipeline.config import COBALT_API_URL, COOKIES_FILE, DATA_DIR

log = logging.getLogger(__name__)

DOWNLOAD_DIR = DATA_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


def download_via_ytdlp(
    video_url: str,
    output_dir: Path | None = None,
    cookies_file: str | None = None,
) -> Path | None:
    """Download via yt-dlp with optional cookies for YouTube authentication."""
    out_dir = output_dir or DOWNLOAD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    video_id = _extract_video_id(video_url) or "video"
    out_path = out_dir / f"{video_id}.mp4"

    if out_path.exists():
        log.info("Already downloaded: %s", out_path)
        return out_path

    # Use cookies file for YouTube authentication
    cf = cookies_file or COOKIES_FILE
    cookie_args = []
    if cf and Path(cf).exists():
        cookie_args = ["--cookies", cf]
        log.info("Using cookies file: %s", cf)

    # Try multiple format strategies (first success wins)
    format_attempts = [
        # 1. Best quality with merge (requires ffmpeg)
        ["-f", "bestvideo[height<=1080]+bestaudio/best", "--merge-output-format", "mp4"],
        # 2. Sort-based selection (more robust, still needs ffmpeg for merge)
        ["-S", "height:1080", "--merge-output-format", "mp4"],
        # 3. Pre-merged format only (no ffmpeg needed, lower quality)
        ["-f", "best[height<=1080]/best"],
    ]

    for i, fmt_args in enumerate(format_attempts, 1):
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--remote-components", "ejs:github",
            *fmt_args,
            "-o", str(out_path),
            *cookie_args,
            video_url,
        ]

        try:
            log.info("yt-dlp attempt %d/%d: %s", i, len(format_attempts), video_url[:80])
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if proc.returncode == 0 and out_path.exists():
                log.info("yt-dlp downloaded: %s (%.1f MB)", out_path.name, out_path.stat().st_size / 1e6)
                return out_path
            # Check for file with different extension
            if proc.returncode == 0:
                for f in out_dir.glob(f"{video_id}.*"):
                    if f.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}:
                        return f
            stderr = proc.stderr[-500:] if proc.stderr else ""
            log.warning("yt-dlp attempt %d failed: %s", i, stderr)
            out_path.unlink(missing_ok=True)
        except subprocess.TimeoutExpired:
            log.error("yt-dlp timed out for %s", video_url[:80])
            out_path.unlink(missing_ok=True)
        except Exception as e:
            log.error("yt-dlp error: %s", e)
            out_path.unlink(missing_ok=True)

    return None


def download_via_cobalt(video_url: str, output_dir: Path | None = None) -> Path | None:
    """Download via self-hosted Cobalt API (optional fallback).

    Only attempted if COBALT_API_URL is configured.
    """
    if not COBALT_API_URL:
        return None

    out_dir = output_dir or DOWNLOAD_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        resp = requests.post(
            COBALT_API_URL,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            json={"url": video_url, "videoQuality": "1080", "filenameStyle": "basic"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log.warning("Cobalt API request failed: %s", e)
        return None

    status = data.get("status")
    if status in ("tunnel", "redirect"):
        download_url = data.get("url")
        if not download_url:
            log.warning("Cobalt returned %s but no URL", status)
            return None
        return _download_file(download_url, out_dir, video_url)
    elif status == "picker":
        items = data.get("picker", [])
        for item in items:
            if item.get("type") == "video" and item.get("url"):
                return _download_file(item["url"], out_dir, video_url)
        log.warning("Cobalt picker had no video items")
        return None
    elif status == "error":
        log.warning("Cobalt error: %s", data.get("error", {}).get("code", "unknown"))
        return None
    else:
        log.warning("Unexpected Cobalt status: %s", status)
        return None


def _download_file(url: str, out_dir: Path, source_url: str) -> Path | None:
    """Stream-download a file from a direct URL."""
    video_id = _extract_video_id(source_url) or urlparse(source_url).path.split("/")[-1]
    out_path = out_dir / f"{video_id}.mp4"

    if out_path.exists():
        log.info("Already downloaded: %s", out_path)
        return out_path

    try:
        log.info("Downloading %s → %s", url[:80], out_path.name)
        resp = requests.get(url, stream=True, timeout=600)
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        log.info("Downloaded: %s (%.1f MB)", out_path.name, out_path.stat().st_size / 1e6)
        return out_path
    except Exception as e:
        log.error("Download failed: %s", e)
        out_path.unlink(missing_ok=True)
        return None


def download_video(
    video_url: str,
    output_dir: Path | None = None,
    cookies_file: str | None = None,
) -> Path | None:
    """Download a video — yt-dlp first (with cookies), Cobalt as fallback.

    Returns the path to the downloaded file, or None if all methods fail.
    """
    # Try yt-dlp first (works with cookies.txt)
    path = download_via_ytdlp(video_url, output_dir, cookies_file)
    if path and path.exists():
        return path

    # Fallback to Cobalt (only if configured)
    if COBALT_API_URL:
        log.info("yt-dlp failed, trying Cobalt for %s", video_url[:80])
        path = download_via_cobalt(video_url, output_dir)
        if path and path.exists():
            return path

    log.error("All download methods failed for %s", video_url[:80])
    return None


def _extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from a URL."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
