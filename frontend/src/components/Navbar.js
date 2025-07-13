import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

const Navbar = () => {
  const location = useLocation();
  
  return (
    <nav className="navbar">
      <div className="navbar-content">
        <Link to="/" className="navbar-logo">
          <span className="logo-icon">🎯</span>
          <span className="logo-text">Klarity</span>
        </Link>
        
        <div className="navbar-links">
          <Link to="/" className={`navbar-link ${location.pathname === '/' ? 'active' : ''}`}>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="navbar-link-content"
            >
              <span className="navbar-icon">🏠</span>
              <span>Home</span>
            </motion.div>
          </Link>
          
          <Link to="/whats-next" className={`navbar-link ${location.pathname === '/whats-next' ? 'active' : ''}`}>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="navbar-link-content"
            >
              <span className="navbar-icon">🎬</span>
              <span>What's Next</span>
            </motion.div>
          </Link>
          
          <Link to="/history" className={`navbar-link ${location.pathname === '/history' ? 'active' : ''}`}>
            <motion.div
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="navbar-link-content"
            >
              <span className="navbar-icon">📚</span>
              <span>History</span>
            </motion.div>
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 