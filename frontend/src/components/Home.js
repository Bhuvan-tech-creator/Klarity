import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { API_ENDPOINTS } from '../config/api';

// Extract YouTube video ID from URL
const getYouTubeVideoId = (url) => {
  const regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
  const match = url.match(regExp);
  return (match && match[7].length === 11) ? match[7] : null;
};

// YouTube Player Component using YouTube IFrame API
const YouTubePlayer = ({ videoId, onProgress, onError, onReady }) => {
  const iframeRef = useRef(null);
  const playerRef = useRef(null);
  const intervalRef = useRef(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!videoId) return;

    const initializePlayer = () => {
      if (iframeRef.current && !playerRef.current) {
        try {
          playerRef.current = new window.YT.Player(iframeRef.current, {
            videoId: videoId,
            width: '100%',
            height: '540',
            playerVars: {
              controls: 1,
              modestbranding: 1,
              rel: 0,
              showinfo: 1,
              autoplay: 0,
              mute: 0
            },
            events: {
              onReady: () => {
                console.log('YouTube player ready');
                setIsReady(true);
                onReady?.();
                intervalRef.current = setInterval(() => {
                  if (playerRef.current && playerRef.current.getCurrentTime) {
                    try {
                      const currentTime = playerRef.current.getCurrentTime();
                      onProgress({ playedSeconds: currentTime });
                    } catch (error) {
                      console.warn('Error getting current time:', error);
                    }
                  }
                }, 1000);
              },
              onError: (error) => {
                console.error('YouTube Player Error:', error);
                onError?.(error);
              },
              onStateChange: (event) => {
                console.log('Player state changed:', event.data);
              }
            }
          });
        } catch (error) {
          console.error('Failed to initialize YouTube player:', error);
          onError?.(error);
        }
      }
    };

    if (!window.YT) {
      const script = document.createElement('script');
      script.src = 'https://www.youtube.com/iframe_api';
      script.async = true;
      document.head.appendChild(script);
      window.onYouTubeIframeAPIReady = initializePlayer;
    } else {
      initializePlayer();
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      if (playerRef.current && playerRef.current.destroy) {
        try {
          playerRef.current.destroy();
        } catch (error) {
          console.warn('Error destroying YouTube player:', error);
        }
        playerRef.current = null;
      }
      setIsReady(false);
    };
  }, [videoId]);

  if (!videoId) {
    return (
      <div className="video-fallback">
        <div className="fallback-content">
          <div className="fallback-icon">📺</div>
          <p>Please enter a valid YouTube URL</p>
          <small>Supported formats: youtube.com/watch?v=... or youtu.be/...</small>
        </div>
      </div>
    );
  }

  return (
    <div className="youtube-player">
      <div ref={iframeRef} />
      {!isReady && (
        <div className="video-loading">
          <div className="loading-spinner"></div>
          <p>Loading video player...</p>
        </div>
      )}
    </div>
  );
};

// Simple Video Player Component (YouTube only for now)
const VideoPlayer = ({ url, onProgress, onError, onReady }) => {
  const videoId = getYouTubeVideoId(url);
  
  if (!videoId) {
    return (
      <div className="video-fallback">
        <div className="fallback-content">
          <div className="fallback-icon">⚠️</div>
          <p>Please enter a valid YouTube URL</p>
          <small>Supported formats: youtube.com/watch?v=... or youtu.be/...</small>
        </div>
      </div>
    );
  }

  return (
    <YouTubePlayer
      videoId={videoId}
      onProgress={onProgress}
      onError={onError}
      onReady={onReady}
    />
  );
};

// Loading Component
const LoadingMessage = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -20 }}
    className="loading-message"
  >
    <div className="loading-content">
      <div className="loading-spinner large"></div>
      <h3>🤖 Processing your video...</h3>
      <p>Our AI is analyzing the content to create insights and briefings. This may take a moment.</p>
      <div className="loading-steps">
        <div className="step">📹 Extracting transcript</div>
        <div className="step">🧠 Analyzing content</div>
        <div className="step">✨ Generating insights</div>
      </div>
    </div>
  </motion.div>
);

