import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { API_ENDPOINTS } from '../config/api';

const MovieDetail = () => {
  const { movieId } = useParams();
  const navigate = useNavigate();
  const [movie, setMovie] = useState(null);
  const [genre, setGenre] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMovieDetails();
  }, [movieId]);

  const fetchMovieDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`${API_ENDPOINTS.GET_MOVIE_DETAILS}/${movieId}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch movie details');
      }

      const data = await response.json();
      setMovie(data.movie);
      setGenre(data.genre);
      
    } catch (error) {
      setError('Failed to load movie details. Please try again.');
      console.error('Movie details fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const getGenreColor = (genre) => {
    const colors = {
      action: '#ff3366',
      comedy: '#ff9500',
      thriller: '#0066ff',
      horror: '#800080'
    };
    return colors[genre] || '#333';
  };

  const getGenreEmoji = (genre) => {
    const emojis = {
      action: '💥',
      comedy: '😂',
      thriller: '🔪',
      horror: '👻'
    };
    return emojis[genre] || '🎬';
  };

  if (loading) {
    return (
      <div className="movie-detail-container">
        <div className="movie-detail-loading">
          <div className="loading-spinner"></div>
          <p>Loading movie details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="movie-detail-container">
        <div className="movie-detail-error">
          <p>{error}</p>
          <button onClick={() => navigate('/whats-next')} className="back-button">
            Back to Movies
          </button>
        </div>
      </div>
    );
  }

  if (!movie) {
    return (
      <div className="movie-detail-container">
        <div className="movie-detail-error">
          <p>Movie not found</p>
          <button onClick={() => navigate('/whats-next')} className="back-button">
            Back to Movies
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className="movie-detail-container"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <div className="movie-detail-header">
        <button onClick={() => navigate('/whats-next')} className="back-button-enhanced">
          ← Back to Movies
        </button>
      </div>

      <div className="movie-detail-content">
        <div className="movie-poster-section">
          <motion.div 
            className="movie-poster-container"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <img 
              src={movie.thumbnail} 
              alt={movie.title}
              className="movie-poster-large"
            />
            <div className="movie-genre-badge" style={{ backgroundColor: getGenreColor(genre) }}>
              <span className="genre-emoji">{getGenreEmoji(genre)}</span>
              <span className="genre-text">{genre.toUpperCase()}</span>
            </div>
          </motion.div>
        </div>

        <div className="movie-info-section">
          <motion.div 
            className="movie-info-content"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <h1 className="movie-title-large">{movie.title}</h1>
            
            <div className="movie-meta">
              <span className="movie-genre-tag" style={{ color: getGenreColor(genre) }}>
                {getGenreEmoji(genre)} {genre.charAt(0).toUpperCase() + genre.slice(1)}
              </span>
            </div>

            <div className="movie-summary-section">
              <h2 className="summary-title">Plot Summary</h2>
              <p className="movie-summary-text">{movie.summary}</p>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.div>
  );
};

export default MovieDetail; 