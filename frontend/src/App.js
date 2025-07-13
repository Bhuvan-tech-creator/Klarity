import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Navbar from './components/Navbar';
import Home from './components/Home';
import WhatsNext from './components/WhatsNext';
import History from './components/History';
import MovieDetail from './components/MovieDetail';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navbar />
        
        <header className="app-header">
          <div className="header-content">
            <h1 className="app-title">
              <span className="logo-icon">🎯</span>
              Klarity
            </h1>
            <p className="app-subtitle">AI-powered video insights and analysis</p>
          </div>
        </header>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/whats-next" element={<WhatsNext />} />
            <Route path="/history" element={<History />} />
            <Route path="/movie/:movieId" element={<MovieDetail />} />
          </Routes>
        </main>

        <footer className="app-footer">
          <p>Powered by AI • Enhanced video viewing experience</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;