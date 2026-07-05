// src/api/shoutout.js
import API from "./axios.js";

// ---------- shoutouts ----------
export const getShoutouts = async () => {
  return await API.get("/shoutouts");
};

export const postShoutout = async (data) => {
  return await API.post("/shoutouts", data);
};

// ---------- reactions ----------
export const getReactionsFor = async (shoutoutId) => {
  // expects backend route: GET /reactions/{shoutout_id}
  return await API.get(`/reactions/${shoutoutId}`);
};

// Toggle reaction (current user)
export const toggleReaction = async ({ shoutout_id, type }) => {
  // backend: POST /reactions/toggle
  // body: { shoutout_id, type }
  return await API.post("/reactions/toggle", { shoutout_id, type });
};

// ✅ alias for compatibility with your frontend import
export const postReaction = toggleReaction;

// ---------- comments ----------
export const getCommentsFor = async (shoutoutId) => {
  // backend: GET /comments/{shoutout_id}
  return await API.get(`/comments/${shoutoutId}`);
};

export const postComment = async (data) => {
  // backend: POST /comments
  return await API.post("/comments", data);
};