const Home = () => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [videoData, setVideoData] = useState(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [showRecap, setShowRecap] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [clickCount, setClickCount] = useState(0);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const handleFullscreenChange = () => {
      const isCurrentlyFullscreen = !!(
        document.fullscreenElement ||
        document.webkitFullscreenElement ||
        document.mozFullScreenElement ||
        document.msFullscreenElement
      );
      console.log('Fullscreen state changed:', isCurrentlyFullscreen);
      setIsFullscreen(isCurrentlyFullscreen);
      if (isCurrentlyFullscreen) {
        setTimeout(() => {
          const alerts = document.querySelectorAll('.alert');
          const buttons = document.querySelectorAll('.recap-button');
          const popups = document.querySelectorAll('.recap');
          alerts.forEach(alert => {
            alert.style.position = 'fixed';
            alert.style.zIndex = '2147483647';
          });
          buttons.forEach(button => {
            button.style.position = 'fixed';
            button.style.zIndex = '2147483647';
          });
          popups.forEach(popup => {
            popup.style.position = 'fixed';
            popup.style.zIndex = '2147483647';
          });
        }, 100);
      }
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('MSFullscreenChange', handleFullscreenChange);
    window.addEventListener('resize', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('MSFullscreenChange', handleFullscreenChange);
      window.removeEventListener('resize', handleFullscreenChange);
    };
  }, []);

  const fetchHistory = async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      
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
      setShowHistory(true);
      
    } catch (error) {
      console.error('History fetch error:', error);
      // Don't show error to user for this, it's not critical
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!youtubeUrl.trim()) return;
    
    console.log('Submitting URL:', youtubeUrl);
    setIsLoading(true);
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout
      
      const response = await fetch(API_ENDPOINTS.PROCESS_VIDEO, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          youtube_url: youtubeUrl,
          user_id: 'default_user'
        }),
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Backend response:', data);
      
      if (data.error) {
        alert(data.error);
      } else {
        setVideoData(data);
        setClickCount(0); // Reset click count for new video
        // Fetch history after successful video analysis
        fetchHistory();
      }
    } catch (error) {
      console.error('Backend error:', error);
      if (error.name === 'AbortError') {
        alert('Request timed out. Please try again.');
      } else if (error.message.includes('Failed to fetch')) {
        alert('Cannot connect to server. Please ensure the backend is running.');
      } else {
        alert('Error connecting to backend: ' + error.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleProgress = ({ playedSeconds }) => {
    console.log('Video time:', Math.floor(playedSeconds));
    setCurrentTime(Math.floor(playedSeconds));
  };

  const handleError = (error) => {
    console.error('Video playback error:', error);
  };

  const handleReady = () => {
    console.log('Video player is ready');
  };

  const handleRecapClick = async () => {
    const newClickCount = clickCount + 1;
    setClickCount(newClickCount);
    setShowRecap(true);
    
    // Send click data to backend to update complexity score
    try {
      const response = await fetch(API_ENDPOINTS.UPDATE_CLICKS, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          user_id: 'default_user',
          clicks: newClickCount
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('Updated complexity score:', data.complexity_score);
      }
    } catch (error) {
      console.error('Error updating click count:', error);
      // Don't show error to user for this, it's not critical
    }
  };

  const getCurrentRecap = () => {
    if (!videoData || !videoData.recaps) return null;
    return videoData.recaps.find(
      (recap) =>
        currentTime >= recap.timestamp_start && currentTime < recap.timestamp_end
    );
  };

  const getFullscreenStyle = (baseStyle = {}) => {
    if (isFullscreen) {
      return {
        ...baseStyle,
        position: 'fixed !important',
        zIndex: 2147483647,
        top: baseStyle.top || '20px',
        right: baseStyle.right || '20px',
        bottom: baseStyle.bottom,
        left: baseStyle.left,
      };
    }
    return baseStyle;
  };

  const renderRatingStars = (rating) => {
    if (!rating) return '';
    const stars = Math.round(parseFloat(rating) || 0);
    return '★'.repeat(stars) + '☆'.repeat(5 - stars);
  };

  return (
    <div className="home-container">
      {isFullscreen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          pointerEvents: 'none',
          zIndex: 2147483647
        }}>
          {videoData && videoData.theme_alerts && videoData.theme_alerts.map(
            (alert) =>
              currentTime >= alert.timestamp &&
              currentTime < alert.timestamp + 10 && (
                <motion.div
                  key={`fullscreen-alert-${alert.timestamp}`}
                  initial={{ opacity: 0, transform: 'translateY(20px)' }}
                  animate={{ opacity: 1, transform: 'translateY(0)' }}
                  exit={{ opacity: 0, transform: 'translateY(-20px)' }}
                  style={{
                    position: 'fixed',
                    top: '20px',
                    right: '20px',
                    zIndex: 2147483647,
                    pointerEvents: 'all',
                    background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.98) 0%, rgba(5, 150, 105, 0.98) 50%, rgba(59, 130, 246, 0.95) 100%)',
                    backdropFilter: 'blur(20px)',
                    color: 'white',
                    padding: '1.5rem',
                    borderRadius: '20px',
                    boxShadow: '0 10px 40px rgba(16, 185, 129, 0.4)',
                    maxWidth: '320px',
                    border: '1px solid rgba(255, 255, 255, 0.3)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', fontWeight: 600 }}>
                    <span style={{ fontSize: '1.2rem' }}>🎭</span>
                    <strong>{alert.theme}</strong>
                    <span style={{ opacity: 0.9, fontStyle: 'italic', fontWeight: 400 }}>({alert.emotion})</span>
                  </div>
                  <p style={{ fontSize: '0.95rem', lineHeight: '1.5', margin: 0, opacity: 0.95 }}>{alert.description}</p>
                </motion.div>
              )
          )}
          <button
            onClick={handleRecapClick}
            style={{
              position: 'fixed',
              bottom: '20px',
              right: '20px',
              zIndex: 2147483647,
              pointerEvents: 'all',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 50%, #0369a1 100%)',
              color: 'white',
              padding: '1rem 1.5rem',
              border: 'none',
              borderRadius: '50px',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '1rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              boxShadow: '0 8px 30px rgba(16, 185, 129, 0.4)',
              transition: 'all 0.4s ease',
              backdropFilter: 'blur(15px)',
              border: '1px solid rgba(255, 255, 255, 0.3)'
            }}
            title="Get a recap of what just happened"
          >
            <span>🤔</span>
            What Just Happened?
          </button>
          {showRecap && getCurrentRecap() && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              style={{
                position: 'fixed',
                bottom: '100px',
                right: '20px',
                zIndex: 2147483647,
                pointerEvents: 'all',
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.98) 0%, rgba(240, 253, 244, 0.98) 100%)',
                backdropFilter: 'blur(25px)',
                padding: '2rem',
                borderRadius: '25px',
                boxShadow: '0 15px 60px rgba(16, 185, 129, 0.3)',
                maxWidth: '400px',
                border: '1px solid rgba(34, 197, 94, 0.3)',
                color: '#1a3b2e'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  📝 Quick Recap
                </h3>
                <button
                  onClick={() => setShowRecap(false)}
                  style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    color: '#ef4444',
                    border: 'none',
                    borderRadius: '50%',
                    width: '32px',
                    height: '32px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '1.2rem'
                  }}
                  title="Close recap"
                >
                  ✕
                </button>
              </div>
              <p style={{ fontSize: '1.05rem', lineHeight: '1.6', marginBottom: '1rem', color: '#2d5f4a' }}>
                {getCurrentRecap().summary}
              </p>
              <div style={{
                background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(59, 130, 246, 0.05) 100%)',
                padding: '0.5rem 1rem',
                borderRadius: '15px',
                textAlign: 'center',
                border: '1px solid rgba(34, 197, 94, 0.2)'
              }}>
                <small style={{ color: '#10b981', fontWeight: 500 }}>
                  {Math.floor(getCurrentRecap().timestamp_start / 60)}:
                  {String(getCurrentRecap().timestamp_start % 60).padStart(2, '0')} - 
                  {Math.floor(getCurrentRecap().timestamp_end / 60)}:
                  {String(getCurrentRecap().timestamp_end % 60).padStart(2, '0')}
                </small>
              </div>
            </motion.div>
          )}
        </div>
      )}

      <section className="input-section">
        <div className="form-container">
          <form onSubmit={handleSubmit} className="url-form">
            <div className="input-group">
              <input
                type="text"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="Paste your YouTube URL here..."
                className="url-input"
                disabled={isLoading}
              />
              <button 
                type="submit" 
                className="submit-button"
                disabled={isLoading || !youtubeUrl.trim()}
              >
                {isLoading ? (
                  <>
                    <div className="loading-spinner small"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    <span>🚀</span>
                    Analyze Video
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </section>

      <AnimatePresence>
        {isLoading && <LoadingMessage />}
      </AnimatePresence>

      <AnimatePresence>
        {videoData && (videoData.briefing || (videoData.characters && videoData.characters.length > 0)) && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            className="insights-container"
          >
            <div className="insights-row">
              {/* Pre-watch Briefing Section */}
              {videoData.briefing && (
                <motion.section
                  initial={{ opacity: 0, x: -30 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className="briefing-section-side"
                >
                  <div className="briefing">
                    <div className="section-header">
                      <h2 className="section-title-enhanced">📋 Pre-watch Briefing</h2>
                      <span className="section-badge">AI Generated</span>
                    </div>
                    <p className="briefing-text-enhanced">{videoData.briefing}</p>
                    {videoData.rating && (
                      <div style={{ marginTop: '1rem', color: '#2d5f4a' }}>
                        <strong>Rating:</strong> {renderRatingStars(videoData.rating)} ({videoData.rating}/5)
                      </div>
                    )}
                    {videoData.complexity && (
                      <div style={{ marginTop: '0.5rem', color: '#2d5f4a' }}>
                        <strong>Complexity:</strong> {videoData.complexity}
                      </div>
                    )}
                  </div>
                </motion.section>
              )}

              {/* Character Chart Section */}
              {videoData.characters && videoData.characters.length > 0 && (
                <motion.section
                  initial={{ opacity: 0, x: 30 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="character-chart-section-side"
                >
                  <div className="character-chart">
                    <div className="section-header">
                      <h2 className="section-title-enhanced">🎭 Character Chart</h2>
                      <span className="section-badge">AI Generated</span>
                    </div>
                    <div className="character-table-container">
                      <table className="character-table">
                        <thead>
                          <tr>
                            <th>Character Name</th>
                            <th>Role</th>
                            <th>Description</th>
                          </tr>
                        </thead>
                        <tbody>
                          {videoData.characters
                            .sort((a, b) => (a.importance || 1) - (b.importance || 1))
                            .map((character, index) => (
                              <tr key={index} className={`character-row importance-${character.importance || 1}`}>
                                <td className="character-name">
                                  <div className="character-name-cell">
                                    <span className="importance-indicator">
                                      {character.importance === 1 ? '⭐' : character.importance === 2 ? '✨' : '💫'}
                                    </span>
                                    {character.name}
                                  </div>
                                </td>
                                <td className="character-role">{character.role}</td>
                                <td className="character-description">{character.description}</td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                    <div className="character-chart-legend">
                      <small>
                        ⭐ Main Character • ✨ Supporting Character • 💫 Minor Character
                      </small>
                    </div>
                  </div>
                </motion.section>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {youtubeUrl && !isLoading && (
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ delay: 0.3 }}
            className="video-section"
          >
            <div className="video-container">
              <VideoPlayer
                url={youtubeUrl}
                onProgress={handleProgress}
                onError={handleError}
                onReady={handleReady}
              />

              <div className="video-overlays">
                <AnimatePresence>
                  {videoData &&
                    videoData.theme_alerts &&
                    videoData.theme_alerts.map(
                      (alert) =>
                        currentTime >= alert.timestamp &&
                        currentTime < alert.timestamp + 10 && (
                          <motion.div
                            key={alert.timestamp}
                            initial={{ opacity: 0, transform: 'translateY(20px)' }}
                            animate={{ opacity: 1, transform: 'translateY(0)' }}
                            exit={{ opacity: 0, transform: 'translateY(-20px)' }}
                            className={`alert ${isFullscreen ? 'fullscreen-active' : ''}`}
                            style={getFullscreenStyle({
                              top: '20px',
                              right: '20px',
                              position: isFullscreen ? 'fixed' : 'absolute',
                              zIndex: isFullscreen ? 2147483647 : 'auto'
                            })}
                          >
                            <div className="alert-header">
                              <span className="alert-emoji">🎭</span>
                              <strong>{alert.theme}</strong>
                              <span className="alert-emotion">({alert.emotion})</span>
                            </div>
                            <p>{alert.description}</p>
                          </motion.div>
                        )
                    )}
                </AnimatePresence>

                <AnimatePresence>
                  {videoData && getCurrentRecap() && (
                    <motion.button
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 0.8 }}
                      className={`recap-button ${isFullscreen ? 'fullscreen-active' : ''}`}
                      onClick={handleRecapClick}
                      style={getFullscreenStyle({
                        bottom: '20px',
                        right: '20px',
                        position: isFullscreen ? 'fixed' : 'absolute',
                        zIndex: isFullscreen ? 2147483647 : 'auto'
                      })}
                    >
                      💡 Need a recap?
                    </motion.button>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showRecap && videoData && getCurrentRecap() && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`recap ${isFullscreen ? 'fullscreen-active' : ''}`}
            style={getFullscreenStyle({
              bottom: '80px',
              right: '20px',
              position: isFullscreen ? 'fixed' : 'absolute',
              zIndex: isFullscreen ? 2147483647 : 'auto'
            })}
          >
            <div className="recap-header">
              <h3>📝 Quick Recap</h3>
              <button
                className="close-button"
                onClick={() => setShowRecap(false)}
              >
                ×
              </button>
            </div>
            <p>{getCurrentRecap().recap}</p>
            <div className="recap-timestamp">
              <small>
                Timestamp: {Math.floor(getCurrentRecap().timestamp_start / 60)}:
                {(getCurrentRecap().timestamp_start % 60).toString().padStart(2, '0')} - 
                {Math.floor(getCurrentRecap().timestamp_end / 60)}:
                {(getCurrentRecap().timestamp_end % 60).toString().padStart(2, '0')}
              </small>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showHistory && history.length > 0 && !isLoading && (
          <motion.section
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            className="history-section"
          >
            <div className="section-header">
              <h2 className="section-title-enhanced">📚 Your Watch History</h2>
              <span className="section-badge">Recent Videos</span>
            </div>
            <div className="history-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
              {history.slice(0, 6).map((item, index) => (
                <motion.div
                  key={`${item.video_id}-${index}`}
                  className="history-item"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  style={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(10px)',
                    borderRadius: '12px',
                    padding: '1rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div className="history-info">
                    <h3 className="history-title-enhanced" style={{ 
                      color: '#ffffff', 
                      fontSize: '1.1rem', 
                      fontWeight: '600', 
                      marginBottom: '0.5rem',
                      lineHeight: '1.3'
                    }}>
                      {item.title}
                    </h3>
                    <p className="history-date-enhanced" style={{ 
                      color: '#cbd5e1', 
                      fontSize: '0.9rem',
                      marginBottom: '0.75rem'
                    }}>
                      {formatDate(item.watched_at)}
                    </p>
                    <div className="history-actions">
                      <button 
                        className="history-watch-button"
                        onClick={() => window.open(`https://youtube.com/watch?v=${item.video_id}`, '_blank')}
                        style={{
                          background: 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
                          color: 'white',
                          border: 'none',
                          borderRadius: '8px',
                          padding: '0.5rem 1rem',
                          fontSize: '0.9rem',
                          fontWeight: '600',
                          cursor: 'pointer',
                          transition: 'all 0.3s ease',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}
                      >
                        <span>▶️</span>
                        Watch Again
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {isFullscreen && (
        <div style={{
          position: 'fixed',
          top: '10px',
          left: '10px',
          background: 'rgba(0,0,0,0.8)',
          color: 'white',
          padding: '10px',
          borderRadius: '5px',
          fontSize: '12px',
          zIndex: 2147483647
        }}>
          🎬 Fullscreen Mode Active
        </div>
      )}
    </div>
  );
};

export default Home; 