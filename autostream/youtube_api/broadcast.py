"""YouTube Live Streaming API wrapper — broadcast & stream management."""

from __future__ import annotations

import logging
from typing import Optional

from googleapiclient.discovery import build

from autostream.youtube_api.auth import get_credentials

logger = logging.getLogger(__name__)

API_SERVICE = "youtube"
API_VERSION = "v3"


def _get_service(channel_id: int):
    creds = get_credentials(channel_id)
    if not creds:
        raise RuntimeError(f"Channel {channel_id}: No valid OAuth credentials.")
    return build(API_SERVICE, API_VERSION, credentials=creds)


def create_broadcast(
    channel_id: int,
    title: str,
    description: str = "",
    privacy: str = "public",
) -> dict:
    """Create a new live broadcast and bind it to a stream."""
    service = _get_service(channel_id)

    broadcast = service.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "scheduledStartTime": "1970-01-01T00:00:00Z",
            },
            "status": {"privacyStatus": privacy},
            "contentDetails": {
                "enableAutoStart": True,
                "enableAutoStop": False,
                "latencyPreference": "ultraLow",
            },
        },
    ).execute()

    stream = service.liveStreams().insert(
        part="snippet,cdn",
        body={
            "snippet": {"title": f"{title} — stream"},
            "cdn": {
                "frameRate": "30fps",
                "ingestionType": "rtmp",
                "resolution": "1080p",
            },
        },
    ).execute()

    service.liveBroadcasts().bind(
        part="id,contentDetails",
        id=broadcast["id"],
        streamId=stream["id"],
    ).execute()

    stream_key = stream["cdn"]["ingestionInfo"]["streamName"]

    logger.info("Channel %d: Broadcast %s created, stream key obtained.", channel_id, broadcast["id"])
    return {
        "broadcast_id": broadcast["id"],
        "stream_id": stream["id"],
        "stream_key": stream_key,
        "rtmp_url": stream["cdn"]["ingestionInfo"]["ingestionAddress"],
    }


def update_broadcast_title(channel_id: int, broadcast_id: str, title: str) -> None:
    service = _get_service(channel_id)
    service.liveBroadcasts().update(
        part="snippet",
        body={
            "id": broadcast_id,
            "snippet": {"title": title},
        },
    ).execute()
    logger.info("Channel %d: Broadcast %s title updated to '%s'.", channel_id, broadcast_id, title)


def transition_broadcast(channel_id: int, broadcast_id: str, status: str) -> None:
    """Transition broadcast: testing → live → complete."""
    service = _get_service(channel_id)
    service.liveBroadcasts().transition(
        broadcastStatus=status,
        id=broadcast_id,
        part="id,status",
    ).execute()
    logger.info("Channel %d: Broadcast %s transitioned to %s.", channel_id, broadcast_id, status)


def stop_broadcast(channel_id: int, broadcast_id: str) -> None:
    transition_broadcast(channel_id, broadcast_id, "complete")


def list_broadcasts(channel_id: int, status: str = "active") -> list[dict]:
    service = _get_service(channel_id)
    resp = service.liveBroadcasts().list(
        part="snippet,status",
        broadcastStatus=status,
        maxResults=25,
    ).execute()
    return resp.get("items", [])
