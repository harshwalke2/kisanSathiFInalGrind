import React, { useState, useEffect } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { CheckCircle, TrendingUp, Cloud, Droplets, Zap } from 'lucide-react';
import '../styles/ResultsPage.css';

function ResultsPage() {
  const location = useLocation();
  const [results, setResults] = useState(null);
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [riskData, setRiskData] = useState(null);

  useEffect(() => {
    if (location.state?.results) {
      setResults(location.state.results);
      setSelectedCrop(location.state.results.primary_recommendation);
      fetchRiskData(location.state.results.primary_recommendation);
    }
  }, [location]);

  const fetchRiskData = async (crop) => {
    try {
      const response = await fetch(`http://localhost:5000/api/market-insights/${crop}`);
      const data = await response.json();
      if (data.status === 'success') {
        setRiskData(data);
      }
    } catch (error) {
      console.error('Error fetching risk data:', error);
    }
  };

  const handleCropSelect = (crop) => {
    setSelectedCrop(crop);
    fetchRiskData(crop);
  };

  if (!results) {
    return (
      <div className="results-page section">
        <div className="container">
          <div className="no-results">
            <p>No recommendations found. Please go back and fill the form.</p>
            <Link to="/recommend" className="btn btn-primary">Back to Form</Link>
          </div>
        </div>
      </div>
    );
  }

  const primaryCrop = results.top_recommendations[0];
  return (
    <div className="results-page section">
      <div className="container">
        {/* Success Header */}
        <div className="success-header fade-in">
          <div className="success-icon">
            <CheckCircle size={60} color="#2ecc71" />
          </div>
          <h2>Recommendations Generated!</h2>
          <p>Based on your soil and environmental conditions, here are the best crops to grow</p>
        </div>

        {/* Primary Recommendation Card */}
        <div className="primary-recommendation card fade-in">
          <div className="recommendation-badge">🏆 Top Recommendation</div>
          <div className="recommendation-grid">
            <div className="recommendation-content">
              <h3>{primaryCrop.crop.toUpperCase()}</h3>
              <div className="recommendation-stats">
                <div className="stat-item">
                  <span className="stat-label">Confidence</span>
                  <span className="stat-value confidence-high">{primaryCrop.confidence}%</span>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${primaryCrop.confidence}%` }}></div>
                  </div>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Estimated Yield</span>
                  <span className="stat-value">{primaryCrop.estimated_yield} kg/ha</span>
                </div>
              </div>
            </div>
            <div className="recommendation-action">
              <Link to="/recommend" className="btn btn-secondary">New Analysis</Link>
            </div>
          </div>
        </div>

        <div className="results-grid">
          {/* Alternative Recommendations */}
          <div className="alt-recommendations">
            <h3>Alternative Options</h3>
            <div className="recommendations-list">
              {results.top_recommendations.slice(1).map((rec, idx) => (
                <div 
                  key={idx}
                  className={`recommendation-item ${selectedCrop === rec.crop ? 'active' : ''}`}
                  onClick={() => handleCropSelect(rec.crop)}
                >
                  <div className="item-header">
                    <h4>{rec.crop}</h4>
                    <span className="confidence-badge">{rec.confidence}%</span>
                  </div>
                  <div className="item-details">
                    <span className="yield-info">Est. Yield: {rec.estimated_yield} kg/ha</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Input Conditions Summary */}
          <div className="input-summary card">
            <h3>Your Conditions</h3>
            <div className="conditions-grid">
              <div className="condition-item">
                <span className="condition-icon">N</span>
                <span className="condition-label">Nitrogen</span>
                <span className="condition-value">{results.input_conditions.nitrogen}</span>
              </div>
              <div className="condition-item">
                <span className="condition-icon">P</span>
                <span className="condition-label">Phosphorus</span>
                <span className="condition-value">{results.input_conditions.phosphorus}</span>
              </div>
              <div className="condition-item">
                <span className="condition-icon">K</span>
                <span className="condition-label">Potassium</span>
                <span className="condition-value">{results.input_conditions.potassium}</span>
              </div>
              <div className="condition-item">
                <Cloud size={20} />
                <span className="condition-label">Temp</span>
                <span className="condition-value">{results.input_conditions.temperature}°C</span>
              </div>
              <div className="condition-item">
                <Droplets size={20} />
                <span className="condition-label">Humidity</span>
                <span className="condition-value">{results.input_conditions.humidity}%</span>
              </div>
              <div className="condition-item">
                <span className="condition-icon">pH</span>
                <span className="condition-label">Soil pH</span>
                <span className="condition-value">{results.input_conditions.ph}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Assessment & Market Insights */}
        {riskData && (
          <div className="insights-section">
            <h2>Risk & Market Analysis for {selectedCrop}</h2>
            
            <div className="insights-grid">
              {/* Risk Assessment */}
              <div className="card insight-card">
                <h3>⚠️ Risk Assessment</h3>
                <div className="risk-items">
                  <div className="risk-item">
                    <span className="risk-label">Weather Risk</span>
                    <span className={`risk-badge risk-${riskData.risk_assessment.weather_risk.toLowerCase()}`}>
                      {riskData.risk_assessment.weather_risk}
                    </span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-label">Market Risk</span>
                    <span className={`risk-badge risk-${riskData.risk_assessment.market_risk.toLowerCase()}`}>
                      {riskData.risk_assessment.market_risk}
                    </span>
                  </div>
                  <div className="risk-item">
                    <span className="risk-label">Disease Risk</span>
                    <span className={`risk-badge risk-${riskData.risk_assessment.disease_risk.toLowerCase()}`}>
                      {riskData.risk_assessment.disease_risk}
                    </span>
                  </div>
                  <div className="risk-item overall">
                    <span className="risk-label">Overall Risk</span>
                    <span className={`risk-badge risk-${riskData.risk_assessment.overall_risk.toLowerCase()}`}>
                      {riskData.risk_assessment.overall_risk}
                    </span>
                  </div>
                </div>
              </div>

              {/* Optimal Conditions */}
              <div className="card insight-card">
                <h3>🌱 Optimal Conditions</h3>
                <div className="conditions-items">
                  <div className="condition-range">
                    <span className="range-label">Temperature</span>
                    <span className="range-value">{riskData.optimal_conditions.temperature_range}</span>
                  </div>
                  <div className="condition-range">
                    <span className="range-label">Humidity</span>
                    <span className="range-value">{riskData.optimal_conditions.humidity_range}</span>
                  </div>
                  <div className="condition-range">
                    <span className="range-label">Soil pH</span>
                    <span className="range-value">{riskData.optimal_conditions.ph_range}</span>
                  </div>
                  <div className="condition-range">
                    <span className="range-label">Rainfall</span>
                    <span className="range-value">{riskData.optimal_conditions.rainfall_range}</span>
                  </div>
                </div>
              </div>

              {/* Market Data */}
              <div className="card insight-card">
                <h3>📊 Market Insights</h3>
                <div className="market-items">
                  <div className="market-item">
                    <TrendingUp size={20} />
                    <div>
                      <span className="market-label">Demand Trend</span>
                      <span className="market-value">{riskData.market_data.demand_trend}</span>
                    </div>
                  </div>
                  <div className="market-item">
                    <Zap size={20} />
                    <div>
                      <span className="market-label">Price Stability</span>
                      <span className="market-value">{riskData.market_data.price_stability}</span>
                    </div>
                  </div>
                  {riskData.market_data.latest_price?.value && (
                    <div className="market-item">
                      <span className="market-icon">💰</span>
                      <div>
                        <span className="market-label">Latest Price</span>
                        <span className="market-value">
                          {riskData.market_data.latest_price.value} {riskData.market_data.latest_price.unit}
                        </span>
                      </div>
                    </div>
                  )}
                  {riskData.market_data.forecast_30d?.avg && (
                    <div className="market-item">
                      <span className="market-icon">🧠</span>
                      <div>
                        <span className="market-label">30-day Forecast</span>
                        <span className="market-value">
                          {riskData.market_data.forecast_30d.avg} {riskData.market_data.latest_price?.unit}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
                <p className="market-recommendation">
                  {riskData.market_data.recommendation}
                </p>
              </div>

              {/* Seasonal Info */}
              <div className="card insight-card">
                <h3>📅 Seasonal Information</h3>
                <div className="seasonal-items">
                  <div className="seasonal-item">
                    <span className="seasonal-label">Best Season</span>
                    <span className="seasonal-value">{riskData.seasonal_info.best_season}</span>
                  </div>
                  <div className="seasonal-item">
                    <span className="seasonal-label">Growing Period</span>
                    <span className="seasonal-value">{riskData.seasonal_info.growing_period}</span>
                  </div>
                  <div className="seasonal-item">
                    <span className="seasonal-label">Harvest Time</span>
                    <span className="seasonal-value">{riskData.seasonal_info.harvest_time}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="action-buttons">
          <Link to="/recommend" className="btn btn-primary">
            New Analysis
          </Link>
          <Link to="/market-insights" className="btn btn-secondary">
            Explore More Insights
          </Link>
        </div>
      </div>
    </div>
  );
}

export default ResultsPage;
