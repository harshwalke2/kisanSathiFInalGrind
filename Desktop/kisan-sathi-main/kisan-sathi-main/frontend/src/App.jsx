import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Header from './components/Header';
import Home from './pages/Home';
import RecommendationPage from './pages/RecommendationPage';
import ResultsPage from './pages/ResultsPage';
import MarketInsights from './pages/MarketInsights';
import GlobalMarketAccess from './pages/GlobalMarketAccess';
import Navbar from './components/Navbar';

function App() {
  const [crops, setCrops] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Fetch available crops on app load
    const fetchCrops = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/crops/list');
        const data = await response.json();
        if (data.status === 'success') {
          setCrops(data.crops);
        }
      } catch (error) {
        console.error('Error fetching crops:', error);
      }
    };

    fetchCrops();
  }, []);

  return (
    <Router>
      <div className="App">
        <Navbar />
        <Header />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/recommend" element={<RecommendationPage crops={crops} />} />
          <Route path="/results" element={<ResultsPage />} />
          <Route path="/market-insights" element={<MarketInsights crops={crops} />} />
          <Route path="/global-market" element={<GlobalMarketAccess />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
