import React, { useState, useEffect } from 'react';
import { Globe, TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react';
import '../styles/GlobalMarketAccess.css';

function GlobalMarketAccess() {
  const [crops, setCrops] = useState([]);
  const [marketData, setMarketData] = useState({});
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [loading, setLoading] = useState(false);
  const [filterTrend, setFilterTrend] = useState('all'); // all, increasing, decreasing, stable
  const [sortBy, setSortBy] = useState('name'); // name, demand, price

  useEffect(() => {
    fetchCrops();
  }, []);

  const fetchCrops = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/crops/list');
      const data = await response.json();
      if (data.status === 'success') {
        setCrops(data.crops);
        // Fetch market data for all crops
        fetchAllMarketData(data.crops);
      }
    } catch (error) {
      console.error('Error fetching crops:', error);
    }
  };

  const fetchAllMarketData = async (cropList) => {
    setLoading(true);
    const allMarketData = {};
    
    for (const crop of cropList) {
      try {
        const response = await fetch(`http://localhost:5000/api/market-insights/${crop}`);
        const data = await response.json();
        if (data.status === 'success') {
          allMarketData[crop] = data;
        }
      } catch (error) {
        console.error(`Error fetching market data for ${crop}:`, error);
        allMarketData[crop] = null;
      }
    }
    
    setMarketData(allMarketData);
    setLoading(false);
  };

  const getFilteredAndSortedCrops = () => {
    let filtered = crops.filter(crop => {
      const data = marketData[crop];
      if (!data) return false;
      
      if (filterTrend === 'all') return true;
      return data.market_data?.global_demand === filterTrend || 
             data.market_data?.demand_trend === filterTrend;
    });

    return filtered.sort((a, b) => {
      if (sortBy === 'name') {
        return a.localeCompare(b);
      } else if (sortBy === 'demand') {
        const demandA = marketData[a]?.market_data?.demand_trend || 'moderate';
        const demandB = marketData[b]?.market_data?.demand_trend || 'moderate';
        const demandOrder = { 'high': 3, 'moderate': 2, 'low': 1 };
        return (demandOrder[demandB] || 0) - (demandOrder[demandA] || 0);
      } else if (sortBy === 'price') {
        const priceA = marketData[a]?.market_data?.latest_price?.value || 0;
        const priceB = marketData[b]?.market_data?.latest_price?.value || 0;
        return priceB - priceA;
      }
      return 0;
    });
  };

  const getDemandColor = (trend) => {
    if (trend === 'high') return '#27ae60';
    if (trend === 'low') return '#e74c3c';
    return '#f39c12';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return <TrendingUp size={18} color="#27ae60" />;
    if (trend === 'decreasing') return <TrendingDown size={18} color="#e74c3c" />;
    return <DollarSign size={18} color="#3498db" />;
  };

  const filteredCrops = getFilteredAndSortedCrops();

  return (
    <div className="global-market-access-page section">
      <div className="container">
        {/* Page Header */}
        <div className="page-header">
          <div className="header-content">
            <Globe size={40} className="header-icon" />
            <div>
              <h2>Global Market Access</h2>
              <p>Monitor real-time market prices, trends, and demand across all crops in the system</p>
            </div>
          </div>
        </div>

        {/* Controls Section */}
        <div className="controls-section card">
          <div className="controls-group">
            <div className="control">
              <label>Filter by Trend</label>
              <select value={filterTrend} onChange={(e) => setFilterTrend(e.target.value)}>
                <option value="all">All Trends</option>
                <option value="increasing">Increasing ↑</option>
                <option value="decreasing">Decreasing ↓</option>
                <option value="stable">Stable →</option>
              </select>
            </div>

            <div className="control">
              <label>Sort By</label>
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="name">Crop Name</option>
                <option value="demand">Demand Level</option>
                <option value="price">Price (High to Low)</option>
              </select>
            </div>

            <div className="control-info">
              <p><strong>{filteredCrops.length}</strong> crops found</p>
            </div>
          </div>
        </div>

        {/* Market Data Grid */}
        {loading ? (
          <div className="loading-section">
            <div className="spinner"></div>
            <p>Loading market data for {crops.length} crops...</p>
          </div>
        ) : filteredCrops.length > 0 ? (
          <div className="market-grid">
            {filteredCrops.map(crop => {
              const data = marketData[crop];
              if (!data || data.status !== 'success') return null;

              const marketInfo = data.market_data;
              const price = marketInfo?.latest_price;
              const trend = marketInfo?.global_demand || marketInfo?.demand_trend;
              const priceChange = marketInfo?.price_change_90d_pct || 0;

              return (
                <div 
                  key={crop} 
                  className="market-card card"
                  onClick={() => setSelectedCrop(selectedCrop === crop ? null : crop)}
                >
                  <div className="card-header">
                    <h3>{crop.charAt(0).toUpperCase() + crop.slice(1)}</h3>
                    <span 
                      className="demand-badge"
                      style={{ backgroundColor: getDemandColor(trend) }}
                    >
                      {trend || 'N/A'}
                    </span>
                  </div>

                  <div className="card-body">
                    {/* Price Information */}
                    {price && (
                      <div className="price-section">
                        <div className="price-display">
                          <span className="price-label">Current Price</span>
                          <span className="price-value">₹{price.value || 'N/A'}</span>
                          <span className="price-unit">/{price.unit || 'quintal'}</span>
                        </div>
                        
                        {priceChange !== 0 && (
                          <div className="price-change" style={{
                            color: priceChange > 0 ? '#27ae60' : '#e74c3c'
                          }}>
                            {priceChange > 0 ? '+' : ''}{priceChange.toFixed(2)}%
                          </div>
                        )}
                      </div>
                    )}

                    {/* Trend Indicator */}
                    <div className="trend-section">
                      <span className="trend-label">Market Trend</span>
                      <div className="trend-display">
                        {getTrendIcon(marketInfo?.global_demand)}
                        <span>{marketInfo?.global_demand || 'Stable'}</span>
                      </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="stats-grid">
                      <div className="stat">
                        <span className="stat-label">Records</span>
                        <span className="stat-value">{marketInfo?.records || 'N/A'}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Stability</span>
                        <span className="stat-value">{marketInfo?.price_stability || 'N/A'}</span>
                      </div>
                    </div>

                    {/* Expandable Details */}
                    {selectedCrop === crop && data.market_data && (
                      <div className="expanded-details">
                        <hr />
                        
                        {marketInfo?.latest_price && (
                          <div className="detail-group">
                            <h4>Price Information</h4>
                            <div className="detail-row">
                              <span>Latest:</span>
                              <strong>₹{marketInfo.latest_price.value}</strong>
                            </div>
                            {marketInfo?.recent_average && (
                              <div className="detail-row">
                                <span>30-Day Avg:</span>
                                <strong>₹{marketInfo.recent_average.value}</strong>
                              </div>
                            )}
                          </div>
                        )}

                        {marketInfo?.forecast_30d && (
                          <div className="detail-group">
                            <h4>30-Day Forecast</h4>
                            <div className="detail-row">
                              <span>Expected Avg:</span>
                              <strong>₹{marketInfo.forecast_30d.avg}</strong>
                            </div>
                            <div className="detail-row">
                              <span>Range:</span>
                              <strong>₹{marketInfo.forecast_30d.min} - ₹{marketInfo.forecast_30d.max}</strong>
                            </div>
                          </div>
                        )}

                        {marketInfo?.recommendation && (
                          <div className="detail-group">
                            <h4>Market Insight</h4>
                            <p className="recommendation">{marketInfo.recommendation}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="no-data card">
            <BarChart3 size={48} />
            <p>No crops match the selected filters</p>
          </div>
        )}

        {/* Legend */}
        <div className="legend card">
          <h4>Legend</h4>
          <div className="legend-items">
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#27ae60' }}></span>
              <span>High Demand</span>
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#f39c12' }}></span>
              <span>Moderate Demand</span>
            </div>
            <div className="legend-item">
              <span className="legend-color" style={{ backgroundColor: '#e74c3c' }}></span>
              <span>Low Demand</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default GlobalMarketAccess;
