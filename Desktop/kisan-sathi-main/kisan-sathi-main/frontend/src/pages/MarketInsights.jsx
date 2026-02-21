import React, { useState, useEffect } from 'react';
import { Globe } from 'lucide-react';
import '../styles/MarketInsights.css';

function MarketInsights({ crops = [] }) {
  const [selectedSeason, setSelectedSeason] = useState('rainy');
  const [seasonalCrops, setSeasonalCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [marketData, setMarketData] = useState(null);
  const [loading, setLoading] = useState(false);

  const seasons = [
    { id: 'summer', label: '☀️ Summer', color: '#ff6b6b' },
    { id: 'winter', label: '❄️ Winter', color: '#4ecdc4' },
    { id: 'rainy', label: '🌧️ Rainy', color: '#45b7d1' },
    { id: 'spring', label: '🌸 Spring', color: '#96ceb4' }
  ];

  useEffect(() => {
    fetchSeasonalRecommendations(selectedSeason);
  }, [selectedSeason]);

  const fetchSeasonalRecommendations = async (season) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:5000/api/seasonal-recommendations/${season}`);
      const data = await response.json();
      if (data.status === 'success') {
        setSeasonalCrops(data.recommended_crops);
        setSelectedCrop(data.recommended_crops[0]);
        if (data.recommended_crops[0]) {
          await fetchMarketInsights(data.recommended_crops[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching seasonal recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketInsights = async (crop) => {
    try {
      const response = await fetch(
        `http://localhost:5000/api/market-insights/${crop}?season=${selectedSeason}`
      );
      const data = await response.json();
      if (data.status === 'success') {
        setMarketData(data);
        setSelectedCrop(crop);
      }
    } catch (error) {
      console.error('Error fetching market insights:', error);
    }
  };

  const handleCropSelect = (crop) => {
    fetchMarketInsights(crop);
  };

  return (
    <div className="market-insights-page section">
      <div className="container">
        {/* Page Header */}
        <div className="page-header">
          <h2>Market Insights & Seasonal Guide</h2>
          <p>
            Explore crop recommendations for different seasons and access market insights
            to make informed decisions about what to plant
          </p>
        </div>

        {/* Season Selection */}
        <div className="season-selector">
          <h3>Select Season</h3>
          <div className="season-cards">
            {seasons.map(season => (
              <button
                key={season.id}
                className={`season-card ${selectedSeason === season.id ? 'active' : ''}`}
                onClick={() => setSelectedSeason(season.id)}
                style={{
                  borderColor: selectedSeason === season.id ? season.color : '#ecf0f1',
                  backgroundColor: selectedSeason === season.id ? `${season.color}20` : 'white'
                }}
              >
                <span className="season-label">{season.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="insights-main-grid">
          {/* Seasonal Crops */}
          <div className="seasonal-crops card">
            <h3>Recommended Crops</h3>
            {loading ? (
              <div className="loading-spinner">
                <div className="spinner"></div>
              </div>
            ) : (
              <div className="crops-list">
                {seasonalCrops.length > 0 ? (
                  seasonalCrops.map((crop, idx) => (
                    <button
                      key={idx}
                      className={`crop-item ${selectedCrop === crop ? 'active' : ''}`}
                      onClick={() => handleCropSelect(crop)}
                    >
                      <span className="crop-name">{crop}</span>
                      <span className="crop-arrow">→</span>
                    </button>
                  ))
                ) : (
                  <p className="no-data">No crops available for this season</p>
                )}
              </div>
            )}
          </div>

          {/* Market Data & Details */}
          {marketData && (
            <div className="market-details">
              {/* Market Trends */}
              <div className="card market-trends">
                <h3>📈 Market Trends</h3>
                <div className="trend-items">
                  <div className="trend-item">
                    <span className="trend-icon">📊</span>
                    <div className="trend-content">
                      <span className="trend-label">Demand Trend</span>
                      <span className="trend-value">
                        {marketData.market_data.demand_trend}
                      </span>
                    </div>
                  </div>
                  <div className="trend-item">
                    <span className="trend-icon">💹</span>
                    <div className="trend-content">
                      <span className="trend-label">Price Stability</span>
                      <span className="trend-value">
                        {marketData.market_data.price_stability}
                      </span>
                    </div>
                  </div>
                  <div className="trend-item">
                    <Globe className="trend-icon" size={18} />
                    <div className="trend-content">
                      <span className="trend-label">Global Demand</span>
                      <span className="trend-value">
                        {marketData.market_data.global_demand}
                      </span>
                    </div>
                  </div>
                  {marketData.market_data.latest_price?.value && (
                    <div className="trend-item">
                      <span className="trend-icon">💰</span>
                      <div className="trend-content">
                        <span className="trend-label">Latest Price</span>
                        <span className="trend-value">
                          {marketData.market_data.latest_price.value} {marketData.market_data.latest_price.unit}
                        </span>
                      </div>
                    </div>
                  )}
                  {marketData.market_data.forecast_30d?.avg && (
                    <div className="trend-item">
                      <span className="trend-icon">🧠</span>
                      <div className="trend-content">
                        <span className="trend-label">30-day Forecast</span>
                        <span className="trend-value">
                          {marketData.market_data.forecast_30d.avg} {marketData.market_data.latest_price?.unit}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Risk & Opportunities */}
              <div className="card risk-opportunities">
                <h3>⚠️ Risk Assessment</h3>
                <div className="risk-grid">
                  <div className="risk-item">
                    <span className="risk-type">Weather Risk</span>
                    <span className={`risk-pill risk-${marketData.risk_assessment.weather_risk.toLowerCase()}`}>
                      {marketData.risk_assessment.weather_risk}
                    </span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-type">Market Risk</span>
                    <span className={`risk-pill risk-${marketData.risk_assessment.market_risk.toLowerCase()}`}>
                      {marketData.risk_assessment.market_risk}
                    </span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-type">Disease Risk</span>
                    <span className={`risk-pill risk-${marketData.risk_assessment.disease_risk.toLowerCase()}`}>
                      {marketData.risk_assessment.disease_risk}
                    </span>
                  </div>
                  <div className="risk-item highlight">
                    <span className="risk-type">Overall Risk</span>
                    <span className={`risk-pill risk-${marketData.risk_assessment.overall_risk.toLowerCase()}`}>
                      {marketData.risk_assessment.overall_risk}
                    </span>
                  </div>
                </div>
              </div>

              {/* Optimal Growing Conditions */}
              <div className="card optimal-conditions">
                <h3>🌱 Optimal Growing Conditions</h3>
                <div className="conditions-cards">
                  <div className="condition-box">
                    <span className="condition-name">Temperature</span>
                    <span className="condition-range">
                      {marketData.optimal_conditions.temperature_range}
                    </span>
                  </div>
                  <div className="condition-box">
                    <span className="condition-name">Humidity</span>
                    <span className="condition-range">
                      {marketData.optimal_conditions.humidity_range}
                    </span>
                  </div>
                  <div className="condition-box">
                    <span className="condition-name">Soil pH</span>
                    <span className="condition-range">
                      {marketData.optimal_conditions.ph_range}
                    </span>
                  </div>
                  <div className="condition-box">
                    <span className="condition-name">Rainfall</span>
                    <span className="condition-range">
                      {marketData.optimal_conditions.rainfall_range}
                    </span>
                  </div>
                </div>
              </div>

              {/* Seasonal Timeline */}
              <div className="card seasonal-timeline">
                <h3>📅 Growing Timeline</h3>
                <div className="timeline-items">
                  <div className="timeline-item">
                    <span className="timeline-icon">🌱</span>
                    <div className="timeline-content">
                      <span className="timeline-label">Best Season</span>
                      <span className="timeline-value">
                        {marketData.seasonal_info.best_season}
                      </span>
                    </div>
                  </div>
                  <div className="timeline-item">
                    <span className="timeline-icon">⏱️</span>
                    <div className="timeline-content">
                      <span className="timeline-label">Growing Period</span>
                      <span className="timeline-value">
                        {marketData.seasonal_info.growing_period}
                      </span>
                    </div>
                  </div>
                  <div className="timeline-item">
                    <span className="timeline-icon">🌾</span>
                    <div className="timeline-content">
                      <span className="timeline-label">Harvest Time</span>
                      <span className="timeline-value">
                        {marketData.seasonal_info.harvest_time}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Market Tips Section */}
        <div className="tips-section card">
          <h3>💡 Farmer's Market Tips</h3>
          <ul className="tips-list">
            <li>Monitor weather forecasts closely before and during the growing season</li>
            <li>Check local market prices weekly to time your harvest correctly</li>
            <li>Connect with neighboring farmers to share market insights</li>
            <li>Consider crop diversification to spread risk across multiple crops</li>
            <li>Plan irrigation and fertilization based on seasonal rainfall patterns</li>
            <li>Stay updated with government agricultural bulletins for pest and disease warnings</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default MarketInsights;
