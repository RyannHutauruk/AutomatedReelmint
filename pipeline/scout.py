"""Trend Scout — discovers trending long-form videos via YouTube Data API."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from googleapiclient.discovery import build  # type: ignore[import-untyped]

from pipeline.config import (
    MAX_DURATION_S,
    MAX_TRENDING_RESULTS,
    MIN_DURATION_S,
    REGION_CODE,
    VIDEO_CATEGORY_ID,
    YOUTUBE_API_KEY,
)

log = logging.getLogger(__name__)


@dataclass
class TrendingVideo:
    video_id: str
    title: str
    channel: str
    duration_s: int
    view_count: int
    url: str


def _parse_iso8601_duration(raw: str) -> int:
    """Convert ISO 8601 duration (PT1H23M45S) to seconds."""
    match = re.match(
        r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", raw
    )
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def fetch_trending(
    api_key: str | None = None,
    region: str | None = None,
    category_id: str | None = None,
    max_results: int | None = None,
    min_duration: int | None = None,
    max_duration: int | None = None,
) -> list[TrendingVideo]:
    """Fetch currently trending videos from YouTube, filtered by duration.

    Returns only long-form videos (default: 5–60 min).
    """
    key = api_key or YOUTUBE_API_KEY
    if not key:
        raise RuntimeError(
            "YOUTUBE_API_KEY not set. Get one free at "
            "https://console.cloud.google.com/apis/credentials"
        )

    region = region or REGION_CODE
    category_id = category_id or VIDEO_CATEGORY_ID
    max_results = max_results or MAX_TRENDING_RESULTS
    min_dur = min_duration or MIN_DURATION_S
    max_dur = max_duration or MAX_DURATION_S

    youtube = build("youtube", "v3", developerKey=key)

    # Step 1: get trending video IDs
    response = (
        youtube.videos()
        .list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            regionCode=region,
            videoCategoryId=category_id,
            maxResults=min(max_results, 50),
        )
        .execute()
    )

    results: list[TrendingVideo] = []
    for item in response.get("items", []):
        duration = _parse_iso8601_duration(
            item["contentDetails"]["duration"]
        )
        if duration < min_dur or duration > max_dur:
            continue

        view_count = int(item["statistics"].get("viewCount", 0))
        vid = TrendingVideo(
            video_id=item["id"],
            title=item["snippet"]["title"],
            channel=item["snippet"]["channelTitle"],
            duration_s=duration,
            view_count=view_count,
            url=f"https://www.youtube.com/watch?v={item['id']}",
        )
        results.append(vid)

    log.info(
        "Scout found %d long-form trending videos (region=%s, category=%s)",
        len(results),
        region,
        category_id,
    )
    return results


def filter_unprocessed(
    videos: list[TrendingVideo], archive_path: str
) -> list[TrendingVideo]:
    """Remove videos that have already been processed (exist in archive)."""
    try:
        with open(archive_path, "r") as f:
            processed = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        processed = set()

    new = [v for v in videos if v.video_id not in processed]
    log.info(
        "Dedup: %d total trending, %d already processed, %d new",
        len(videos),
        len(videos) - len(new),
        len(new),
    )
    return new


def mark_processed(video_id: str, archive_path: str) -> None:
    """Record a video ID as processed."""
    with open(archive_path, "a") as f:
        f.write(f"{video_id}\n")
