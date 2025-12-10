// Configuration for the frontend application
let apiUrl = import.meta.env.VITE_API_URL || '';

// Normalize: remove quotes, trim spaces, remove trailing slash
apiUrl = apiUrl.replace(/['"]/g, '').trim().replace(/\/$/, '');

// If env var is set, ensure it ends with /api
if (apiUrl && !apiUrl.endsWith('/api')) {
    apiUrl += '/api';
}

// Default to the Live Hugging Face Backend if no environment variable is set
if (!apiUrl) {
    apiUrl = 'https://anantwdev-forexbot.hf.space/api';
    console.log('Using Default Hugging Face Backend');
}

// Debug log to help verify correct configuration in production
console.log('🔌 API Configuration:', {
    raw: import.meta.env.VITE_API_URL,
    resolved: apiUrl
});

export const API_URL = apiUrl;
