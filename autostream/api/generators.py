"""Generator control API — trigger music/visual generation."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from autostream.generators.music import generate_musicgen
from autostream.generators.visual import (
    generate_stable_diffusion_stub,
    image_to_loop_video,
)

router = APIRouter(prefix="/api/generators", tags=["generators"])


class MusicGenRequest(BaseModel):
    prompt: str
    genre: str = "lofi"
    duration_s: int = 30


class VisualGenRequest(BaseModel):
    prompt: str
    theme: str = "aesthetic"


class ImageToVideoRequest(BaseModel):
    image_path: str
    output_path: str
    duration_s: int = 10


@router.post("/music/generate")
def trigger_music_gen(req: MusicGenRequest):
    result = generate_musicgen(req.prompt, req.genre, req.duration_s)
    if result:
        return {"detail": "Generated", "path": result}
    return {"detail": "Generation stub — no model loaded. Place audio files in library/ manually."}


@router.post("/visuals/generate")
def trigger_visual_gen(req: VisualGenRequest):
    result = generate_stable_diffusion_stub(req.prompt, req.theme)
    if result:
        return {"detail": "Generated", "path": result}
    return {"detail": "Generation stub — no model loaded. Place images in visuals/ manually."}


@router.post("/visuals/image-to-video")
def trigger_image_to_video(req: ImageToVideoRequest):
    try:
        path = image_to_loop_video(req.image_path, req.output_path, req.duration_s)
        return {"detail": "Created", "path": path}
    except Exception as e:
        return {"detail": f"Failed: {e}"}
