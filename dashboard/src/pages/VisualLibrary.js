import React, { useEffect, useState } from "react";
import { getVisualThemes, getVisualFiles, getVisualsStats, deleteVisual } from "../api";

export default function VisualLibrary() {
  const [themes, setThemes] = useState([]);
  const [selected, setSelected] = useState("");
  const [files, setFiles] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getVisualThemes().then((t) => { setThemes(t); if (t.length) setSelected(t[0]); }).catch((e) => setError(e.message));
    getVisualsStats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    if (selected) getVisualFiles(selected).then(setFiles).catch((e) => setError(e.message));
  }, [selected]);

  const handleDelete = async (filename) => {
    if (!window.confirm(`Delete ${filename}?`)) return;
    try {
      await deleteVisual(selected, filename);
      setFiles(files.filter((f) => f.name !== filename));
    } catch (e) { setError(e.message); }
  };

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>Visual Library</h1>
      {error && <div style={{ color: "var(--red)", marginBottom: 12 }}>{error}</div>}

      {stats && (
        <div className="grid-3" style={{ marginBottom: 20 }}>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.total_visuals}</div>
            <div style={{ fontSize: 13, color: "var(--text-dim)" }}>Total Visuals</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{Object.keys(stats.themes || {}).length}</div>
            <div style={{ fontSize: 13, color: "var(--text-dim)" }}>Themes</div>
          </div>
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 28, fontWeight: 700 }}>{stats.themes?.[selected] || 0}</div>
            <div style={{ fontSize: 13, color: "var(--text-dim)" }}>In {selected || "—"}</div>
          </div>
        </div>
      )}

      <div style={{ marginBottom: 16, display: "flex", gap: 8 }}>
        {themes.map((t) => (
          <button key={t} className={t === selected ? "btn-primary" : "btn-secondary"} onClick={() => setSelected(t)}>
            {t}
          </button>
        ))}
      </div>

      {files.length === 0 ? (
        <div className="card" style={{ textAlign: "center", color: "var(--text-dim)", padding: 30 }}>
          No visuals in "{selected}". Upload video files to visuals/{selected}/.
        </div>
      ) : (
        <table>
          <thead>
            <tr><th>Name</th><th>Size</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {files.map((f) => (
              <tr key={f.name}>
                <td>{f.name}</td>
                <td>{f.size_mb} MB</td>
                <td><button className="btn-danger btn-small" onClick={() => handleDelete(f.name)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
