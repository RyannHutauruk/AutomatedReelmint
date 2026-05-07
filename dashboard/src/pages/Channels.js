import React, { useEffect, useState } from "react";
import { getChannels, createChannel, deleteChannel } from "../api";

export default function Channels() {
  const [channels, setChannels] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    name: "",
    stream_key: "",
    music_folder: "library/lofi",
    visual_folder: "visuals/aesthetic",
    genre: "lofi",
    playback_mode: "shuffle",
    is_24_7: true,
    schedule_start: "",
    schedule_stop: "",
    titles: "",
  });
  const [error, setError] = useState("");

  const load = () => getChannels().then(setChannels).catch((e) => setError(e.message));

  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await createChannel({
        ...form,
        titles: form.titles ? form.titles.split("\n").filter(Boolean) : [],
      });
      setShowForm(false);
      setForm({ name: "", stream_key: "", music_folder: "library/lofi", visual_folder: "visuals/aesthetic", genre: "lofi", playback_mode: "shuffle", is_24_7: true, schedule_start: "", schedule_stop: "", titles: "" });
      load();
    } catch (e) {
      setError(e.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this channel?")) return;
    try { await deleteChannel(id); load(); } catch (e) { setError(e.message); }
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <h1>Channels</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "+ Add Channel"}
        </button>
      </div>

      {error && <div style={{ color: "var(--red)", marginBottom: 12 }}>{error}</div>}

      {showForm && (
        <form onSubmit={handleCreate} className="card" style={{ marginBottom: 20 }}>
          <div className="grid-2" style={{ marginBottom: 12 }}>
            <div>
              <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Channel Name</label>
              <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            </div>
            <div>
              <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Stream Key</label>
              <input value={form.stream_key} onChange={(e) => setForm({ ...form, stream_key: e.target.value })} placeholder="From YouTube Studio" />
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
              <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Playback Mode</label>
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
            {!form.is_24_7 && (
              <>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Schedule Start (HH:MM)</label>
                  <input value={form.schedule_start} onChange={(e) => setForm({ ...form, schedule_start: e.target.value })} placeholder="08:00" />
                </div>
                <div>
                  <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Schedule Stop (HH:MM)</label>
                  <input value={form.schedule_stop} onChange={(e) => setForm({ ...form, schedule_stop: e.target.value })} placeholder="22:00" />
                </div>
              </>
            )}
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Title Rotation (one per line)</label>
            <textarea rows={3} value={form.titles} onChange={(e) => setForm({ ...form, titles: e.target.value })} placeholder={"lofi hip hop radio - beats to relax/study to\nchill vibes 24/7 stream"} />
          </div>
          <button type="submit" className="btn-success">Create Channel</button>
        </form>
      )}

      {channels.length === 0 && !showForm && (
        <div className="card" style={{ textAlign: "center", color: "var(--text-dim)", padding: 40 }}>
          No channels yet. Click "+ Add Channel" to get started.
        </div>
      )}

      <div style={{ display: "grid", gap: 16 }}>
        {channels.map((ch) => (
          <div key={ch.id} className="card" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 16 }}>
                {ch.name}
                <span className={`badge ${ch.is_active ? "badge-live" : "badge-offline"}`} style={{ marginLeft: 10 }}>
                  {ch.is_active ? "LIVE" : "OFFLINE"}
                </span>
              </div>
              <div style={{ fontSize: 13, color: "var(--text-dim)", marginTop: 4 }}>
                {ch.genre} &middot; {ch.music_folder} &middot; {ch.playback_mode}
                {ch.is_24_7 ? " &middot; 24/7" : ` &middot; ${ch.schedule_start}-${ch.schedule_stop}`}
              </div>
              {ch.current_song && (
                <div style={{ fontSize: 12, color: "var(--accent)", marginTop: 4 }}>
                  Now playing: {ch.current_song.split("/").pop()}
                </div>
              )}
            </div>
            <div>
              <button className="btn-danger btn-small" onClick={() => handleDelete(ch.id)}>Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
