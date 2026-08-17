import axios from "axios";

const fallbackBase = import.meta.env.PROD ? "" : "http://127.0.0.1:8001";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || fallbackBase,
});
