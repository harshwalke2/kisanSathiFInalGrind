# Demo Endpoint Guide - `/api/global/demo/<crop>`

## Overview
The demo endpoint provides **complete structured showcase data** for hackathon presentations and system demonstrations. It combines predictions, market insights, and system capabilities into a single comprehensive response.

## Endpoint

```
GET /api/global/demo/<crop>
```

## Parameters

- **crop** (string, required): Crop name
  - Example: `rice`, `wheat`, `maize`, `cotton`, `sugarcane`
  - See `/api/crops/list` for full list of 22 supported crops

## Response Structure

The response includes:

### 1. **Crop Information**
```json
{
  "crop_info": {
    "name": "rice",
    "normalized_name": "rice",
    "available_in_system": true,
    "total_crops_in_system": 22
  }
}
```

### 2. **Prediction Results**
- Input conditions (NPK, temperature, humidity, pH, rainfall)
- Crop suitability with confidence score
- Estimated yield prediction (kg/ha)
- Top 5 crop recommendations with rankings

```json
{
  "prediction_results": {
    "input_conditions": {
      "nitrogen": 50,
      "phosphorus": 40,
      "potassium": 60,
      "temperature": 25,
      "humidity": 75,
      "ph": 6.5,
      "rainfall": 150
    },
    "crop_suitability": {
      "crop": "rice",
      "confidence": 78.5,
      "suitability": "high"
    },
    "estimated_yield": {
      "value": 4500.0,
      "unit": "kg/ha"
    },
    "top_5_recommendations": [
      {
        "crop": "rice",
        "confidence": 78.5,
        "estimated_yield": 4500.0,
        "rank": 1
      },
      // ... more crops
    ]
  }
}
```

### 3. **Market Intelligence**
- Current demand trend (high/moderate/low)
- Price range and trends
- Market records in system
- Outlook assessment

```json
{
  "market_intelligence": {
    "crop": "rice",
    "demand_trend": "high",
    "price_data": {
      "min": 1200.0,
      "max": 2150.0,
      "avg": 1650.5,
      "latest": 1850.0,
      "unit": "INR/quintal"
    },
    "market_records": 15234,
    "trend_analysis": "increasing",
    "market_outlook": "Strong"
  }
}
```

### 4. **Optimal Growing Conditions**
Crop-specific parameters for best results:

```json
{
  "optimal_conditions": {
    "temperature_range": "20-30°C",
    "humidity_range": "70-90%",
    "ph_range": "5.5-7.0",
    "rainfall_range": "1000-1500mm",
    "season": "Rainy/Monsoon"
  }
}
```

### 5. **Risk Assessment**
Comprehensive risk analysis with scores and recommendations:

```json
{
  "risk_assessment": {
    "weather_risk": "medium",
    "market_risk": "low",
    "disease_risk": "medium",
    "pest_risk": "medium",
    "water_stress": "low",
    "overall_risk_score": 5.0,
    "recommendation": "Moderate risk. Suitable for cultivation with standard precautions."
  }
}
```

### 6. **Feature Analysis**
Top influential factors for crop selection:

```json
{
  "feature_analysis": {
    "top_influential_factors": [
      {
        "feature": "nitrogen",
        "importance": 0.245
      },
      // ... more features
    ],
    "total_features_in_model": 14,
    "message": "These factors have the most significant impact on crop selection"
  }
}
```

### 7. **Model Performance Metrics**
System accuracy and reliability metrics:

```json
{
  "model_performance": {
    "models": {
      "crop_classifier": {
        "accuracy": 99.09,
        "f1_score": 0.9908,
        "model_type": "RandomForestClassifier"
      },
      "yield_predictor": {
        "r2_score": 0.954,
        "rmse": 850.5,
        "model_type": "RandomForestRegressor"
      }
    },
    "summary": {
      "crop_classification_accuracy": "99.09%",
      "yield_prediction_r2": 0.954,
      "system_reliability": "High"
    }
  }
}
```

### 8. **Demo Scenarios**
Pre-configured scenarios showing system capabilities:

```json
{
  "demo_scenarios": [
    {
      "title": "High Fertility Soil",
      "description": "Farmer with excellent soil conditions (high NPK)",
      "conditions": {
        "nitrogen": 80,
        "phosphorus": 50,
        "potassium": 70,
        "temperature": 26,
        "humidity": 70,
        "ph": 7.0,
        "rainfall": 180
      },
      "expected_yield": "5.5-6.0 tons/ha"
    },
    // ... more scenarios
  ]
}
```

