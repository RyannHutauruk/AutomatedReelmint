"""OAuth2 helpers for per-channel YouTube authentication."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from autostream.config import CREDENTIALS_DIR

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]


def _token_path(channel_id: int) -> Path:
    return CREDENTIALS_DIR / f"token_channel_{channel_id}.json"


def _client_secret_path(channel_id: int) -> Path:
    return CREDENTIALS_DIR / f"client_secret_channel_{channel_id}.json"


def save_client_secret(channel_id: int, client_id: str, client_secret: str) -> Path:
    """Persist OAuth client credentials for a channel."""
    secret_data = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    path = _client_secret_path(channel_id)
    path.write_text(json.dumps(secret_data, indent=2))
    return path


def get_credentials(channel_id: int) -> Optional[Credentials]:
    """Load or refresh OAuth credentials for a channel."""
    token_file = _token_path(channel_id)
    creds: Optional[Credentials] = None

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_file.write_text(creds.to_json())
        except Exception:
            logger.warning("Channel %d: Token refresh failed, re-auth needed.", channel_id)
            creds = None

    return creds


def authorize_channel(channel_id: int) -> Optional[Credentials]:
    """Run the OAuth2 installed-app flow (opens browser)."""
    secret_file = _client_secret_path(channel_id)
    if not secret_file.exists():
        logger.error("Channel %d: No client_secret file at %s", channel_id, secret_file)
        return None

    flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), SCOPES)
    creds = flow.run_local_server(port=0)

    token_file = _token_path(channel_id)
    token_file.write_text(creds.to_json())
    logger.info("Channel %d: OAuth token saved.", channel_id)
    return creds


def has_credentials(channel_id: int) -> bool:
    return _token_path(channel_id).exists()
