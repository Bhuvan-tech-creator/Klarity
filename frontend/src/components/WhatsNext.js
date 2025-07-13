import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const WhatsNext = () => {
  const navigate = useNavigate();
  const [userStats, setUserStats] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [genreMovies, setGenreMovies] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      setLoading(true);
      setError(null); // Clear any previous errors
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 seconds timeout
      
      const response = await fetch('http://localhost:5000/get_recommendations?user_id=default_user', {
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
      setUserStats({ complexity_score: data.complexity_score });
      setRecommendations(data.recommendations);
      setGenreMovies(data.genres);
      
    } catch (error) {
      if (error.name === 'AbortError') {
        setError('Request timed out. Please try again.');
      } else {
        setError('Failed to load recommendations. Please try again.');
      }
      console.error('Recommendations fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMovieThumbnail = (movie) => {
    // ALWAYS use real movie images from TMDB - NO FALLBACKS ALLOWED
    return movie.thumbnail;
  };

  const getComplexityLevel = (score) => {
    // Simpler, more intuitive complexity levels
    if (score >= 4.0) return { level: 'Expert', color: '#ff3366', emoji: '🔥', description: 'Advanced storytelling' };
    if (score >= 3.0) return { level: 'Advanced', color: '#ff6600', emoji: '⚡', description: 'Complex narratives' };
    if (score >= 2.0) return { level: 'Intermediate', color: '#ffcc00', emoji: '🎯', description: 'Moderate complexity' };
    return { level: 'Beginner', color: '#00ff88', emoji: '🌱', description: 'Simple & engaging' };
  };

  const handleMovieClick = (movie) => {
    navigate(`/movie/${movie.id}`);
  };

  const renderMovieCard = (movie, index, isRecommended = false) => (
    <motion.div
      key={`${movie.id}-${index}`}
      className="netflix-movie-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      whileHover={{ scale: 1.05 }}
      onClick={() => handleMovieClick(movie)}
      style={{ cursor: 'pointer' }}
    >
      <div className="netflix-movie-thumbnail">
        <img 
          src={getMovieThumbnail(movie)} 
          alt={movie.title}
          style={{ objectFit: 'cover', width: '100%', height: '100%' }}
        />
        <div className="netflix-movie-overlay">
          <div className="netflix-movie-title">{movie.title}</div>
          {isRecommended && (
            <div className="netflix-recommended-badge">
              <span>✨ Recommended</span>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );

  const renderGenreSection = (genre, movies) => {
    const genreEmojis = {
      action: '💥',
      comedy: '😂',
      thriller: '🔪',
      horror: '👻'
    };

    return (
      <div key={genre} className="netflix-genre-section">
        <h3 className="netflix-genre-title">
          <span className="netflix-genre-emoji">{genreEmojis[genre]}</span>
          {genre.charAt(0).toUpperCase() + genre.slice(1)} Movies
        </h3>
        <div className="netflix-movies-grid">
          {movies.map((movie, index) => renderMovieCard(movie, index))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="whats-next-container">
        <div className="whats-next-header">
          <h1 className="page-title-enhanced">🎬 What's Next</h1>
          <p className="page-subtitle-enhanced">Personalized movie recommendations based on your complexity level</p>
        </div>
        <div className="whats-next-loading">
          <div className="loading-spinner"></div>
          <p>Loading your personalized recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="whats-next-container">
        <div className="whats-next-header">
          <h1 className="page-title-enhanced">🎬 What's Next</h1>
          <p className="page-subtitle-enhanced">Personalized movie recommendations based on your complexity level</p>
        </div>
        <div className="whats-next-error">
          <p>{error}</p>
          <button onClick={fetchUserData} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const complexityInfo = getComplexityLevel(userStats?.complexity_score || 1.0);

  return (
    <div className="whats-next-container">
      <div className="whats-next-header">
        <h1 className="page-title-enhanced">🎬 What's Next</h1>
        <p className="page-subtitle-enhanced">Personalized movie recommendations based on your complexity level</p>
      </div>

      {/* Enhanced Complexity Score Section */}
      <div className="complexity-section">
        <div className="complexity-card-enhanced">
          <h2 className="section-title-enhanced">Your Complexity Level</h2>
          <div className="complexity-display-enhanced">
            <div className="complexity-visual">
              <div className="complexity-circle" style={{ borderColor: complexityInfo.color }}>
                <span className="complexity-emoji-large">{complexityInfo.emoji}</span>
              </div>
              <div className="complexity-level-info">
                <span className="complexity-level-name" style={{ color: complexityInfo.color }}>
                  {complexityInfo.level}
                </span>
                <span className="complexity-description">
                  {complexityInfo.description}
                </span>
                <span className="complexity-score-display">
                  {(userStats?.complexity_score || 1.0).toFixed(1)}/5.0
                </span>
              </div>
            </div>
            
            {/* Enhanced Progress Bar with Labels */}
            <div className="complexity-progress-section">
              <div className="complexity-progress-bar">
                <div 
                  className="complexity-progress-fill"
                  style={{ 
                    width: `${(userStats?.complexity_score || 1.0) * 20}%`,
                    backgroundColor: complexityInfo.color
                  }}
                />
              </div>
              <div className="complexity-labels">
                <div className="complexity-label">
                  <span className="label-emoji">🌱</span>
                  <span className="label-text">Beginner</span>
                </div>
                <div className="complexity-label">
                  <span className="label-emoji">🎯</span>
                  <span className="label-text">Intermediate</span>
                </div>
                <div className="complexity-label">
                  <span className="label-emoji">⚡</span>
                  <span className="label-text">Advanced</span>
                </div>
                <div className="complexity-label">
                  <span className="label-emoji">🔥</span>
                  <span className="label-text">Expert</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Personalized Recommendations */}
      {recommendations && (
        <div className="recommendations-section">
          <h2 className="section-title-enhanced">✨ Recommended For You</h2>
          <div className="netflix-recommended-movies">
            {Object.entries(recommendations).map(([genre, movie], index) => (
              <div key={genre} className="netflix-recommended-item">
                <h3 className="netflix-recommended-genre-enhanced">
                  {genre.charAt(0).toUpperCase() + genre.slice(1)}
                </h3>
                {renderMovieCard(movie, index, true)}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Browse by Genre */}
      {genreMovies && (
        <div className="browse-section">
          <h2 className="section-title-enhanced">🎭 Browse by Genre</h2>
          <div className="netflix-browse-container">
            {Object.entries(genreMovies).map(([genre, movies]) => 
              renderGenreSection(genre, movies)
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatsNext; 