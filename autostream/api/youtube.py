"""YouTube API routes — OAuth, broadcast management."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from autostream.youtube_api.auth import (
    authorize_channel,
    has_credentials,
    save_client_secret,
)
from autostream.youtube_api.broadcast import (
    create_broadcast,
    list_broadcasts,
    stop_broadcast,
    update_broadcast_title,
)

router = APIRouter(prefix="/api/youtube", tags=["youtube"])


class OAuthSetup(BaseModel):
    channel_id: int
    client_id: str
    client_secret: str


class BroadcastCreate(BaseModel):
    channel_id: int
    title: str
    description: str = ""
    privacy: str = "public"


class TitleUpdate(BaseModel):
    channel_id: int
    broadcast_id: str
    title: str


@router.post("/oauth/setup")
def setup_oauth(data: OAuthSetup):
    save_client_secret(data.channel_id, data.client_id, data.client_secret)
    return {"detail": "Client secret saved. Call /oauth/authorize to complete flow."}


@router.post("/oauth/authorize/{channel_id}")
def authorize(channel_id: int):
    creds = authorize_channel(channel_id)
    if not creds:
        raise HTTPException(status_code=400, detail="Authorization failed. Check client secret file.")
    return {"detail": "Authorized successfully"}


@router.get("/oauth/status/{channel_id}")
def oauth_status(channel_id: int):
    return {"has_credentials": has_credentials(channel_id)}


@router.post("/broadcast/create")
def api_create_broadcast(data: BroadcastCreate):
    try:
        result = create_broadcast(data.channel_id, data.title, data.description, data.privacy)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast/update-title")
def api_update_title(data: TitleUpdate):
    try:
        update_broadcast_title(data.channel_id, data.broadcast_id, data.title)
        return {"detail": "Title updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/broadcast/list/{channel_id}")
def api_list_broadcasts(channel_id: int, status: str = "active"):
    try:
        return list_broadcasts(channel_id, status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast/stop")
def api_stop_broadcast(channel_id: int, broadcast_id: str):
    try:
        stop_broadcast(channel_id, broadcast_id)
        return {"detail": "Broadcast stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