### 9. **System Capabilities**
Overview of system features and coverage:

```json
{
  "system_capabilities": {
    "total_crops_supported": 22,
    "ml_models": 2,
    "market_data_points": 15234,
    "features_analyzed": 14,
    "seasons_covered": 4,
    "key_features": [
      "Real-time crop recommendations",
      "Automated yield predictions",
      "Market price intelligence",
      "Risk assessment and management",
      "Seasonal insights",
      "Feature importance analysis",
      "Multi-crop comparison"
    ]
  }
}
```

### 10. **Presentation Highlights**
Key talking points for hackathon judges:

```json
{
  "presentation_highlights": {
    "accuracy": "99.09% crop classification accuracy",
    "performance": "95.4% R² yield prediction",
    "coverage": "22 crops across Indian agriculture",
    "data_driven": "Real market data + ML models",
    "farmer_friendly": "Simple mobile-optimized interface",
    "impact": "Helps farmers increase yields & reduce risks"
  }
}
```

### 11. **Related Endpoints**
Links to other API endpoints for additional data:

```json
{
  "related_endpoints": {
    "recommendations": "/api/recommend-crop (POST)",
    "yield_prediction": "/api/yield-prediction (POST)",
    "market_insights": "/api/market-insights/rice (GET)",
    "all_crops": "/api/crops/list (GET)",
    "model_info": "/api/model-info (GET)",
    "feature_importance": "/api/feature-importance (GET)"
  }
}
```

## Example Requests

### Get demo data for Rice
```bash
curl http://localhost:5000/api/global/demo/rice
```

### Get demo data for Wheat
```bash
curl http://localhost:5000/api/global/demo/wheat
```

### Get demo data for Cotton
```bash
curl http://localhost:5000/api/global/demo/cotton
```

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success - Complete demo data returned |
| 404 | Crop not found in system |
| 500 | Server error - Check logs |

## Error Response

```json
{
  "status": "error",
  "message": "Crop 'unknown_crop' not found in system",
  "available_crops": ["apple", "banana", "...", "watermelon"]
}
```

## Use Cases

### Hackathon Presentation
1. Call `/api/global/demo/rice`
2. Display prediction results showing 99% accuracy
3. Show market intelligence with real price data
4. Highlight risk assessment capabilities
5. Present model performance metrics

### Feature Demo
1. Show top 5 crop recommendations
2. Display optimal growing conditions
3. Present market trends and forecasts
4. Demonstrate risk scoring system

### System Testing
1. Verify all models are loaded and working
2. Check market data integration
3. Validate feature importance calculations
4. Confirm system reliability metrics

## Integration Example

```javascript
// Fetch demo data for selected crop
async function getDemoData(cropName) {
  const response = await fetch(`/api/global/demo/${cropName}`);
  const data = await response.json();
  
  // Display prediction results
  console.log(`${data.crop_info.name}:`);
  console.log(`Confidence: ${data.prediction_results.crop_suitability.confidence}%`);
  console.log(`Yield: ${data.prediction_results.estimated_yield.value} kg/ha`);
  
  // Show market insights
  console.log(`Market Trend: ${data.market_intelligence.trend_analysis}`);
  console.log(`Price Range: ${data.market_intelligence.price_data.min}-${data.market_intelligence.price_data.max}`);
  
  // Display system metrics
  console.log(`System Accuracy: ${data.model_performance.summary.crop_classification_accuracy}`);
}
```

## Supported Crops

All 22 crops are supported:
- apple, banana, blackgram, chickpea, coconut, coffee, cotton, grapes, jute
- kidneybeans, lentil, maize, mango, mothbeans, mungbean, muskmelon
- orange, papaya, pigeonpeas, pomegranate, rice, watermelon

## Notes

- Demo uses fixed environmental conditions for consistency
- Market data updates as new price information is added
- Prediction confidence varies based on soil/environment similarity to training data
- All yields are in kg/ha (kilograms per hectare)
- Risk scores range from 0-10 (lower is better)

---

**Created**: February 21, 2026  
**API Version**: 1.0  
**Backend**: Flask with ML Models
