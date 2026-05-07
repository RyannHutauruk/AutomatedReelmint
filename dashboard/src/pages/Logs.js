import React, { useEffect, useState } from "react";
import { getStreamLogs, getGenerationLogs, getChannels } from "../api";

export default function Logs() {
  const [tab, setTab] = useState("stream");
  const [streamLogs, setStreamLogs] = useState([]);
  const [genLogs, setGenLogs] = useState([]);
  const [channels, setChannels] = useState([]);
  const [filterChannel, setFilterChannel] = useState("");
  const [error, setError] = useState("");

  useEffect(() => { getChannels().then(setChannels).catch(() => {}); }, []);

  useEffect(() => {
    const load = () => {
      if (tab === "stream") {
        getStreamLogs(filterChannel || null).then(setStreamLogs).catch((e) => setError(e.message));
      } else {
        getGenerationLogs().then(setGenLogs).catch((e) => setError(e.message));
      }
    };
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, [tab, filterChannel]);

  const levelColor = (level) => {
    if (level === "error") return "var(--red)";
    if (level === "warning") return "var(--yellow)";
    return "var(--text-dim)";
  };

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>Logs</h1>
      {error && <div style={{ color: "var(--red)", marginBottom: 12 }}>{error}</div>}

      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <button className={tab === "stream" ? "btn-primary" : "btn-secondary"} onClick={() => setTab("stream")}>
          Stream Logs
        </button>
        <button className={tab === "generation" ? "btn-primary" : "btn-secondary"} onClick={() => setTab("generation")}>
          Generation Logs
        </button>
      </div>

      {tab === "stream" && (
        <>
          <div style={{ marginBottom: 12 }}>
            <select value={filterChannel} onChange={(e) => setFilterChannel(e.target.value)} style={{ width: 200 }}>
              <option value="">All Channels</option>
              {channels.map((ch) => <option key={ch.id} value={ch.id}>{ch.name}</option>)}
            </select>
          </div>
          <table>
            <thead><tr><th>Time</th><th>Channel</th><th>Level</th><th>Message</th></tr></thead>
            <tbody>
              {streamLogs.map((log) => (
                <tr key={log.id}>
                  <td style={{ fontSize: 12, whiteSpace: "nowrap" }}>{log.timestamp?.replace("T", " ").slice(0, 19)}</td>
                  <td>{channels.find((c) => c.id === log.channel_id)?.name || log.channel_id}</td>
                  <td style={{ color: levelColor(log.level) }}>{log.level}</td>
                  <td>{log.message}</td>
                </tr>
              ))}
              {streamLogs.length === 0 && (
                <tr><td colSpan={4} style={{ textAlign: "center", color: "var(--text-dim)" }}>No logs yet</td></tr>
              )}
            </tbody>
          </table>
        </>
      )}

      {tab === "generation" && (
        <table>
          <thead><tr><th>Time</th><th>Type</th><th>Genre</th><th>Status</th><th>Message</th></tr></thead>
          <tbody>
            {genLogs.map((log) => (
              <tr key={log.id}>
                <td style={{ fontSize: 12, whiteSpace: "nowrap" }}>{log.timestamp?.replace("T", " ").slice(0, 19)}</td>
                <td>{log.gen_type}</td>
                <td>{log.genre}</td>
                <td>{log.status}</td>
                <td>{log.message}</td>
              </tr>
            ))}
            {genLogs.length === 0 && (
              <tr><td colSpan={5} style={{ textAlign: "center", color: "var(--text-dim)" }}>No generation logs yet</td></tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
