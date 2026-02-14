"""
Water Advisory Service
Provides irrigation recommendations and water compatibility analysis.
"""

from typing import Dict, List, Any
from services.data_loader import get_data_loader


class WaterAdvisory:
    """Provides water and irrigation recommendations."""
    
    # Water requirement levels for crops (mm per season)
    WATER_REQUIREMENTS = {
        'rice': {'low': 800, 'medium': 1000, 'high': 1200},
        'wheat': {'low': 300, 'medium': 400, 'high': 500},
        'cotton': {'low': 500, 'medium': 650, 'high': 800},
        'sugarcane': {'low': 900, 'medium': 1200, 'high': 1500},
        'maize': {'low': 300, 'medium': 400, 'high': 500},
        'groundnut': {'low': 300, 'medium': 400, 'high': 500},
        'soybean': {'low': 400, 'medium': 550, 'high': 650},
        'onion': {'low': 300, 'medium': 400, 'high': 500},
        'potato': {'low': 400, 'medium': 550, 'high': 650},
        'tomato': {'low': 400, 'medium': 550, 'high': 650}
    }
    
    # Irrigation period (days) for each season
    IRRIGATION_PERIODS = {
        'kharif': 120,      # Monsoon - needs less irrigation
        'rabi': 150,        # Winter - needs more irrigation
        'zaid': 90          # Summer - intensive irrigation
    }
    
    def __init__(self):
        """Initialize water advisory with data loader."""
        self.data_loader = get_data_loader()
    
    def get_water_advisory(
        self,
        crop_id: str,
        region: str,
        season: str,
        water_availability: str
    ) -> Dict[str, Any]:
        """
        Get water and irrigation advisory for a crop.
        
        Args:
            crop_id: Crop identifier
            region: Region/district name
            season: Season (kharif/rabi/zaid)
            water_availability: Water availability level (low/medium/high)
            
        Returns:
            dict: Water advisory with compatibility and recommendations
        """
        
        # Get water requirements for crop
        water_req = self.WATER_REQUIREMENTS.get(crop_id.lower(), {}).get(water_availability, 500)
        irrigation_days = self.IRRIGATION_PERIODS.get(season.lower(), 120)
        
        # Calculate daily water requirement
        daily_requirement = water_req / irrigation_days
        
        # Get rainfall data for region
        seasonal_rainfall = self._get_seasonal_rainfall(region, season)
        
        # Calculate water deficit/surplus
        water_deficit = max(0, water_req - seasonal_rainfall)
        water_surplus = max(0, seasonal_rainfall - water_req)
        
        # Calculate compatibility
        compatibility = self._calculate_compatibility(
            water_availability,
            water_req,
            seasonal_rainfall
        )
        
        # Generate irrigation schedule
        irrigation_schedule = self._generate_irrigation_schedule(
            crop_id,
            season,
            daily_requirement,
            water_deficit,
            seasonal_rainfall
        )
        
        # Generate advisory message
        advisory = self._generate_advisory(
            crop_id,
            water_availability,
            seasonal_rainfall,
            water_deficit,
            compatibility
        )
        
        return {
            'success': True,
            'crop_id': crop_id,
            'region': region,
            'season': season,
            'water_availability': water_availability,
            'water_analysis': {
                'crop_requirement_mm': water_req,
                'seasonal_rainfall_mm': seasonal_rainfall,
                'water_deficit_mm': round(water_deficit, 2),
                'water_surplus_mm': round(water_surplus, 2),
                'daily_requirement_mm': round(daily_requirement, 2)
            },
            'compatibility': {
                'score': compatibility,
                'level': self._categorize_compatibility(compatibility),
                'suitable': compatibility >= 60
            },
            'irrigation_schedule': irrigation_schedule,
            'advisory': advisory,
            'water_saving_tips': self._get_water_saving_tips(crop_id, season),
            'drought_risk': 'High' if water_deficit > 200 else 'Moderate' if water_deficit > 100 else 'Low'
        }
    
    def _get_seasonal_rainfall(self, region: str, season: str) -> float:
        """
        Get average seasonal rainfall for region.
        
        Args:
            region: Region name
            season: Season name
            
        Returns:
            float: Rainfall in mm
        """
        
        # Mock rainfall data by region and season (mm)
        rainfall_data = {
            'kharif': {
                'north': 600,    # June-Sept in north India
                'south': 800,    # June-Sept in south India
                'east': 700,     # June-Sept in east India
                'west': 750      # June-Sept in west India
            },
            'rabi': {
                'north': 100,    # Oct-March in north
                'south': 200,    # Oct-March in south
                'east': 150,     # Oct-March in east
                'west': 50       # Oct-March in west
            },
            'zaid': {
                'north': 100,    # April-May
                'south': 150,    # April-May
                'east': 100,     # April-May
                'west': 50       # April-May
            }
        }
        
        # Determine region type
        region_type = 'north'
        if region.lower() in ['maharashtra', 'karnataka', 'tamil nadu', 'telangana']:
            region_type = 'south'
        elif region.lower() in ['odisha', 'bengal', 'bihar']:
            region_type = 'east'
        elif region.lower() in ['rajasthan', 'gujrat']:
            region_type = 'west'
        
        return rainfall_data.get(season.lower(), {}).get(region_type, 100)
    
    def _calculate_compatibility(
        self,
        water_availability: str,
        water_requirement: float,
        seasonal_rainfall: float
    ) -> float:
        """
        Calculate irrigation compatibility score (0-100).
        
        Args:
            water_availability: User's water availability level
            water_requirement: Crop's water requirement
            seasonal_rainfall: Natural rainfall for season
            
        Returns:
            float: Compatibility score
        """
        
        # Calculate water gap (deficit percentage)
        total_water = seasonal_rainfall
        water_gap = max(0, water_requirement - total_water)
        gap_percentage = (water_gap / water_requirement) * 100 if water_requirement > 0 else 0
        
        # Base score from rainfall coverage
        base_score = 100 - gap_percentage
        
        # Adjust based on water availability
        availability_bonus = {
            'high': 20,
            'medium': 10,
            'low': -20
        }.get(water_availability.lower(), 0)
        
        final_score = max(0, min(100, base_score + availability_bonus))
        return final_score
    
    def _categorize_compatibility(self, score: float) -> str:
        """
        Categorize compatibility level.
        
        Args:
            score: Compatibility score
            
        Returns:
            str: Compatibility level
        """
        if score >= 80:
            return 'Excellent'
        elif score >= 60:
            return 'Good'
        elif score >= 40:
            return 'Fair'
        else:
            return 'Poor'
    
    def _generate_irrigation_schedule(
        self,
        crop_id: str,
        season: str,
        daily_requirement: float,
        water_deficit: float,
        seasonal_rainfall: float
    ) -> List[Dict[str, Any]]:
        """
        Generate irrigation schedule for the season.
        
        Args:
            crop_id: Crop identifier
            season: Season name
            daily_requirement: Daily water requirement
            water_deficit: Water deficit for season
            seasonal_rainfall: Rainfall data
            
        Returns:
            list: Irrigation schedule by period
        """
        
        # Determine number of irrigation cycles
        if water_deficit <= 50:
            cycles = 2  # Light irrigation
        elif water_deficit <= 150:
            cycles = 4  # Moderate irrigation
        else:
            cycles = 6  # Heavy irrigation
        
        schedule = []
        for i in range(1, cycles + 1):
            cycle_percentage = (i / cycles) * 100
            schedule.append({
                'cycle': i,
                'timing': f'{int(cycle_percentage)}% through season',
                'amount_mm': round(daily_requirement * 30, 2),  # Monthly requirement
                'priority': 'High' if i <= 2 else 'Medium'
            })
        
        return schedule
    
    def _generate_advisory(
        self,
        crop_id: str,
        water_availability: str,
        seasonal_rainfall: float,
        water_deficit: float,
        compatibility: float
    ) -> str:
        """
        Generate water advisory message.
        
        Args:
            crop_id: Crop identifier
            water_availability: Water availability level
            seasonal_rainfall: Rainfall data
            water_deficit: Water deficit
            compatibility: Compatibility score
            
        Returns:
            str: Advisory message
        """
        
        if compatibility >= 80:
            return f"{crop_id.capitalize()} is well-suited for {water_availability} water availability. Natural rainfall should cover most water needs."
        elif compatibility >= 60:
            return f"{crop_id.capitalize()} can grow with {water_availability} water availability but requires supplemental irrigation. Plan for {int(water_deficit)}mm of irrigation."
        elif compatibility >= 40:
            return f"{crop_id.capitalize()} can be grown with careful water management. Plan for {int(water_deficit)}mm of irrigation and use water-saving techniques."
        else:
            return f"{crop_id.capitalize()} requires significant water management with {water_availability} availability. Consider drought-resistant alternatives or improving irrigation system."
    
    def _get_water_saving_tips(self, crop_id: str, season: str) -> List[str]:
        """
        Get water-saving tips for the crop and season.
        
        Args:
            crop_id: Crop identifier
            season: Season name
            
        Returns:
            list: Water-saving tips
        """
        
        tips = [
            'Use drip irrigation systems for 30-40% water savings',
            'Apply mulch to reduce soil evaporation',
            'Schedule irrigation during early morning to reduce water loss',
            'Monitor soil moisture before irrigation',
            'Maintain proper field leveling for even water distribution'
        ]
        
        # Crop-specific tips
        if crop_id.lower() == 'rice':
            tips.append('Practice alternate wetting and drying to save 20-25% water')
        elif crop_id.lower() == 'sugarcane':
            tips.append('Use drip irrigation - can save up to 50% water compared to flooding')
        elif crop_id.lower() == 'cotton':
            tips.append('Reduce irrigation frequency as cotton drought-tolerant crop')
        
        return tips
