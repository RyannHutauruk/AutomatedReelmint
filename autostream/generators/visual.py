"""Visual generator — creates looping video backgrounds from images.

Supports:
- Converting static images to looping videos via ffmpeg
- Managing visual folders by theme
- Stubs for AI image generation (Stable Diffusion / DALL-E)
"""

from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from autostream.config import VISUALS_DIR

logger = logging.getLogger(__name__)

DEFAULT_THEMES = ["aesthetic", "dark-cafe", "nature"]


def ensure_theme_folders(themes: Optional[list[str]] = None) -> list[Path]:
    themes = themes or DEFAULT_THEMES
    paths = []
    for theme in themes:
        p = VISUALS_DIR / theme
        p.mkdir(parents=True, exist_ok=True)
        paths.append(p)
    return paths


def list_visuals(theme: str) -> list[dict]:
    folder = VISUALS_DIR / theme
    if not folder.exists():
        return []
    exts = (".mp4", ".mkv", ".webm", ".avi", ".mov")
    visuals = []
    for f in sorted(folder.iterdir()):
        if f.is_file() and f.suffix.lower() in exts:
            visuals.append({
                "name": f.name,
                "path": str(f),
                "size_mb": round(f.stat().st_size / (1024 * 1024), 2),
                "theme": theme,
            })
    return visuals


def image_to_loop_video(
    image_path: str,
    output_path: str,
    duration_s: int = 10,
    fps: int = 30,
) -> str:
    """Convert a static image to a short looping video using ffmpeg.

    The output video can be seamlessly looped with -stream_loop -1.
    """
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", image_path,
        "-c:v", "libx264",
        "-t", str(duration_s),
        "-pix_fmt", "yuv420p",
        "-vf", f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,fps={fps}",
        "-preset", "medium",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[-500:]}")
    logger.info("Created loop video: %s (%ds)", output_path, duration_s)
    return output_path


def create_seamless_loop(input_video: str, output_path: str, repeats: int = 3) -> str:
    """Create a seamless loop by concatenating a clip multiple times via concat demuxer."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for _ in range(repeats):
            f.write(f"file '{input_video}'\n")
        concat_list = f.name

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list,
        "-c", "copy",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    Path(concat_list).unlink(missing_ok=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concat failed: {result.stderr[-500:]}")
    logger.info("Created seamless loop: %s (%dx)", output_path, repeats)
    return output_path


def delete_visual(theme: str, filename: str) -> bool:
    path = VISUALS_DIR / theme / filename
    if path.exists():
        path.unlink()
        logger.info("Deleted %s/%s", theme, filename)
        return True
    return False


def list_themes() -> list[str]:
    if not VISUALS_DIR.exists():
        return []
    return sorted(d.name for d in VISUALS_DIR.iterdir() if d.is_dir())


def get_visuals_stats() -> dict:
    stats: dict[str, int] = {}
    total = 0
    for theme in list_themes():
        count = len(list_visuals(theme))
        stats[theme] = count
        total += count
    return {"themes": stats, "total_visuals": total}


# ---------- Generation stubs ----------

def generate_stable_diffusion_stub(prompt: str, theme: str) -> Optional[str]:
    """Stub for local Stable Diffusion image generation."""
    logger.info("SD stub: would generate '%s' for theme=%s", prompt, theme)
    return None


def generate_dalle_stub(prompt: str, theme: str) -> Optional[str]:
    """Stub for DALL-E API image generation."""
    logger.info("DALL-E stub: would generate '%s' for theme=%s", prompt, theme)
    return None
