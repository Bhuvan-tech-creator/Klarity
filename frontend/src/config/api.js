// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  PROCESS_VIDEO: `${API_BASE_URL}/process_video`,
  GET_HISTORY: `${API_BASE_URL}/get_history`,
  GET_RECOMMENDATIONS: `${API_BASE_URL}/get_recommendations`,
  GET_MOVIE_DETAILS: `${API_BASE_URL}/get_movie_details`,
  UPDATE_CLICKS: `${API_BASE_URL}/update_clicks`,
  WHAT_HAPPENED: `${API_BASE_URL}/what_happened`,
  DIAGNOSE: `${API_BASE_URL}/diagnose`
};

export default API_BASE_URL; 