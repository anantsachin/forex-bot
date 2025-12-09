// Configuration for the frontend application

// API URL logic:
// 1. If VITE_API_URL environment variable is set (e.g. in Vercel), use it.
// 2. Otherwise, default to '/api' which works with the local Vite proxy.
// Automatically append /api if VITE_API_URL is set (and doesn't have it), or default to /api
const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
export const API_URL = baseUrl.endsWith('/api') ? baseUrl : `${baseUrl || ''}/api`;
