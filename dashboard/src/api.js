const BASE = process.env.REACT_APP_API_URL || "";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

// Channels
export const getChannels = () => request("/api/channels");
export const getChannel = (id) => request(`/api/channels/${id}`);
export const createChannel = (data) =>
  request("/api/channels", { method: "POST", body: JSON.stringify(data) });
export const updateChannel = (id, data) =>
  request(`/api/channels/${id}`, { method: "PUT", body: JSON.stringify(data) });
export const deleteChannel = (id) =>
  request(`/api/channels/${id}`, { method: "DELETE" });
export const startStream = (id) =>
  request(`/api/channels/${id}/start`, { method: "POST" });
export const stopStream = (id) =>
  request(`/api/channels/${id}/stop`, { method: "POST" });

// Library
export const getMusicStats = () => request("/api/library/music/stats");
export const getMusicGenres = () => request("/api/library/music/genres");
export const getMusicTracks = (genre) => request(`/api/library/music/${genre}`);
export const deleteTrack = (genre, filename) =>
  request(`/api/library/music/${genre}/${filename}`, { method: "DELETE" });

export const getVisualsStats = () => request("/api/library/visuals/stats");
export const getVisualThemes = () => request("/api/library/visuals/themes");
export const getVisualFiles = (theme) => request(`/api/library/visuals/${theme}`);
export const deleteVisual = (theme, filename) =>
  request(`/api/library/visuals/${theme}/${filename}`, { method: "DELETE" });

// Generators
export const triggerMusicGen = (data) =>
  request("/api/generators/music/generate", { method: "POST", body: JSON.stringify(data) });
export const triggerVisualGen = (data) =>
  request("/api/generators/visuals/generate", { method: "POST", body: JSON.stringify(data) });

// Logs
export const getStreamLogs = (channelId, limit = 100) => {
  const params = new URLSearchParams({ limit });
  if (channelId) params.set("channel_id", channelId);
  return request(`/api/logs/stream?${params}`);
};
export const getGenerationLogs = (genType, limit = 100) => {
  const params = new URLSearchParams({ limit });
  if (genType) params.set("gen_type", genType);
  return request(`/api/logs/generation?${params}`);
};

// Health
export const getHealth = () => request("/api/health");
