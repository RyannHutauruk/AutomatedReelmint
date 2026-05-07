import React, { useState } from "react";
import { triggerMusicGen } from "../api";

export default function MusicGenerator() {
  const [prompt, setPrompt] = useState("");
  const [genre, setGenre] = useState("lofi");
  const [duration, setDuration] = useState(30);
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult("");
    try {
      const res = await triggerMusicGen({ prompt, genre, duration_s: duration });
      setResult(res.detail);
    } catch (e) {
      setResult(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>Music Generator</h1>

      <div className="card" style={{ marginBottom: 20 }}>
        <p style={{ color: "var(--text-dim)", marginBottom: 16 }}>
          Generate music using AI. Currently supports MusicGen (Meta) as a local, unlimited, open-source option.
          Suno AI and Udio stubs are available but require browser automation.
        </p>

        <form onSubmit={handleGenerate}>
          <div className="grid-2" style={{ marginBottom: 12 }}>
            <div>
              <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Genre</label>
              <select value={genre} onChange={(e) => setGenre(e.target.value)}>
                <option value="lofi">Lo-fi</option>
                <option value="jazz">Jazz</option>
                <option value="ambient">Ambient</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Duration (seconds)</label>
              <input type="number" value={duration} onChange={(e) => setDuration(Number(e.target.value))} min={5} max={300} />
            </div>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Prompt</label>
            <textarea rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="chill lo-fi beats with soft piano and rain sounds" required />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Generating..." : "Generate"}
          </button>
        </form>
      </div>

      {result && (
        <div className="card">
          <strong>Result:</strong> {result}
        </div>
      )}

      <div className="card" style={{ marginTop: 20 }}>
        <h3 style={{ marginBottom: 12 }}>Alternative Sources</h3>
        <table>
          <thead><tr><th>Source</th><th>Free Quota</th><th>Notes</th></tr></thead>
          <tbody>
            <tr><td>MusicGen (Meta)</td><td>Unlimited</td><td>Local, open-source, MIT licensed</td></tr>
            <tr><td>Suno AI</td><td>25 songs/day</td><td>Browser automation required</td></tr>
            <tr><td>Udio</td><td>50 songs/day</td><td>Browser automation required</td></tr>
            <tr><td>YouTube Audio Library</td><td>Unlimited</td><td>Copyright-safe, manual download</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
