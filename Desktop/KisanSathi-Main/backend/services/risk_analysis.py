"""
Risk Analysis Service
Analyzes crop risk factors including weather sensitivity, price volatility,
and environmental conditions.
"""

from typing import Dict, Any, Tuple
from services.data_loader import get_data_loader


class RiskAnalyzer:
    """Analyzes risk factors for crop recommendations."""
    
    # Risk categorization thresholds
    LOW_RISK_THRESHOLD = 30
    MEDIUM_RISK_THRESHOLD = 60
    HIGH_RISK_THRESHOLD = 100
    
    def __init__(self):
        """Initialize risk analyzer with data loader."""
        self.data_loader = get_data_loader()
    
    def calculate_risk_score(
        self,
        crop: Dict[str, Any],
        region: str,
        season: str,
        water_availability: str
    ) -> Dict[str, Any]:
        """
        Calculate overall risk score for a crop in given conditions.
        
        Args:
            crop: Crop data dictionary
            region: Location/district name
            season: Growing season (Kharif/Rabi/Zaid)
            water_availability: Water level (Low/Medium/High)
            
        Returns:
            dict: Risk assessment with score, level, color, and factors
        """
        
        # Calculate individual risk components (0-100 scale)
        weather_risk = self._calculate_weather_risk(crop, region, season, water_availability)
        price_volatility_risk = self._calculate_price_risk(crop, region)
        seasonal_risk = self._calculate_seasonal_risk(crop, season)
        water_risk = self._calculate_water_risk(crop, water_availability)
        
        # Weighted average of risk factors
        overall_risk = (
            (weather_risk * 0.35) +
            (price_volatility_risk * 0.30) +
            (seasonal_risk * 0.20) +
            (water_risk * 0.15)
        )
        
        # Normalize to 0-100
        risk_score = min(100, max(0, overall_risk))
        
        # Determine risk level and color
        risk_level, risk_color = self._categorize_risk(risk_score)
        
        return {
            'risk_score': round(risk_score, 2),
            'risk_level': risk_level,
            'risk_color': risk_color,
            'factors': {
                'weather_risk': round(weather_risk, 2),
                'price_volatility': round(price_volatility_risk, 2),
                'seasonal_fit': round(seasonal_risk, 2),
                'water_suitability': round(water_risk, 2)
            },
            'explanation': self._generate_risk_explanation(
                crop, risk_level, weather_risk, price_volatility_risk
            )
        }
    
    def _calculate_weather_risk(
        self,
        crop: Dict[str, Any],
        region: str,
        season: str,
        water_availability: str
    ) -> float:
        """
        Calculate weather-related risk based on temperature and rainfall.
        
        Args:
            crop: Crop details
            region: Location
            season: Growing season
            water_availability: Available water
            
        Returns:
            float: Risk score (0-100)
        """
        weather = self.data_loader.get_weather_for_region(region)
        
        if not weather:
            return 25.0  # Neutral risk if no data
        
        # Check temperature compatibility
        temp_risk = 0.0
        current_temp = weather.get('temperature', {}).get('avg', 25)
        min_temp = crop.get('min_temperature', 10)
        max_temp = crop.get('max_temperature', 35)
        
        if current_temp < min_temp or current_temp > max_temp:
            temp_risk = 40.0  # High risk if out of range
        else:
            # Lower risk if within comfortable range
            mid_temp = (min_temp + max_temp) / 2
            temp_diff = abs(current_temp - mid_temp)
            range_width = (max_temp - min_temp) / 2
            temp_risk = (temp_diff / range_width) * 30.0
        
        # Check rainfall/water risk
        rainfall_risk = 0.0
        rainfall_data = weather.get('rainfall', {}).get(season, {})
        recent_rainfall = rainfall_data.get('recent', 100)
        avg_rainfall = rainfall_data.get('avg', 100)
        
        crop_water = crop.get('water_requirement', 'Medium').lower()
        
        if crop_water == 'high' and recent_rainfall < avg_rainfall * 0.7:
            rainfall_risk = 35.0
        elif crop_water == 'low' and recent_rainfall > avg_rainfall * 1.3:
            rainfall_risk = 25.0  # Excess water risk for low-water crops
        else:
            rainfall_risk = 10.0
        
        # Soil moisture compatibility
        soil_moisture = weather.get('soil_moisture', 'medium').lower()
        moisture_risk = 0.0
        
        if crop_water == 'high' and soil_moisture == 'low':
            moisture_risk = 30.0
        elif crop_water == 'low' and soil_moisture == 'high':
            moisture_risk = 15.0
        else:
            moisture_risk = 5.0
        
        # Average the weather components
        weather_risk = (temp_risk + rainfall_risk + moisture_risk) / 3
        return min(100, weather_risk)
    
    def _calculate_price_risk(self, crop: Dict[str, Any], region: str) -> float:
        """
        Calculate price volatility risk.
        
        Args:
            crop: Crop details
            region: Location
            
        Returns:
            float: Risk score (0-100)
        """
        price_data = self.data_loader.get_price_for_crop_region(crop['id'], region)
        
        if not price_data:
            return 20.0  # Neutral if no data
        
        # Price trend risk (down = higher risk)
        trend = price_data.get('price_trend', 'stable').lower()
        trend_risk = {
            'down': 40.0,
            'stable': 20.0,
            'up': 10.0
        }.get(trend, 20.0)
        
        # Stability - measure of price volatility
        stability = price_data.get('stability', 'medium').lower()
        stability_risk = {
            'high': 5.0,
            'medium': 25.0,
            'low': 45.0
        }.get(stability, 25.0)
        
        # Export demand affects market stability
        export_demand = price_data.get('export_demand', 'medium').lower()
        demand_risk = {
            'very_high': 5.0,
            'high': 15.0,
            'medium': 25.0,
            'low': 40.0
        }.get(export_demand, 25.0)
        
        price_risk = (trend_risk + stability_risk + demand_risk) / 3
        return min(100, price_risk)
    
    def _calculate_seasonal_risk(self, crop: Dict[str, Any], season: str) -> float:
        """
        Calculate seasonal fit risk (lower if crop matches season).
        
        Args:
            crop: Crop details
            season: Growing season
            
        Returns:
            float: Risk score (0-100)
        """
        supported_seasons = crop.get('season', '').split('|')
        
        if season in supported_seasons:
            return 10.0  # Low risk if season matches
        else:
            return 70.0  # High risk if season doesn't match
    
    def _calculate_water_risk(self, crop: Dict[str, Any], water_availability: str) -> float:
        """
        Calculate water availability risk.
        
        Args:
            crop: Crop details
            water_availability: Available water level
            
        Returns:
            float: Risk score (0-100)
        """
        crop_water = crop.get('water_requirement', 'Medium').lower()
        available_water = water_availability.lower()
        
        # Match matrix - lower values = better match = lower risk
        match_matrix = {
            'high': {'high': 10, 'medium': 40, 'low': 70},
            'medium': {'high': 20, 'medium': 10, 'low': 35},
            'low': {'high': 30, 'medium': 15, 'low': 10}
        }
        
        risk = match_matrix.get(crop_water, {}).get(available_water, 50)
        return float(risk)
    
    def _categorize_risk(self, risk_score: float) -> Tuple[str, str]:
        """
        Categorize risk score into level and assign color.
        
        Args:
            risk_score: Numeric score (0-100)
            
        Returns:
            tuple: (risk_level, color_code)
        """
        if risk_score <= self.LOW_RISK_THRESHOLD:
            return 'Low', 'green'
        elif risk_score <= self.MEDIUM_RISK_THRESHOLD:
            return 'Medium', 'yellow'
        else:
            return 'High', 'red'
    
    def _generate_risk_explanation(
        self,
        crop: Dict[str, Any],
        risk_level: str,
        weather_risk: float,
        price_risk: float
    ) -> str:
        """
        Generate farmer-friendly explanation of risks.
        
        Args:
            crop: Crop details
            risk_level: Risk categorization
            weather_risk: Weather component score
            price_risk: Price volatility component score
            
        Returns:
            str: Plain-language explanation
        """
        crop_name = crop.get('name', 'This crop')
        explanation = f"{crop_name} carries a {risk_level.lower()} risk profile. "
        
        if weather_risk > 40:
            explanation += "Weather conditions may be challenging. "
        else:
            explanation += "Weather is favorable for growth. "
        
        if price_risk > 40:
            explanation += "Market prices are unstable, but demand exists. "
        else:
            explanation += "Market prices have been stable with good demand. "
        
        if risk_level == 'Low':
            explanation += "This is a safer choice for your conditions."
        elif risk_level == 'Medium':
            explanation += "Monitor weather and pest management closely."
        else:
            explanation += "Only choose if you have experience with this crop."
        
        return explanation
