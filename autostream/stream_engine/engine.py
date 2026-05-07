"""Core streaming engine — merges audio + looping video and pushes RTMP."""

from __future__ import annotations

import logging
import os
import random
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

from autostream.config import (
    BASE_DIR,
    DEFAULT_AUDIO_BITRATE,
    DEFAULT_FPS,
    DEFAULT_RESOLUTION,
    DEFAULT_RTMP_URL,
    DEFAULT_VIDEO_BITRATE,
    LIBRARY_DIR,
    VISUALS_DIR,
)

logger = logging.getLogger(__name__)

# Track running ffmpeg processes per channel
_running: dict[int, subprocess.Popen] = {}
_threads: dict[int, threading.Thread] = {}
_stop_events: dict[int, threading.Event] = {}


def _pick_random_file(folder: Path, extensions: tuple[str, ...]) -> Optional[Path]:
    """Pick a random file from *folder* matching the given extensions."""
    if not folder.exists():
        return None
    files = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in extensions]
    return random.choice(files) if files else None


AUDIO_EXTS = (".wav", ".mp3", ".flac", ".ogg", ".aac", ".m4a")
VIDEO_EXTS = (".mp4", ".mkv", ".webm", ".avi", ".mov")


def _build_ffmpeg_cmd(
    visual_path: Path,
    audio_path: Path,
    stream_key: str,
    rtmp_url: str = DEFAULT_RTMP_URL,
) -> list[str]:
    """Build the ffmpeg command list for streaming."""
    width, height = DEFAULT_RESOLUTION.split("x")
    return [
        "ffmpeg",
        "-re",
        "-stream_loop", "-1",
        "-i", str(visual_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-b:v", DEFAULT_VIDEO_BITRATE,
        "-maxrate", DEFAULT_VIDEO_BITRATE,
        "-bufsize", "5000k",
        "-pix_fmt", "yuv420p",
        "-g", str(DEFAULT_FPS * 2),
        "-c:a", "aac",
        "-b:a", DEFAULT_AUDIO_BITRATE,
        "-ar", "44100",
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        "-f", "flv",
        f"{rtmp_url}/{stream_key}",
    ]


def _stream_loop(
    channel_id: int,
    music_folder: Path,
    visual_folder: Path,
    stream_key: str,
    playback_mode: str,
    stop_event: threading.Event,
    on_song_change: Optional[callable] = None,
) -> None:
    """Continuously stream songs. When one ends, pick the next."""
    audio_files = sorted(
        [f for f in music_folder.iterdir() if f.is_file() and f.suffix.lower() in AUDIO_EXTS]
    ) if music_folder.exists() else []

    if not audio_files:
        logger.error("Channel %d: No audio files in %s", channel_id, music_folder)
        return

    visual = _pick_random_file(visual_folder, VIDEO_EXTS)
    if visual is None:
        logger.error("Channel %d: No visual files in %s", channel_id, visual_folder)
        return

    if playback_mode == "shuffle":
        random.shuffle(audio_files)

    idx = 0
    while not stop_event.is_set():
        audio = audio_files[idx % len(audio_files)]
        idx += 1

        logger.info("Channel %d: Now playing %s with visual %s", channel_id, audio.name, visual.name)
        if on_song_change:
            on_song_change(channel_id, str(audio), str(visual))

        cmd = _build_ffmpeg_cmd(visual, audio, stream_key)
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            _running[channel_id] = proc

            while proc.poll() is None:
                if stop_event.is_set():
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    return
                time.sleep(1)

            if proc.returncode != 0:
                stderr_out = proc.stderr.read().decode(errors="replace")[-500:]
                logger.warning("Channel %d: ffmpeg exited %d — %s", channel_id, proc.returncode, stderr_out)
                time.sleep(2)

        except Exception as exc:
            logger.exception("Channel %d: ffmpeg error — %s", channel_id, exc)
            time.sleep(5)

        # Rotate visual occasionally
        new_visual = _pick_random_file(visual_folder, VIDEO_EXTS)
        if new_visual:
            visual = new_visual

    logger.info("Channel %d: Stream loop stopped.", channel_id)


def start_stream(
    channel_id: int,
    music_folder: str,
    visual_folder: str,
    stream_key: str,
    playback_mode: str = "shuffle",
    on_song_change: Optional[callable] = None,
) -> bool:
    """Start streaming for a channel. Returns True if started."""
    if channel_id in _threads and _threads[channel_id].is_alive():
        logger.warning("Channel %d already streaming.", channel_id)
        return False

    music_path = Path(music_folder) if Path(music_folder).is_absolute() else BASE_DIR / music_folder
    visual_path = Path(visual_folder) if Path(visual_folder).is_absolute() else BASE_DIR / visual_folder

    stop_event = threading.Event()
    _stop_events[channel_id] = stop_event

    t = threading.Thread(
        target=_stream_loop,
        args=(channel_id, music_path, visual_path, stream_key, playback_mode, stop_event, on_song_change),
        daemon=True,
        name=f"stream-{channel_id}",
    )
    _threads[channel_id] = t
    t.start()
    logger.info("Channel %d: Stream started.", channel_id)
    return True


def stop_stream(channel_id: int) -> bool:
    """Stop streaming for a channel. Returns True if stopped."""
    stop_event = _stop_events.pop(channel_id, None)
    if stop_event:
        stop_event.set()

    proc = _running.pop(channel_id, None)
    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

    thread = _threads.pop(channel_id, None)
    if thread:
        thread.join(timeout=10)

    logger.info("Channel %d: Stream stopped.", channel_id)
    return True


def is_streaming(channel_id: int) -> bool:
    t = _threads.get(channel_id)
    return t is not None and t.is_alive()


def get_running_channels() -> list[int]:
    return [cid for cid, t in _threads.items() if t.is_alive()]
