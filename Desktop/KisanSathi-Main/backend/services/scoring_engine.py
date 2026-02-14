"""
Scoring Engine
Implements the weighted decision matrix that ranks crops based on
suitability, profit, demand, and risk factors.
"""

from typing import Dict, List, Any, Tuple
from services.data_loader import get_data_loader
from services.risk_analysis import RiskAnalyzer


class ScoringEngine:
    """
    Core recommendation engine using weighted scoring algorithm.
    
    Weights default to:
    - Suitability: 30%
    - Profit: 30%
    - Demand: 20%
    - Risk: 20% (inverse - lower risk = higher score)
    
    Can be dynamically adjusted based on risk_preference.
    """
    
    # Default scoring weights (must sum to 100)
    WEIGHTS = {
        'suitability': 0.30,
        'profit': 0.30,
        'demand': 0.20,
        'risk': 0.20
    }
    
    # Risk appetite weight profiles
    RISK_PROFILES = {
        'conservative': {
            'suitability': 0.30,
            'profit': 0.20,
            'demand': 0.15,
            'risk': 0.35
        },
        'balanced': {
            'suitability': 0.30,
            'profit': 0.30,
            'demand': 0.20,
            'risk': 0.20
        },
        'aggressive': {
            'suitability': 0.20,
            'profit': 0.40,
            'demand': 0.25,
            'risk': 0.15
        }
    }
    
    def __init__(self):
        """Initialize scoring engine with data and risk analyzer."""
        self.data_loader = get_data_loader()
        self.risk_analyzer = RiskAnalyzer()
    
    def recommend(
        self,
        location: str,
        season: str,
        water_availability: str,
        top_n: int = 3,
        risk_preference: str = 'balanced'
    ) -> List[Dict[str, Any]]:
        """
        Generate crop recommendations ranked by comprehensive scoring.
        
        Args:
            location: District/Village
            season: Kharif, Rabi, or Zaid
            water_availability: Low, Medium, or High
            top_n: Number of top recommendations to return
            risk_preference: 'conservative', 'balanced', or 'aggressive'
            
        Returns:
            list: Top N ranked crops with detailed scores and explanations
        """
        
        # Validate input
        if not self.data_loader.validate_location(location):
            raise ValueError(f"Location '{location}' not found in database")
        
        # Select risk profile
        risk_preference = risk_preference.lower() if risk_preference else 'balanced'
        if risk_preference not in self.RISK_PROFILES:
            risk_preference = 'balanced'
        weights = self.RISK_PROFILES[risk_preference]
        
        # Get crops suitable for this season
        season_crops = self.data_loader.get_crops_by_season(season)
        
        if not season_crops:
            raise ValueError(f"No crops found for season '{season}'")
        
        # Score each crop
        scored_crops = []
        for crop in season_crops:
            score_data = self._score_crop(crop, location, season, water_availability, weights)
            scored_crops.append(score_data)
        
        # Sort by final score (descending)
        scored_crops.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Return top N
        return scored_crops[:top_n]
    
    def _score_crop(
        self,
        crop: Dict[str, Any],
        location: str,
        season: str,
        water_availability: str,
        weights: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive score for a single crop.
        
        Args:
            crop: Crop data
            location: District
            season: Growing season
            water_availability: Water level
            weights: Custom weight dictionary (if None, uses default)
            
        Returns:
            dict: Complete scoring breakdown and recommendation
        """
        
        # Use provided weights or defaults
        if weights is None:
            weights = self.WEIGHTS
        
        # Calculate individual component scores
        suitability_score = self._calculate_suitability(crop, location, water_availability)
        profit_score = self._calculate_profit(crop, location)
        demand_score = self._calculate_demand(crop, location)
        risk_data = self.risk_analyzer.calculate_risk_score(
            crop, location, season, water_availability
        )
        risk_score = 100 - risk_data['risk_score']  # Inverse - lower risk = higher score
        
        # Calculate final weighted score
        final_score = (
            (suitability_score * weights['suitability']) +
            (profit_score * weights['profit']) +
            (demand_score * weights['demand']) +
            (risk_score * weights['risk'])
        )
        
        # Get price data for profit details
        price_data = self.data_loader.get_price_for_crop_region(crop['id'], location)
        
        return {
            'crop_id': crop['id'],
            'crop_name': crop['name'],
            'hindi_name': crop.get('hindi_name', ''),
            'final_score': round(final_score, 2),
            'scores': {
                'suitability': round(suitability_score, 2),
                'profit': round(profit_score, 2),
                'demand': round(demand_score, 2),
                'risk_inverted': round(risk_score, 2)
            },
            'risk': risk_data,
            'profit_estimate': {
                'base_yield': crop.get('base_yield', 0),
                'yield_unit': 'quintal/hectare',
                'market_price': price_data.get('current_price', 0),
                'input_cost': crop.get('input_cost', 0),
                'cost_unit': 'INR/hectare',
                'expected_revenue': self._estimate_revenue(crop, price_data),
                'estimated_profit': self._estimate_profit(crop, price_data)
            },
            'demand': {
                'local_trend': price_data.get('price_trend', 'stable'),
                'export_potential': crop.get('export_potential', 0),
                'demand_level': self._categorize_demand(price_data.get('export_demand', 'medium'))
            },
            'explanation': self._generate_explanation(crop, final_score, risk_data, price_data)
        }
    
    def _calculate_suitability(
        self,
        crop: Dict[str, Any],
        location: str,
        water_availability: str
    ) -> float:
        """
        Calculate suitability score based on region compatibility and water fit.
        
        Args:
            crop: Crop details
            location: District
            water_availability: Water level
            
        Returns:
            float: Score 0-100
        """
        score = 0.0
        
        # Check if crop is in list of suitable regions
        crop_regions = crop.get('regions', [])
        if location in crop_regions:
            score += 40.0
        else:
            score += 10.0
        
        # Check water requirement match
        crop_water = crop.get('water_requirement', 'Medium').lower()
        available_water = water_availability.lower()
        
        water_match = {
            ('high', 'high'): 40,
            ('high', 'medium'): 25,
            ('high', 'low'): 5,
            ('medium', 'high'): 35,
            ('medium', 'medium'): 40,
            ('medium', 'low'): 25,
            ('low', 'high'): 35,
            ('low', 'medium'): 30,
            ('low', 'low'): 40
        }
        
        water_score = water_match.get((crop_water, available_water), 20)
        score += water_score
        
        return min(100, score)
    
    def _calculate_profit(self, crop: Dict[str, Any], location: str) -> float:
        """
        Calculate profit potential based on yield and market price.
        
        Args:
            crop: Crop details
            location: District
            
        Returns:
            float: Score 0-100
        """
        yield_qty = crop.get('base_yield', 40)
        input_cost = crop.get('input_cost', 20000)
        
        price_data = self.data_loader.get_price_for_crop_region(crop['id'], location)
        market_price = price_data.get('current_price', 2000)
        
        # Calculate gross and net values
        revenue = yield_qty * market_price
        profit = revenue - input_cost
        
        # Normalize profit to 0-100 scale
        # Assumption: 50000 INR profit = 100, 0 or less = 0
        profit_score = min(100, max(0, (profit / 50000) * 100))
        
        return profit_score
    
    def _calculate_demand(self, crop: Dict[str, Any], location: str) -> float:
        """
        Calculate demand score based on local trend and export potential.
        
        Args:
            crop: Crop details
            location: District
            
        Returns:
            float: Score 0-100
        """
        score = 0.0
        
        # Local trend component
        price_data = self.data_loader.get_price_for_crop_region(crop['id'], location)
        trend = price_data.get('price_trend', 'stable').lower()
        
        trend_score = {
            'up': 60,
            'stable': 40,
            'down': 20
        }.get(trend, 40)
        score += trend_score * 0.5
        
        # Export potential component
        export_potential = crop.get('export_potential', 0.5)
        export_score = export_potential * 100  # Scale 0-1 to 0-100
        score += export_score * 0.5
        
        return min(100, score)
    
    def _estimate_revenue(self, crop: Dict[str, Any], price_data: Dict[str, Any]) -> float:
        """
        Calculate estimated revenue.
        
        Args:
            crop: Crop details
            price_data: Market price data
            
        Returns:
            float: Estimated revenue in INR
        """
        yield_qty = crop.get('base_yield', 40)
        price = price_data.get('current_price', 2000)
        return yield_qty * price
    
    def _estimate_profit(self, crop: Dict[str, Any], price_data: Dict[str, Any]) -> float:
        """
        Calculate estimated profit.
        
        Args:
            crop: Crop details
            price_data: Market price data
            
        Returns:
            float: Estimated profit in INR
        """
        revenue = self._estimate_revenue(crop, price_data)
        input_cost = crop.get('input_cost', 20000)
        return revenue - input_cost
    
    def _categorize_demand(self, export_demand_str: str) -> str:
        """
        Convert export demand string to level.
        
        Args:
            export_demand_str: Export demand value
            
        Returns:
            str: Demand level
        """
        demand_map = {
            'very_high': 'Very High',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        }
        return demand_map.get(export_demand_str.lower(), 'Unknown')
    
    def _generate_explanation(
        self,
        crop: Dict[str, Any],
        final_score: float,
        risk_data: Dict[str, Any],
        price_data: Dict[str, Any]
    ) -> str:
        """
        Generate farmer-friendly explanation for recommendation.
        
        Args:
            crop: Crop details
            final_score: Overall recommendation score
            risk_data: Risk analysis results
            price_data: Market price data
            
        Returns:
            str: Plain-language explanation
        """
        crop_name = crop['name']
        season = crop.get('season', 'suitable seasons')
        water_req = crop.get('water_requirement', 'moderate water')
        hindi_name = crop.get('hindi_name', '')
        
        explanation = f"We recommend {crop_name} ({hindi_name}). "
        
        # Season explanation
        explanation += f"It's perfect for {season} season. "
        
        # Water explanation
        water_req_lower = water_req.lower()
        if water_req_lower == 'high':
            explanation += "It needs good water supply. "
        elif water_req_lower == 'low':
            explanation += "It's drought-resistant and can thrive with less water. "
        else:
            explanation += "It needs moderate water. "
        
        # Price explanation
        trend = price_data.get('price_trend', 'stable')
        if trend == 'up':
            explanation += "Market prices are currently rising. "
        elif trend == 'down':
            explanation += "Market prices are soft, but stable. "
        
        # Risk note
        risk_level = risk_data.get('risk_level', 'Medium')
        if risk_level == 'Low':
            explanation += "Risk is low, making it a safe choice."
        elif risk_level == 'Medium':
            explanation += "Risk is moderate - follow good farming practices."
        else:
            explanation += "Risk is higher - best for experienced farmers."
        
        return explanation
