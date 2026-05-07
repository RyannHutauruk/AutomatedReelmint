import React, { useEffect, useState } from "react";
import { getMusicGenres, getMusicTracks, getMusicStats, deleteTrack } from "../api";

export default function MusicLibrary() {
  const [genres, setGenres] = useState([]);
  const [selected, setSelected] = useState("");
  const [tracks, setTracks] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getMusicGenres().then((g) => { setGenres(g); if (g.length) setSelected(g[0]); }).catch((e) => setError(e.message));
    getMusicStats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    if (selected) getMusicTracks(selected).then(setTracks).catch((e) => setError(e.message));
  }, [selected]);

  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete ${filename}?`)) return;
    try {
      await deleteTrack(selected, filename);
      setTracks(tracks.filter((t) => t.name !== filename));
    } catch (e) { setError(e.message); }
  };

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>Music Library</h1>
      {error && <div style={{ color: "var(--red)", marginBottom: 12 }}>{error}</div>}

      {stats && (
        <div className="grid-3" style={{ marginBottom: 20 }}>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.total_tracks}</div>
            <div style={{ fontSize: 13, color: "var(--text-dim)" }}>Total Tracks</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{Object.keys(stats.genres || {}).length}</div>
            <div style={{ fontSize: 13, color: "var(--text-dim)" }}>Genres</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.genres?.[selected] || 0}</div>
            <div style={{ fontSize: 13, color: "var(--text-dim)" }}>In {selected || "—"}</div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
        {genres.map((g) => (
          <button key={g} className={g === selected ? "btn-primary" : "btn-secondary"} onClick={() => setSelected(g)}>
            {g}
          </button>
        ))}
      </div>

      {tracks.length === 0 ? (
        <div className="card" style={{ textAlign: "center", color: "var(--text-dim)", padding: 30 }}>
          No tracks in "{selected}". Upload audio files to library/{selected}/.
        </div>
      ) : (
        <table>
          <thead>
            <tr><th>Name</th><th>Size</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {tracks.map((t) => (
              <tr key={t.name}>
                <td>{t.name}</td>
                <td>{t.size_mb} MB</td>
                <td><button className="btn-danger btn-small" onClick={() => handleDelete(t.name)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
