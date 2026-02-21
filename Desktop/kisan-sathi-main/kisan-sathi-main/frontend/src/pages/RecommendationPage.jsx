import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { Send, AlertCircle, MapPin, HelpCircle } from 'lucide-react';
import '../styles/RecommendationPage.css';

function RecommendationPage() {
  // Input mode toggle
  const [inputMode, setInputMode] = useState('location');
  
  // Location data
  const [locations, setLocations] = useState({});
  const [selectedState, setSelectedState] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('');
  const [loadingLocations, setLoadingLocations] = useState(true);
  const [autoFilled, setAutoFilled] = useState(false);
  
  // Testing centers
  const [testingCenters, setTestingCenters] = useState([]);
  const [showCenters, setShowCenters] = useState(false);
  
  const [formData, setFormData] = useState({
    nitrogen: '',
    phosphorus: '',
    potassium: '',
    temperature: '',
    humidity: '',
    ph: '',
    rainfall: ''
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [showResults, setShowResults] = useState(false);

  // Load locations on mount
  useEffect(() => {
    fetchLocations();
  }, []);

  const fetchLocations = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/locations');
      const data = await response.json();
      if (data.status === 'success') {
        setLocations(data.locations);
      }
    } catch (error) {
      console.error('Error fetching locations:', error);
    } finally {
      setLoadingLocations(false);
    }
  };

  const handleStateChange = async (e) => {
    const state = e.target.value;
    setSelectedState(state);
    setSelectedDistrict('');
    setAutoFilled(false);
    
    if (state && inputMode === 'location') {
      await fetchSoilData(state, '');
    }
  };

  const handleDistrictChange = async (e) => {
    const district = e.target.value;
    setSelectedDistrict(district);
    
    if (selectedState && district && inputMode === 'location') {
      await fetchSoilData(selectedState, district);
    }
  };

  const fetchSoilData = async (state, district) => {
    try {
      setLoading(true);
      let url = `http://localhost:5000/api/soil-data?state=${encodeURIComponent(state)}`;
      if (district) {
        url += `&district=${encodeURIComponent(district)}`;
      }
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === 'success') {
        setFormData(prev => ({
          ...prev,
          nitrogen: data.soil_data.nitrogen,
          phosphorus: data.soil_data.phosphorus,
          potassium: data.soil_data.potassium,
          ph: data.soil_data.ph
        }));
        setAutoFilled(true);
      }
    } catch (error) {
      console.error('Error fetching soil data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchTestingCenters = async () => {
    if (!selectedState) return;
    
    try {
      const response = await fetch(`http://localhost:5000/api/testing-centers?state=${encodeURIComponent(selectedState)}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setTestingCenters(data.centers);
        setShowCenters(true);
      }
    } catch (error) {
      console.error('Error fetching testing centers:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    const { nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall } = formData;

    if (!nitrogen || nitrogen < 0 || nitrogen > 140) newErrors.nitrogen = 'Enter N value (0-140)';
    if (!phosphorus || phosphorus < 0 || phosphorus > 145) newErrors.phosphorus = 'Enter P value (0-145)';
    if (!potassium || potassium < 0 || potassium > 205) newErrors.potassium = 'Enter K value (0-205)';
    if (!temperature || temperature < 5 || temperature > 50) newErrors.temperature = 'Enter temperature (5-50°C)';
    if (!humidity || humidity < 0 || humidity > 100) newErrors.humidity = 'Enter humidity (0-100%)';
    if (!ph || ph < 3 || ph > 10) newErrors.ph = 'Enter pH (3-10)';
    if (!rainfall || rainfall < 0 || rainfall > 300) newErrors.rainfall = 'Enter rainfall (0-300cm)';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/recommend-crop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          nitrogen: parseFloat(formData.nitrogen),
          phosphorus: parseFloat(formData.phosphorus),
          potassium: parseFloat(formData.potassium),
          temperature: parseFloat(formData.temperature),
          humidity: parseFloat(formData.humidity),
          ph: parseFloat(formData.ph),
          rainfall: parseFloat(formData.rainfall)
        })
      });

      const data = await response.json();

      if (data.status === 'success') {
        setResults(data);
        setShowResults(true);
      } else {
        setErrors({ submit: data.message || 'Error getting recommendations' });
      }
    } catch (error) {
      setErrors({ submit: 'Failed to connect to server. Make sure Flask backend is running.' });
    } finally {
      setLoading(false);
    }
  };

  if (showResults && results) {
    return <Navigate to="/results" state={{ results }} />;
  }

  return (
    <div className="recommendation-page section">
      <div className="container">
        <div className="form-wrapper">
          <div className="form-header">
            <h2>Get Crop Recommendations</h2>
            <p>
              Enter your soil and environmental conditions to receive AI-powered 
              crop recommendations tailored to your farm
            </p>
          </div>

          {errors.submit && (
            <div className="error-message">
              <AlertCircle size={20} />
              {errors.submit}
            </div>
          )}

          {/* Mode Toggle */}
          <div className="mode-toggle">
            <button
              type="button"
              className={`mode-btn ${inputMode === 'location' ? 'active' : ''}`}
              onClick={() => setInputMode('location')}
            >
              <MapPin size={18} /> Use My Location
            </button>
            <button
              type="button"
              className={`mode-btn ${inputMode === 'manual' ? 'active' : ''}`}
              onClick={() => setInputMode('manual')}
            >
              ✏️ Enter Soil Test Data
            </button>
          </div>

          <form onSubmit={handleSubmit} className="recommendation-form">
            
            {/* Location Selection */}
            {inputMode === 'location' && (
              <div className="location-section">
                <h3>📍 Your Location</h3>
                <div className="grid grid-2">
                  <div className="form-group">
                    <label htmlFor="state" className="form-label">State *</label>
                    <select
                      id="state"
                      value={selectedState}
                      onChange={handleStateChange}
                      className="form-input"
                      disabled={loadingLocations}
                    >
                      <option value="">Select State</option>
                      {Object.keys(locations).sort().map(state => (
                        <option key={state} value={state}>{state}</option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="district" className="form-label">District (Optional)</label>
                    <select
                      id="district"
                      value={selectedDistrict}
                      onChange={handleDistrictChange}
                      className="form-input"
                      disabled={!selectedState}
                    >
                      <option value="">Select District</option>
                      {selectedState && locations[selectedState]?.map(district => (
                        <option key={district} value={district}>{district}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {autoFilled && (
                  <div className="info-box">
                    ✅ Soil parameters auto-filled based on your location! You can adjust weather data below.
                  </div>
                )}

                <button
                  type="button"
                  onClick={fetchTestingCenters}
                  className="testing-btn"
                  disabled={!selectedState}
                >
                  🔬 Find Nearby Soil Testing Centers
                </button>

                {showCenters && testingCenters.length > 0 && (
                  <div className="centers-box">
                    <h4>Nearby Soil Testing Centers:</h4>
                    {testingCenters.map((center, idx) => (
                      <div key={idx} className="center-item">
                        <strong>{center.name}</strong><br />
                        📍 {center.location} | 📞 {center.phone}
                      </div>
                    ))}
                    <p className="helpline">
                      Kisan Call Centre: <strong>1800-180-1551</strong> (Toll Free)
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Soil Nutrients Section */}
            <div className="form-section">
              <h3>🌱 Soil Nutrients (NPK) {autoFilled && <span className="badge">Auto-filled</span>}</h3>
              <div className="grid grid-2">
                <div className="form-group">
                  <label htmlFor="nitrogen" className="form-label">
                    Nitrogen (N) <span className="unit">mg/kg</span>
                    <span className="tooltip">
                      <HelpCircle size={14} />
                      <span className="tooltip-text">For leaf growth. Range: 0-140</span>
                    </span>
                  </label>
                  <input
                    type="number"
                    id="nitrogen"
                    name="nitrogen"
                    value={formData.nitrogen}
                    onChange={handleInputChange}
                    className={`form-input ${errors.nitrogen ? 'input-error' : ''}`}
                    placeholder="0-140"
                    step="0.1"
                    readOnly={inputMode === 'location' && !autoFilled}
                  />
                  {errors.nitrogen && <span className="error-text">{errors.nitrogen}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="phosphorus" className="form-label">
                    Phosphorus (P) <span className="unit">mg/kg</span>
                    <span className="tooltip">
                      <HelpCircle size={14} />
                      <span className="tooltip-text">For root development. Range: 0-145</span>
                    </span>
                  </label>
                  <input
                    type="number"
                    id="phosphorus"
                    name="phosphorus"
                    value={formData.phosphorus}
                    onChange={handleInputChange}
                    className={`form-input ${errors.phosphorus ? 'input-error' : ''}`}
                    placeholder="0-145"
                    step="0.1"
                    readOnly={inputMode === 'location' && !autoFilled}
                  />
                  {errors.phosphorus && <span className="error-text">{errors.phosphorus}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="potassium" className="form-label">
                    Potassium (K) <span className="unit">mg/kg</span>
                    <span className="tooltip">
                      <HelpCircle size={14} />
                      <span className="tooltip-text">For disease resistance. Range: 0-205</span>
                    </span>
                  </label>
                  <input
                    type="number"
                    id="potassium"
                    name="potassium"
                    value={formData.potassium}
                    onChange={handleInputChange}
                    className={`form-input ${errors.potassium ? 'input-error' : ''}`}
                    placeholder="0-205"
                    step="0.1"
                    readOnly={inputMode === 'location' && !autoFilled}
                  />
                  {errors.potassium && <span className="error-text">{errors.potassium}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="ph" className="form-label">
                    Soil pH <span className="unit">3-10</span>
                    <span className="tooltip">
                      <HelpCircle size={14} />
                      <span className="tooltip-text">Soil acidity. Range: 3-10</span>
                    </span>
                  </label>
                  <input
                    type="number"
                    id="ph"
                    name="ph"
                    value={formData.ph}
                    onChange={handleInputChange}
                    className={`form-input ${errors.ph ? 'input-error' : ''}`}
                    placeholder="3-10"
                    step="0.1"
                    readOnly={inputMode === 'location' && !autoFilled}
                  />
                  {errors.ph && <span className="error-text">{errors.ph}</span>}
                </div>
              </div>
            </div>

            {/* Environmental Conditions */}
            <div className="form-section">
              <h3>🌤️ Environmental Conditions</h3>
              <div className="grid grid-2">
                <div className="form-group">
                  <label htmlFor="temperature" className="form-label">
                    Temperature <span className="unit">°C</span>
                  </label>
                  <input
                    type="number"
                    id="temperature"
                    name="temperature"
                    value={formData.temperature}
                    onChange={handleInputChange}
                    placeholder="5-50"
                    className={`form-input ${errors.temperature ? 'input-error' : ''}`}
                    step="0.1"
                  />
                  {errors.temperature && <span className="error-text">{errors.temperature}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="humidity" className="form-label">
                    Humidity <span className="unit">%</span>
                  </label>
                  <input
                    type="number"
                    id="humidity"
                    name="humidity"
                    value={formData.humidity}
                    onChange={handleInputChange}
                    placeholder="0-100"
                    className={`form-input ${errors.humidity ? 'input-error' : ''}`}
                    step="0.1"
                    max="100"
                  />
                  {errors.humidity && <span className="error-text">{errors.humidity}</span>}
                </div>

                <div className="form-group full-width">
                  <label htmlFor="rainfall" className="form-label">
                    Rainfall <span className="unit">cm</span>
                  </label>
                  <input
                    type="number"
                    id="rainfall"
                    name="rainfall"
                    value={formData.rainfall}
                    onChange={handleInputChange}
                    placeholder="0-300"
                    className={`form-input ${errors.rainfall ? 'input-error' : ''}`}
                    step="0.1"
                  />
                  {errors.rainfall && <span className="error-text">{errors.rainfall}</span>}
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="form-actions">
              <button 
                type="submit" 
                className="btn btn-primary btn-submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-small"></span>
                    Processing...
                  </>
                ) : (
                  <>
                    <Send size={20} />
                    Get Recommendations
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Tips Section */}
          <div className="tips-section">
            <h3>💡 Tips for Better Recommendations</h3>
            <ul>
              <li><strong>Soil Test:</strong> Get your soil tested from a local agricultural lab for accurate NPK values</li>
              <li><strong>Weather Data:</strong> Use average temperature and humidity for your region</li>
              <li><strong>Rainfall:</strong> Consider annual rainfall in your area</li>
              <li><strong>Precision:</strong> More accurate inputs lead to better recommendations</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default RecommendationPage;
