import React, { useEffect, useState } from "react";
import { getChannels, startStream, stopStream } from "../api";

export default function StreamControl() {
  const [channels, setChannels] = useState([]);
  const [error, setError] = useState("");

  const load = () => getChannels().then(setChannels).catch((e) => setError(e.message));

  useEffect(() => { load(); const t = setInterval(load, 3000); return () => clearInterval(t); }, []);

  const handleStart = async (id) => {
    setError("");
    try { await startStream(id); load(); } catch (e) { setError(e.message); }
  };

  const handleStop = async (id) => {
    setError("");
    try { await stopStream(id); load(); } catch (e) { setError(e.message); }
  };

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>Stream Control</h1>
      {error && <div style={{ color: "var(--red)", marginBottom: 12 }}>{error}</div>}

      {channels.length === 0 ? (
        <div className="card" style={{ textAlign: "center", color: "var(--text-dim)", padding: 40 }}>
          No channels configured. Add channels first.
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Channel</th>
              <th>Status</th>
              <th>Genre</th>
              <th>Now Playing</th>
              <th>Visual</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {channels.map((ch) => (
              <tr key={ch.id}>
                <td style={{ fontWeight: 600 }}>{ch.name}</td>
                <td>
                  <span className={`badge ${ch.is_active ? "badge-live" : "badge-offline"}`}>
                    {ch.is_active ? "LIVE" : "OFFLINE"}
                  </span>
                </td>
                <td>{ch.genre}</td>
                <td style={{ fontSize: 13 }}>{ch.current_song ? ch.current_song.split("/").pop() : "—"}</td>
                <td style={{ fontSize: 13 }}>{ch.current_visual ? ch.current_visual.split("/").pop() : "—"}</td>
                <td>
                  {ch.is_active ? (
                    <button className="btn-danger btn-small" onClick={() => handleStop(ch.id)}>Stop</button>
                  ) : (
                    <button className="btn-success btn-small" onClick={() => handleStart(ch.id)}>Start</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
