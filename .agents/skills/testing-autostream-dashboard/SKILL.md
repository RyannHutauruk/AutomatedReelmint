---
name: testing-autostream-dashboard
description: Test the YouTube Auto Stream dashboard end-to-end. Use when verifying dashboard UI, channel CRUD, library pages, or API changes.
---

# Testing the Auto Stream Dashboard

## Prerequisites
- Python 3.12+ with venv
- Node.js 18+
- ffmpeg installed (`sudo apt-get install -y ffmpeg`)

## Devin Secrets Needed
- None for local testing. YouTube API credentials are only needed for actual streaming.

## Setup

### 1. Backend
```bash
cd <repo_root>
python3 -m venv .venv && source .venv/bin/activate
pip install -r autostream/requirements.txt
uvicorn autostream.main:app --host 0.0.0.0 --port 8000 &
# Verify: curl http://localhost:8000/api/health → {"status":"ok",...}
```

### 2. Frontend
Ensure `dashboard/package.json` has `"proxy": "http://localhost:8000"` so the React dev server forwards `/api/*` calls to FastAPI. If missing, add it.

```bash
cd <repo_root>/dashboard
npm install
BROWSER=none PORT=3000 npm start &
# Verify: curl http://localhost:3000 returns HTML
# Verify proxy: curl http://localhost:3000/api/health returns JSON from backend
```

## Key Test Flow: Channel CRUD
1. **Channels page** (`/`) — verify empty state "No channels yet"
2. **Create channel** — click "+ Add Channel", fill name + stream_key, submit → channel card appears with OFFLINE badge
3. **Stream Control** (`/stream`) — verify channel row with Start button and OFFLINE status
4. **Start stream** — click Start; with empty library folders the stream stays OFFLINE (no audio files). This is expected.
5. **Music Library** (`/library/music`) — verify stats (0 tracks, 3 genres), genre tabs (ambient/jazz/lofi), empty state message
6. **Visual Library** (`/library/visuals`) — verify stats (0 visuals, 3 themes), theme tabs (aesthetic/dark-cafe/nature)
7. **Settings** (`/settings`) — edit channel name → Save → verify "Saved!" message and name persists on Channels page
8. **Logs** (`/logs`) — Stream Logs tab shows entries from start attempt; Generation Logs tab shows empty state
9. **Music Gen** (`/generate/music`) — form with genre/duration/prompt + Alternative Sources table
10. **Visual Gen** (`/generate/visuals`) — form with theme/prompt + Image→Video Conversion docs
11. **Delete channel** — click Delete on Channels page → confirm dialog → empty state returns

## Known Issues
- Channel card subtitle may render `&middot;` as literal text instead of the `·` character. This is a JSX escaping issue in `dashboard/src/pages/Channels.js`.
- The confirm dialog on delete is a browser `window.confirm()` — the computer tool may time out waiting for it. Take a screenshot first, then click OK in a separate action.
- The scheduler auto-starts streams for 24/7 channels every minute, so you may see multiple "Auto-started (24/7 mode)" log entries.

## API Endpoints for Quick Verification
- `GET /api/health` — system status
- `GET /api/channels` — list channels
- `POST /api/channels` — create channel (JSON body with `name`, `stream_key`, etc.)
- `GET /api/logs/stream?limit=10` — recent stream logs
- `GET /api/library/music/genres` — list music genres
- `GET /api/library/visuals/themes` — list visual themes
