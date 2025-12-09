// Configuration for the frontend application

// API URL logic:
// 1. If VITE_API_URL environment variable is set (e.g. in Vercel), use it.
// 2. Otherwise, default to '/api' which works with the local Vite proxy.
export const API_URL = import.meta.env.VITE_API_URL || '/api';
