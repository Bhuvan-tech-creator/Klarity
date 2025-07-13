import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_ENDPOINTS } from '../config/api';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 seconds timeout
      
      const response = await fetch(`${API_ENDPOINTS.GET_HISTORY}?user_id=default_user`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setHistory(data.history || []);
      
    } catch (error) {
      if (error.name === 'AbortError') {
        setError('Request timed out. Please try again.');
      } else {
        setError('Failed to load history. Please try again.');
      }
      console.error('History fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Unknown date';
    }
  };

  const getVideoThumbnail = (videoId) => {
    // Use a clean, consistent watched video thumbnail
    return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200"%3E%3Crect width="300" height="200" fill="%2300ff88"/%3E%3Ctext x="150" y="100" text-anchor="middle" dy=".3em" fill="black" font-size="24" font-weight="bold"%3E📺 WATCHED%3C/text%3E%3C/svg%3E';
  };

  if (loading) {
    return (
      <div className="history-container">
        <div className="history-header">
          <h1 className="page-title-enhanced">📚 Watch History</h1>
          <p className="page-subtitle-enhanced">Your recently watched videos</p>
        </div>
        <div className="history-loading">
          <div className="loading-spinner"></div>
          <p>Loading your watch history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="history-container">
        <div className="history-header">
          <h1 className="page-title-enhanced">📚 Watch History</h1>
          <p className="page-subtitle-enhanced">Your recently watched videos</p>
        </div>
        <div className="history-error">
          <p>{error}</p>
          <button onClick={fetchHistory} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <h1 className="page-title-enhanced">📚 Watch History</h1>
        <p className="page-subtitle-enhanced">Your recently watched videos</p>
      </div>
      
      {history.length === 0 ? (
        <div className="history-empty">
          <div className="empty-state">
            <span className="empty-icon">🎬</span>
            <h3 className="section-title-enhanced">No videos watched yet</h3>
            <p className="page-subtitle-enhanced">Start watching videos to see your history here!</p>
          </div>
        </div>
      ) : (
        <div className="history-grid">
          {history.map((item, index) => (
            <motion.div
              key={`${item.video_id}-${index}`}
              className="history-item"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05 }}
            >
              <div className="history-thumbnail">
                <img 
                  src={getVideoThumbnail(item.video_id)} 
                  alt={item.title}
                  style={{ objectFit: 'cover', width: '100%', height: '100%' }}
                />
                <div className="history-overlay">
                  <div className="history-play-button">
                    <span>▶️</span>
                  </div>
                </div>
              </div>
              
              <div className="history-info">
                <h3 className="history-title-enhanced">{item.title}</h3>
                <p className="history-date-enhanced">{formatDate(item.watched_at)}</p>
                <div className="history-actions">
                  <button 
                    className="history-watch-button"
                    onClick={() => window.open(`https://youtube.com/watch?v=${item.video_id}`, '_blank')}
                  >
                    Watch Again
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History; 