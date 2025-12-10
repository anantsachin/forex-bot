// Configuration for the frontend application
// Forcing Hugging Face Backend to bypass Vercel Env Var issues
// let apiUrl = import.meta.env.VITE_API_URL || '';
let apiUrl = 'https://anantwdev-forexbot.hf.space/api';

// Normalize: remove quotes, trim spaces, remove trailing slash
apiUrl = apiUrl.replace(/['"]/g, '').trim().replace(/\/$/, '');

// If env var is set, ensure it ends with /api (Double check for manually entered strings)
if (apiUrl && !apiUrl.endsWith('/api')) {
    apiUrl += '/api';
}

// Debug log to help verify correct configuration in production
console.log('🔌 API Configuration (FORCED):', {
    resolved: apiUrl
});

export const API_URL = apiUrl;
