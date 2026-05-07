import React, { useState } from "react";
import { triggerVisualGen } from "../api";

export default function VisualGenerator() {
  const [prompt, setPrompt] = useState("");
  const [theme, setTheme] = useState("aesthetic");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult("");
    try {
      const res = await triggerVisualGen({ prompt, theme });
      setResult(res.detail);
    } catch (e) {
      setResult(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: 20 }}>Visual Generator</h1>

      <div className="card" style={{ marginBottom: 20 }}>
        <p style={{ color: "var(--text-dim)", marginBottom: 16 }}>
          Generate looping video backgrounds from AI-generated images.
          Supports Stable Diffusion (local) and DALL-E API.
        </p>

        <form onSubmit={handleGenerate}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Theme</label>
            <select value={theme} onChange={(e) => setTheme(e.target.value)}>
              <option value="aesthetic">Aesthetic</option>
              <option value="dark-cafe">Dark Cafe</option>
              <option value="nature">Nature</option>
            </select>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 12, color: "var(--text-dim)" }}>Prompt</label>
            <textarea rows={3} value={prompt} onChange={(e) => setPrompt(e.target.value)} placeholder="cozy anime cafe interior, warm lighting, rain on window, lo-fi aesthetic" required />
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
        <h3 style={{ marginBottom: 12 }}>Image → Video Conversion</h3>
        <p style={{ color: "var(--text-dim)" }}>
          After generating or uploading images, use the API endpoint
          <code style={{ background: "var(--surface2)", padding: "2px 6px", borderRadius: 4 }}> POST /api/generators/visuals/image-to-video</code>
          to convert static images into seamless looping videos using ffmpeg.
        </p>
      </div>
    </div>
  );
}
