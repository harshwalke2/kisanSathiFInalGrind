"""
Crop Rotation Advisor Service
Provides crop rotation recommendations for soil health and productivity.
"""

from typing import Dict, List, Any
from services.data_loader import get_data_loader


class CropRotationAdvisor:
    """Recommends suitable crop rotations."""
    
    # Crop rotation compatibility matrix
    # Higher score = better combination
    ROTATION_MATRIX = {
        'rice': {
            'wheat': 90,      # Excellent rotation
            'potato': 85,     # Good
            'onion': 80,
            'groundnut': 70,
            'maize': 65,
            'cotton': 50,     # Poor compatibility
            'sugarcane': 40
        },
        'wheat': {
            'rice': 90,
            'maize': 85,
            'cotton': 80,
            'potato': 75,
            'onion': 75,
            'groundnut': 80,
            'sugarcane': 45
        },
        'cotton': {
            'wheat': 80,
            'potato': 85,
            'groundnut': 75,
            'maize': 70,
            'rice': 50,
            'sugarcane': 40,
            'onion': 60
        },
        'sugarcane': {
            'groundnut': 85,
            'wheat': 45,
            'rice': 40,
            'cotton': 40,
            'potato': 50,
            'maize': 55,
            'onion': 60
        },
        'maize': {
            'wheat': 85,
            'groundnut': 80,
            'cotton': 70,
            'potato': 75,
            'rice': 65,
            'sugarcane': 55,
            'onion': 70
        },
        'groundnut': {
            'wheat': 80,
            'rice': 70,
            'sugarcane': 85,
            'cotton': 75,
            'potato': 80,
            'maize': 80,
            'onion': 60
        },
        'potato': {
            'cotton': 85,
            'rice': 85,
            'groundnut': 80,
            'wheat': 75,
            'maize': 75,
            'onion': 70,
            'sugarcane': 50
        },
        'onion': {
            'groundnut': 60,
            'rice': 80,
            'wheat': 75,
            'cotton': 60,
            'potato': 70,
            'maize': 70,
            'sugarcane': 60
        },
        'tomato': {
            'wheat': 75,
            'groundnut': 75,
            'onion': 65,
            'potato': 70,
            'rice': 60,
            'cotton': 50,
            'sugarcane': 40,
            'maize': 70
        },
        'soybean': {
            'wheat': 85,
            'groundnut': 80,
            'rice': 70,
            'cotton': 75,
            'potato': 75,
            'maize': 80,
            'onion': 65,
            'sugarcane': 50
        }
    }
    
    # Soil nutrient profiles for crops
    SOIL_PROFILES = {
        'rice': {'nitrogen_drain': 'High', 'phosphorus_drain': 'Medium', 'potash_drain': 'High'},
        'wheat': {'nitrogen_drain': 'High', 'phosphorus_drain': 'High', 'potash_drain': 'Medium'},
        'cotton': {'nitrogen_drain': 'High', 'phosphorus_drain': 'High', 'potash_drain': 'High'},
        'sugarcane': {'nitrogen_drain': 'Very High', 'phosphorus_drain': 'High', 'potash_drain': 'High'},
        'maize': {'nitrogen_drain': 'Very High', 'phosphorus_drain': 'Medium', 'potash_drain': 'Medium'},
        'groundnut': {'nitrogen_drain': 'Low', 'phosphorus_drain': 'Medium', 'potash_drain': 'Medium'},
        'potato': {'nitrogen_drain': 'Medium', 'phosphorus_drain': 'High', 'potash_drain': 'High'},
        'onion': {'nitrogen_drain': 'Medium', 'phosphorus_drain': 'Medium', 'potash_drain': 'Medium'},
        'tomato': {'nitrogen_drain': 'Medium', 'phosphorus_drain': 'High', 'potash_drain': 'High'},
        'soybean': {'nitrogen_drain': 'Low', 'phosphorus_drain': 'Medium', 'potash_drain': 'Medium'}
    }
    
    def __init__(self):
        """Initialize crop rotation advisor."""
        self.data_loader = get_data_loader()
    
    def recommend_rotation(
        self,
        current_crop: str,
        next_season_available: bool = True
    ) -> Dict[str, Any]:
        """
        Recommend rotation for current crop.
        
        Args:
            current_crop: Currently grown crop
            next_season_available: Whether next season is available
            
        Returns:
            dict: Rotation recommendations with rationale
        """
        
        crop_key = current_crop.lower()
        
        if crop_key not in self.ROTATION_MATRIX:
            return {
                'success': False,
                'error': f'Rotation data not available for {current_crop}'
            }
        
        # Get compatibility scores
        compatibility = self.ROTATION_MATRIX.get(crop_key, {})
        
        # Rank options
        ranked_crops = sorted(
            compatibility.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Build recommendations
        recommendations = []
        for crop, score in ranked_crops[:3]:
            recommendations.append({
                'crop': crop.capitalize(),
                'compatibility_score': score,
                'level': self._score_to_level(score),
                'reason': self._get_rotation_reason(crop_key, crop)
            })
        
        return {
            'success': True,
            'current_crop': current_crop.capitalize(),
            'next_season_available': next_season_available,
            'recommendations': recommendations,
            'soil_impact': self._analyze_soil_impact(crop_key),
            'best_practice': self._get_best_practice(crop_key),
            'next_steps': [
                'Choose rotation crop based on market demand',
                'Prepare soil after harvest',
                'Apply recommended fertilizers',
                'Plan pest management for new crop'
            ]
        }
    
    def plan_3_year_rotation(self, initial_crop: str) -> Dict[str, Any]:
        """
        Plan a complete 3-year rotation cycle.
        
        Args:
            initial_crop: Starting crop
            
        Returns:
            dict: 3-year rotation plan
        """
        
        crop_key = initial_crop.lower()
        
        if crop_key not in self.ROTATION_MATRIX:
            return {
                'success': False,
                'error': f'Rotation plan not available for {initial_crop}'
            }
        
        # Year 1: Current crop
        year1_crop = initial_crop.capitalize()
        
        # Year 2: Best rotation option
        year2_options = self.ROTATION_MATRIX.get(crop_key, {})
        year2_crop = max(year2_options.items(), key=lambda x: x[1])[0].capitalize()
        
        # Year 3: Rotation from year 2 crop
        year3_options = self.ROTATION_MATRIX.get(year2_crop.lower(), {})
        year3_crop = max(year3_options.items(), key=lambda x: x[1])[0].capitalize()
        
        # Calculate soil health progression
        soil_progression = self._calculate_soil_progression([
            crop_key,
            year2_crop.lower(),
            year3_crop.lower()
        ])
        
        return {
            'success': True,
            'rotation_plan': [
                {
                    'year': 1,
                    'crop': year1_crop,
                    'season': 'Current',
                    'expected_yield': 'Normal',
                    'soil_status': 'Current'
                },
                {
                    'year': 2,
                    'crop': year2_crop,
                    'season': 'Next',
                    'expected_yield': 'Good',
                    'soil_status': 'Improving'
                },
                {
                    'year': 3,
                    'crop': year3_crop,
                    'season': 'After Next',
                    'expected_yield': 'Excellent',
                    'soil_status': 'Healthy'
                }
            ],
            'expected_benefits': [
                'Soil nitrogen restoration (via legumes if included)',
                'Reduced pest and disease buildup',
                'Better soil structure and moisture',
                'Improved productivity over time',
                'Risk diversification'
            ],
            'soil_health_improvement': soil_progression
        }
    
    def analyze_soil_health(self, current_crop: str, previous_crops: List[str]) -> Dict[str, Any]:
        """
        Analyze soil health based on cropping history.
        
        Args:
            current_crop: Current crop
            previous_crops: List of previously grown crops
            
        Returns:
            dict: Soil health analysis
        """
        
        # Analyze nutrient drain
        total_nitrogen_drain = 0
        total_phosphorus_drain = 0
        total_potash_drain = 0
        
        for crop in previous_crops + [current_crop]:
            crop_key = crop.lower()
            if crop_key in self.SOIL_PROFILES:
                profile = self.SOIL_PROFILES[crop_key]
                
                # Convert drain levels to numeric
                drain_mapping = {'Low': 1, 'Medium': 2, 'High': 3, 'Very High': 4}
                total_nitrogen_drain += drain_mapping.get(profile['nitrogen_drain'], 2)
                total_phosphorus_drain += drain_mapping.get(profile['phosphorus_drain'], 2)
                total_potash_drain += drain_mapping.get(profile['potash_drain'], 2)
        
        # Calculate averages
        num_crops = len(previous_crops) + 1
        nitrogen_level = total_nitrogen_drain / num_crops
        phosphorus_level = total_phosphorus_drain / num_crops
        potash_level = total_potash_drain / num_crops
        
        return {
            'success': True,
            'current_crop': current_crop.capitalize(),
            'cropping_history': previous_crops,
            'nutrient_depletion': {
                'nitrogen': self._level_to_status(nitrogen_level),
                'phosphorus': self._level_to_status(phosphorus_level),
                'potash': self._level_to_status(potash_level)
            },
            'recommendations': self._get_soil_recommendations(
                nitrogen_level,
                phosphorus_level,
                potash_level
            ),
            'suggested_actions': [
                'Get soil test done before next planting',
                'Apply recommended fertilizers',
                'Consider legume crop in rotation',
                'Use organic manure/compost'
            ]
        }
    
    def _score_to_level(self, score: int) -> str:
        """Convert score to compatibility level."""
        if score >= 80:
            return 'Excellent'
        elif score >= 70:
            return 'Good'
        elif score >= 50:
            return 'Fair'
        else:
            return 'Poor'
    
    def _get_rotation_reason(self, current: str, next_crop: str) -> str:
        """Get reason for rotation recommendation."""
        
        # Check if legume rotation
        legumes = ['groundnut', 'soybean']
        if current not in legumes and next_crop in legumes:
            return 'Nitrogen restoration legume'
        
        # Check nutrient complementarity
        current_profile = self.SOIL_PROFILES.get(current, {})
        next_profile = self.SOIL_PROFILES.get(next_crop, {})
        
        if current_profile.get('nitrogen_drain') == 'Very High':
            return 'Follows high nitrogen consumer'
        
        return 'Breaks pest/disease cycle and restores soil balance'
    
    def _analyze_soil_impact(self, crop: str) -> Dict[str, str]:
        """Analyze how current crop impacts soil."""
        
        profile = self.SOIL_PROFILES.get(crop, {})
        
        return {
            'nitrogen_impact': f"Drains {profile.get('nitrogen_drain', 'Medium')} nitrogen",
            'phosphorus_impact': f"Drains {profile.get('phosphorus_drain', 'Medium')} phosphorus",
            'potash_impact': f"Drains {profile.get('potash_drain', 'Medium')} potash"
        }
    
    def _get_best_practice(self, crop: str) -> str:
        """Get best practice for crop."""
        
        practices = {
            'rice': 'Include legume crop in rotation. Keep field fallow or green manure.',
            'wheat': 'Alternate with legume. Apply balanced fertilizer.',
            'cotton': 'Must rotate with non-cotton crop. Riskseed quality',
            'sugarcane': 'Plant legume after sugarcane to restore nitrogen.',
            'maize': 'Alternate with legume or potato. Use crop residue composting.',
            'groundnut': 'Good nitrogen fixer. Follow with nitrogen-hungry crop.',
            'potato': 'Rotate with cereal crop. Avoid 2 years in succession.',
            'onion': 'Include legume in rotation. Monitor soil pH.',
            'tomato': 'Rotate family crops. Include green manure crop.',
            'soybean': 'Nitrogen fixer. Suitable in rotation with cereals.'
        }
        
        return practices.get(crop, 'Follow state agriculture department recommendations.')
    
    def _calculate_soil_progression(self, crops: List[str]) -> str:
        """Calculate soil health progression across years."""
        
        # Simple scoring: legume = +2, cereals/others = -1
        score = 0
        for crop in crops:
            if crop in ['groundnut', 'soybean']:
                score += 2
            elif crop in ['rice', 'wheat', 'maize']:
                score -= 1
            else:
                score -= 0.5
        
        if score > 2:
            return 'Excellent soil health recovery expected'
        elif score > 0:
            return 'Good soil health improvement expected'
        else:
            return 'Soil management recommended'
    
    def _level_to_status(self, level: float) -> str:
        """Convert numeric level to status."""
        if level >= 3.5:
            return 'Very Depleted'
        elif level >= 2.5:
            return 'Depleted'
        elif level >= 1.5:
            return 'Moderate'
        else:
            return 'Adequate'
    
    def _get_soil_recommendations(self, n, p, k) -> List[str]:
        """Get fertilizer recommendations based on depletion."""
        
        recommendations = []
        
        if n > 2.5:
            recommendations.append('High nitrogen content fertilizer recommended')
        if p > 2.5:
            recommendations.append('Phosphate-rich fertilizer needed')
        if k > 2.5:
            recommendations.append('Potassium supplementation required')
        
        if len(recommendations) == 0:
            recommendations.append('Normal maintenance fertilizer sufficient')
        
        return recommendations
