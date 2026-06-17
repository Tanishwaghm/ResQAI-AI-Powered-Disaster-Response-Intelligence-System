import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      "Connection error. Is the backend running?";
    return Promise.reject(new Error(message));
  }
);

export const healthCheck = () => api.get("/health");

export const sendChat = (message, sessionId = "default", useRag = true) =>
  api.post("/chat", { message, session_id: sessionId, use_rag: useRag });

export const sendAgentChat = (message, sessionId = "default", forceAgent = null) =>
  api.post("/agent-chat", { message, session_id: sessionId, force_agent: forceAgent });

export const uploadPDF = (file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/upload-pdf", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {
      if (onProgress) onProgress(Math.round((e.loaded * 100) / e.total));
    },
  });
};

export const getDocuments = () => api.get("/documents");

export default api;
