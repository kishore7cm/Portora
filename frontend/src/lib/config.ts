// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'https://portora-backend-a1d0.onrender.com';

export const config = {
  apiUrl: API_BASE_URL,
  endpoints: {
    portfolio: `${API_BASE_URL}/portfolio`,
    sp500: `${API_BASE_URL}/sp500`,
    historical: `${API_BASE_URL}/historical-data`,
    health: `${API_BASE_URL}/portfolio-health`,
    comparison: `${API_BASE_URL}/comparison`,
    community: `${API_BASE_URL}/community/comparison`,
    bots: `${API_BASE_URL}/bots`,
    alerts: `${API_BASE_URL}/alerts`,
    onboarding: `${API_BASE_URL}/onboarding/status`,
    auth: `${API_BASE_URL}/auth`
  }
};
