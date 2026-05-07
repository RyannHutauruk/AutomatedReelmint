import React, { useEffect, useState } from "react";
import { getHealth, getChannels, updateChannel } from "../api";

export default function Settings() {
  const [health, setHealth] = useState(null);
  const [channels, setChannels] = useState([]);
  const [editId, setEditId] = useState(null);
  const [form, setForm] = useState({});
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {});
    getChannels().then(setChannels).catch(() => {});
  }, []);

  const startEdit = (ch) => {
    setEditId(ch.id);
    setForm({
      name: ch.name,
      stream_key: ch.stream_key,
      music_folder: ch.music_folder,
      visual_folder: ch.visual_folder,
      genre: ch.genre,
      playback_mode: ch.playback_mode,
      is_24_7: ch.is_24_7,
      schedule_start: ch.schedule_start,
      schedule_stop: ch.schedule_stop,
      titles: (ch.titles || []).join("\n"),
      oauth_client_id: "",
      oauth_client_secret: "",
    });
    setError("");
    setSuccess("");
  };

  const handleSave = async () => {
    setError("");
    setSuccess("");
    try {
      const data = {
        ...form,
        titles: form.titles ? form.titles.split("\n").filter(Boolean) : [],
      };
      if (!data.oauth_client_id) delete data.oauth_client_id;
      if (!data.oauth_client_secret) delete data.oauth_client_secret;
      await updateChannel(editId, data);
      setSuccess("Saved!");
      setEditId(null);
      getChannels().then(setChannels);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>Settings</h1>

      {health && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 8 }}>System Status</h3>
          <div>
            Status: <span style={{ color: "var(--green)" }}>{health.status}</span>
          </div>
          <div>
            Active streams: {health.streaming_channels?.length || 0}
          </div>
        </div>
      )}

      <div className="card" style={{ marginBottom: 20 }}>
        <h3 style={{ marginBottom: 8 }}>YouTube API Setup</h3>
        <p style={{ color: "var(--text-dim)", fontSize: 13 }}>
          1. Go to <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noreferrer">Google Cloud Console</a><br />
          2. Enable YouTube Data API v3 and YouTube Live Streaming API<br />
          3. Create OAuth 2.0 credentials (Desktop app type)<br />
          4. Enter Client ID and Secret in each channel's settings below
        </p>
      </div>

      {error && <div style={{ color: "var(--red)", marginBottom: 12 }}>{error}</div>}
      {success && <div style={{ color: "var(--green)", marginBottom: 12 }}>{success}</div>}

      <h2 style={{ marginBottom: 12 }}>Channel Settings</h2>
      {channels.map((ch) => (
        <div key={ch.id} className="card" style={{ marginBottom: 12 }}>
          {editId === ch.id ? (
            <div>
              <div className="grid-2" style={{ marginBottom: 12 }}>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Name</label>
                  <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Stream Key</label>
                  <input value={form.stream_key} onChange={(e) => setForm({ ...form, stream_key: e.target.value })} type="password" />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Music Folder</label>
                  <input value={form.music_folder} onChange={(e) => setForm({ ...form, music_folder: e.target.value })} />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Visual Folder</label>
                  <input value={form.visual_folder} onChange={(e) => setForm({ ...form, visual_folder: e.target.value })} />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Genre</label>
                  <input value={form.genre} onChange={(e) => setForm({ ...form, genre: e.target.value })} />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Playback</label>
                  <select value={form.playback_mode} onChange={(e) => setForm({ ...form, playback_mode: e.target.value })}>
                    <option value="shuffle">Shuffle</option>
                    <option value="sequential">Sequential</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>
                    <input type="checkbox" checked={form.is_24_7} onChange={(e) => setForm({ ...form, is_24_7: e.target.checked })} style={{ width: "auto", marginRight: 6 }} />
                    24/7 Mode
                  </label>
                </div>
              </div>
              {!form.is_24_7 && (
                <div className="grid-2" style={{ marginBottom: 12 }}>
                  <div>
                    <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Start (HH:MM)</label>
                    <input value={form.schedule_start} onChange={(e) => setForm({ ...form, schedule_start: e.target.value })} />
                  </div>
                  <div>
                    <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Stop (HH:MM)</label>
                    <input value={form.schedule_stop} onChange={(e) => setForm({ ...form, schedule_stop: e.target.value })} />
                  </div>
                </div>
              )}
              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Title Rotation (one per line)</label>
                <textarea rows={3} value={form.titles} onChange={(e) => setForm({ ...form, titles: e.target.value })} />
              </div>
              <div className="grid-2" style={{ marginBottom: 12 }}>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>OAuth Client ID (optional)</label>
                  <input value={form.oauth_client_id} onChange={(e) => setForm({ ...form, oauth_client_id: e.target.value })} placeholder="Leave blank to keep current" />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>OAuth Client Secret (optional)</label>
                  <input value={form.oauth_client_secret} onChange={(e) => setForm({ ...form, oauth_client_secret: e.target.value })} type="password" placeholder="Leave blank to keep current" />
                </div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn-success" onClick={handleSave}>Save</button>
                <button className="btn-secondary" onClick={() => setEditId(null)}>Cancel</button>
              </div>
            </div>
          ) : (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <div style={{ fontWeight: 600 }}>{ch.name}</div>
                <div style={{ fontSize: 13, color: "var(--text-dim)" }}>
                  {ch.genre} &middot; {ch.music_folder} &middot; {ch.visual_folder} &middot; {ch.playback_mode}
                </div>
              </div>
              <button className="btn-secondary btn-small" onClick={() => startEdit(ch)}>Edit</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
