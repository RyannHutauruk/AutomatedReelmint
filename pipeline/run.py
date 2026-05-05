#!/usr/bin/env python3
"""Pipeline Orchestrator — find trending → download → clip → output.

Usage:
    python -m pipeline.run              # one-shot: run the full pipeline once
    python -m pipeline.run --daemon     # loop forever on a schedule
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import shutil
import string
import sys
import time
from datetime import datetime
from pathlib import Path

# Add backend/ to sys.path so we can import the Reelmint modules
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from pipeline.config import (
    ARCHIVE_FILE,
    CAPTION_STYLE,
    CLIP_LENGTH_S,
    CLIPS_PER_VIDEO,
    FACE_TRACK,
    GOAL_PRESET,
    OUTPUT_DIR,
    SAFETY_BOOST,
    SUBTITLE_LANGUAGE,
    SUBTITLES,
)
from pipeline.downloader import download_video
from pipeline.scout import TrendingVideo, fetch_trending, filter_unprocessed, mark_processed

log = logging.getLogger("pipeline")


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _generate_id() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def clip_video(
    video_path: Path,
    video_id: str,
    video_title: str,
    n_clips: int,
    clip_len: float,
    subtitles: bool = True,
    face_track: bool = True,
    safety_boost: bool = True,
    language: str | None = None,
    caption_style: str = "hype_emoji",
) -> list[Path]:
    """Run the Reelmint engine on a downloaded video.

    Returns list of output clip paths.
    """
    from analyzer import find_best_moments
    from clipper import CTAS, HOOKS, generate_clip

    log.info("Analyzing: %s (%s)", video_title[:60], video_id)
    moments = find_best_moments(str(video_path), n_clips=n_clips, clip_len=clip_len)

    if not moments:
        log.warning("No moments found for %s — skipping", video_id)
        return []

    log.info("Found %d moments, generating clips...", len(moments))

    # Transcribe if subtitles enabled
    all_phrases = []
    if subtitles:
        from subtitler import group_words, transcribe

        log.info("Transcribing with Whisper...")
        lang = language if language != "auto" else None
        words = transcribe(str(video_path), language=lang)
        all_phrases = group_words(words)
        log.info("Transcribed: %d words, %d phrases", len(words), len(all_phrases))

    # Create output directory for this video
    video_out_dir = OUTPUT_DIR / video_id
    video_out_dir.mkdir(parents=True, exist_ok=True)

    clips: list[Path] = []
    used_hooks: set[str] = set()
    used_ctas: set[str] = set()

    for i, m in enumerate(moments, start=1):
        hook = next(
            (h for h in random.sample(HOOKS, len(HOOKS)) if h not in used_hooks),
            random.choice(HOOKS),
        )
        used_hooks.add(hook)
        cta = next(
            (c for c in random.sample(CTAS, len(CTAS)) if c not in used_ctas),
            random.choice(CTAS),
        )
        used_ctas.add(cta)

        out_path = video_out_dir / f"clip_{i:02d}.mp4"

        clip_phrases = None
        if subtitles and all_phrases:
            from subtitler import slice_phrases

            clip_phrases = slice_phrases(all_phrases, m.start, m.end)

        track = None
        if face_track:
            try:
                from face_tracker import track_face_xs

                track = track_face_xs(str(video_path), m.start, m.end)
            except Exception:
                track = None

        res = generate_clip(
            str(video_path),
            str(out_path),
            m.start,
            m.end,
            hook=hook,
            cta=cta,
            safety_boost=safety_boost,
            subtitle_phrases=clip_phrases,
            face_track=track,
            caption_style=caption_style,
        )
        clips.append(out_path)
        log.info(
            "  Clip %d/%d: %.1fs–%.1fs (score=%.3f) → %s",
            i,
            len(moments),
            m.start,
            m.end,
            m.score,
            out_path.name,
        )

    # Save metadata
    metadata = {
        "video_id": video_id,
        "video_title": video_title,
        "processed_at": datetime.utcnow().isoformat(),
        "clips_generated": len(clips),
        "clip_files": [c.name for c in clips],
    }
    with open(video_out_dir / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    return clips


def run_once() -> dict:
    """Execute one full pipeline run.

    Returns a summary dict with counts.
    """
    log.info("=" * 60)
    log.info("Pipeline run starting at %s", datetime.utcnow().isoformat())
    log.info("=" * 60)

    # Step 1: Discover trending videos
    log.info("Step 1: Scouting trending videos...")
    try:
        trending = fetch_trending()
    except Exception as e:
        log.error("Scout failed: %s", e)
        return {"error": str(e), "videos_processed": 0, "clips_generated": 0}

    if not trending:
        log.info("No trending long-form videos found this run.")
        return {"videos_found": 0, "videos_processed": 0, "clips_generated": 0}

    # Step 2: Filter out already-processed
    new_videos = filter_unprocessed(trending, str(ARCHIVE_FILE))

    if not new_videos:
        log.info("All trending videos already processed. Nothing new to do.")
        return {
            "videos_found": len(trending),
            "videos_new": 0,
            "videos_processed": 0,
            "clips_generated": 0,
        }

    total_clips = 0
    processed = 0

    for video in new_videos:
        log.info(
            "\n--- Processing [%d/%d]: %s ---",
            processed + 1,
            len(new_videos),
            video.title[:60],
        )
        log.info("  URL: %s | Views: %s | Duration: %ds", video.url, f"{video.view_count:,}", video.duration_s)

        # Step 3: Download
        log.info("Step 3: Downloading via Cobalt/yt-dlp...")
        video_path = download_video(video.url)
        if not video_path:
            log.warning("Download failed for %s — skipping", video.video_id)
            continue

        # Step 4: Clip
        log.info("Step 4: Clipping with Reelmint engine...")
        try:
            clips = clip_video(
                video_path=video_path,
                video_id=video.video_id,
                video_title=video.title,
                n_clips=CLIPS_PER_VIDEO,
                clip_len=CLIP_LENGTH_S,
                subtitles=SUBTITLES,
                face_track=FACE_TRACK,
                safety_boost=SAFETY_BOOST,
                language=SUBTITLE_LANGUAGE if SUBTITLE_LANGUAGE != "auto" else None,
                caption_style=CAPTION_STYLE,
            )
            total_clips += len(clips)
        except Exception as e:
            log.error("Clipping failed for %s: %s", video.video_id, e)
            clips = []

        # Step 5: Mark as processed (even if clipping failed, to avoid retrying)
        mark_processed(video.video_id, str(ARCHIVE_FILE))
        processed += 1

        # Cleanup: remove the downloaded source to save disk
        try:
            video_path.unlink(missing_ok=True)
        except Exception:
            pass

        log.info("  → %d clips generated", len(clips))

    summary = {
        "videos_found": len(trending),
        "videos_new": len(new_videos),
        "videos_processed": processed,
        "clips_generated": total_clips,
        "output_dir": str(OUTPUT_DIR),
    }
    log.info("\n" + "=" * 60)
    log.info("Pipeline run complete: %s", json.dumps(summary, indent=2))
    log.info("=" * 60)
    return summary


def run_daemon(interval_hours: float = 6.0) -> None:
    """Run the pipeline in a loop, sleeping between runs."""
    interval_s = interval_hours * 3600
    log.info("Daemon mode: running every %.1f hours", interval_hours)

    while True:
        try:
            run_once()
        except Exception as e:
            log.exception("Pipeline run failed: %s", e)

        log.info("Sleeping %.1f hours until next run...", interval_hours)
        time.sleep(interval_s)


def main() -> None:
    _setup_logging()

    parser = argparse.ArgumentParser(description="Auto-Shorts Pipeline")
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously on a schedule (default: every 6 hours)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=6.0,
        help="Hours between runs in daemon mode (default: 6)",
    )
    args = parser.parse_args()

    if args.daemon:
        run_daemon(interval_hours=args.interval)
    else:
        summary = run_once()
        if summary.get("error"):
            sys.exit(1)


if __name__ == "__main__":
    main()
