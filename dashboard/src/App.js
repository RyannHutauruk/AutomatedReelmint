import React from "react";
import { Routes, Route, NavLink } from "react-router-dom";
import Channels from "./pages/Channels";
import StreamControl from "./pages/StreamControl";
import MusicLibrary from "./pages/MusicLibrary";
import VisualLibrary from "./pages/VisualLibrary";
import MusicGenerator from "./pages/MusicGenerator";
import VisualGenerator from "./pages/VisualGenerator";
import Logs from "./pages/Logs";
import Settings from "./pages/Settings";

const NAV = [
  { to: "/", label: "Channels" },
  { to: "/stream", label: "Stream Control" },
  { to: "/library/music", label: "Music Library" },
  { to: "/library/visuals", label: "Visual Library" },
  { to: "/generate/music", label: "Music Gen" },
  { to: "/generate/visuals", label: "Visual Gen" },
  { to: "/logs", label: "Logs" },
  { to: "/settings", label: "Settings" },
];

export default function App() {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Sidebar */}
      <nav
        style={{
          width: 220,
          background: "var(--surface)",
          borderRight: "1px solid var(--border)",
          padding: "20px 0",
          flexShrink: 0,
        }}
      >
        <div style={{ padding: "0 20px 24px", fontSize: 18, fontWeight: 700, color: "var(--accent)" }}>
          AutoStream
        </div>
        {NAV.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            end={n.to === "/"}
            style={({ isActive }) => ({
              display: "block",
              padding: "10px 20px",
              fontSize: 14,
              color: isActive ? "#fff" : "var(--text-dim)",
              background: isActive ? "var(--accent2)" : "transparent",
              borderLeft: isActive ? "3px solid var(--accent)" : "3px solid transparent",
              textDecoration: "none",
            })}
          >
            {n.label}
          </NavLink>
        ))}
      </nav>

      {/* Main content */}
      <main style={{ flex: 1, padding: 28, overflowY: "auto" }}>
        <Routes>
          <Route path="/" element={<Channels />} />
          <Route path="/stream" element={<StreamControl />} />
          <Route path="/library/music" element={<MusicLibrary />} />
          <Route path="/library/visuals" element={<VisualLibrary />} />
          <Route path="/generate/music" element={<MusicGenerator />} />
          <Route path="/generate/visuals" element={<VisualGenerator />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}
