"""
Disease Detection Service
Mock disease detection for crop diseases using image classification logic.
"""

from typing import Dict, List, Any
from services.data_loader import get_data_loader
import random


class DiseaseDetector:
    """Detects and provides advisory for crop diseases."""
    
    # Disease symptoms and recommendations by crop
    DISEASE_DATABASE = {
        'rice': [
            {
                'id': 'blast',
                'name': 'Leaf Blast',
                'symptoms': ['Gray-white lesions on leaf', 'Brown edges', 'Reduced photosynthesis'],
                'severity': 'High',
                'treatment': ['Apply Tricyclazole fungicide', 'Improve drainage', 'Avoid nitrogen excess'],
                'prevention': ['Use resistant varieties', 'Maintain field sanitation', 'Avoid dense planting']
            },
            {
                'id': 'sheath_blight',
                'name': 'Sheath Blight',
                'symptoms': ['Water-soaked lesions on sheath', 'Circular pattern', 'Yellowing around lesion'],
                'severity': 'Medium',
                'treatment': ['Apply Hexaconazole', 'Reduce humidity', 'Proper spacing'],
                'prevention': ['Use resistant varieties', 'Reduce nitrogen', 'Air circulation']
            }
        ],
        'wheat': [
            {
                'id': 'powdery_mildew',
                'name': 'Powdery Mildew',
                'symptoms': ['White powder on leaves', 'Leaf curl', 'Stunted growth'],
                'severity': 'Medium',
                'treatment': ['Sulfur spray', 'Improve air circulation', 'Reduce humidity'],
                'prevention': ['Select resistant varieties', 'Proper spacing', 'Avoid over-watering']
            },
            {
                'id': 'rust',
                'name': 'Rust (Leaf/Stripe/Stem)',
                'symptoms': ['Orange/brown pustules', 'Powdery appearance', 'Leaf drying'],
                'severity': 'High',
                'treatment': ['Apply Propiconazole', 'Remove infected leaves', 'Improve drainage'],
                'prevention': ['Use resistant varieties', 'Monitor field regularly', 'Early scouting']
            }
        ],
        'cotton': [
            {
                'id': 'leaf_curl',
                'name': 'Cotton Leaf Curl Virus',
                'symptoms': ['Leaf curling upward', 'Purple veins', 'Stunted growth'],
                'severity': 'High',
                'treatment': ['Control whitefly vectors', 'Rogue infected plants', 'Apply insecticide'],
                'prevention': ['Use resistant varieties', 'Control weeds', 'Control insect vectors']
            },
            {
                'id': 'boll_rot',
                'name': 'Boll Rot',
                'symptoms': ['Blackening of bolls', 'Decay inside', 'Lint quality reduction'],
                'severity': 'High',
                'treatment': ['Apply Copper fungicide', 'Remove affected bolls', 'Improve drainage'],
                'prevention': ['Reduce humidity', 'Prune lower branches', 'Adequate spacing']
            }
        ],
        'maize': [
            {
                'id': 'leaf_blight',
                'name': 'Northern Leaf Blight',
                'symptoms': ['Tan oval lesions', 'Parallel veins', 'Coalescence of lesions'],
                'severity': 'Medium',
                'treatment': ['Apply Mancozeb', 'Remove lower infected leaves', 'Improve air flow'],
                'prevention': ['Use resistant hybrids', 'Crop rotation', 'Sanitation']
            }
        ],
        'potato': [
            {
                'id': 'late_blight',
                'name': 'Late Blight',
                'symptoms': ['Water-soaked spots', 'White mold on underside', 'Rapid spread'],
                'severity': 'High',
                'treatment': ['Spray Mancozeb/Chlorothalonil', 'Remove affected plants', 'Reduce humidity'],
                'prevention': ['Use resistant varieties', 'Proper spacing', 'Destroy infected tubers']
            }
        ]
    }
    
    def __init__(self):
        """Initialize disease detector."""
        self.data_loader = get_data_loader()
    
    def detect_disease(
        self,
        crop_id: str,
        image_description: str
    ) -> Dict[str, Any]:
        """
        Detect disease from image description (mock detection).
        
        In production: Use ML model for image classification.
        
        Args:
            crop_id: Crop identifier
            image_description: Description of plant symptoms/appearance
            
        Returns:
            dict: Disease detection results with recommendations
        """
        
        # Get diseases for this crop
        crop_key = crop_id.lower()
        diseases = self.DISEASE_DATABASE.get(crop_key, [])
        
        if not diseases:
            return {
                'success': False,
                'error': f'Disease database not available for {crop_id}'
            }
        
        # Mock detection: randomly select a disease or healthy
        detection_result = self._mock_disease_detection(
            crop_id,
            image_description,
            diseases
        )
        
        return detection_result
    
    def get_disease_info(self, crop_id: str, disease_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific disease.
        
        Args:
            crop_id: Crop identifier
            disease_id: Disease identifier
            
        Returns:
            dict: Disease information
        """
        
        crop_key = crop_id.lower()
        diseases = self.DISEASE_DATABASE.get(crop_key, [])
        
        # Find disease
        disease = next((d for d in diseases if d['id'] == disease_id), None)
        
        if not disease:
            return {'success': False, 'error': 'Disease not found'}
        
        return {
            'success': True,
            'crop_id': crop_id,
            'disease': disease
        }
    
    def list_crop_diseases(self, crop_id: str) -> Dict[str, Any]:
        """
        List all known diseases for a crop.
        
        Args:
            crop_id: Crop identifier
            
        Returns:
            dict: List of diseases for the crop
        """
        
        crop_key = crop_id.lower()
        diseases = self.DISEASE_DATABASE.get(crop_key, [])
        
        if not diseases:
            return {
                'success': False,
                'error': f'No disease database for {crop_id}'
            }
        
        return {
            'success': True,
            'crop_id': crop_id,
            'diseases': [
                {
                    'id': d['id'],
                    'name': d['name'],
                    'severity': d['severity']
                }
                for d in diseases
            ],
            'total_diseases': len(diseases)
        }
    
    def _mock_disease_detection(
        self,
        crop_id: str,
        image_description: str,
        diseases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Mock disease detection based on description.
        
        In production: Use actual ML model.
        
        Args:
            crop_id: Crop identifier
            image_description: Plant description
            diseases: Available diseases for crop
            
        Returns:
            dict: Detection result
        """
        
        description_lower = image_description.lower()
        
        # Check keywords against symptoms
        best_match = None
        best_score = 0
        
        for disease in diseases:
            symptom_matches = 0
            for symptom in disease['symptoms']:
                if any(keyword in description_lower for keyword in symptom.lower().split()):
                    symptom_matches += 1
            
            disease_score = (symptom_matches / len(disease['symptoms'])) * 100
            
            if disease_score > best_score:
                best_score = disease_score
                best_match = disease
        
        # If good match found, return disease info
        if best_match and best_score > 30:
            confidence = min(95, 50 + best_score)
            return {
                'success': True,
                'crop_id': crop_id,
                'detected': True,
                'disease': {
                    'id': best_match['id'],
                    'name': best_match['name'],
                    'severity': best_match['severity'],
                    'confidence': round(confidence, 1),
                    'symptoms': best_match['symptoms'],
                    'treatment': best_match['treatment'],
                    'prevention': best_match['prevention']
                },
                'message': f"Disease detected: {best_match['name']} (Confidence: {round(confidence, 1)}%)"
            }
        
        # No disease detected
        return {
            'success': True,
            'crop_id': crop_id,
            'detected': False,
            'message': f"{crop_id.capitalize()} appears healthy! No major disease detected.",
            'advice': [
                'Continue regular monitoring',
                'Maintain proper field hygiene',
                'Use preventive sprays as recommended',
                'Scout field at least twice weekly'
            ]
        }
    
    def get_management_plan(self, crop_id: str, disease_id: str) -> Dict[str, Any]:
        """
        Get integrated disease management plan.
        
        Args:
            crop_id: Crop identifier
            disease_id: Disease identifier
            
        Returns:
            dict: Integrated management plan
        """
        
        crop_key = crop_id.lower()
        diseases = self.DISEASE_DATABASE.get(crop_key, [])
        disease = next((d for d in diseases if d['id'] == disease_id), None)
        
        if not disease:
            return {'success': False, 'error': 'Disease not found'}
        
        return {
            'success': True,
            'crop_id': crop_id,
            'disease_name': disease['name'],
            'management_plan': {
                'immediate_actions': [
                    f"Scout field and identify affected plants",
                    f"Isolate severely infected plants (rogue)",
                    f"Apply recommended fungicide: {disease['treatment'][0]}"
                ],
                'ongoing_care': disease['treatment'],
                'preventive_measures': disease['prevention'],
                'monitoring_schedule': [
                    'Daily visual inspection',
                    'Monitor weather (humidity/rainfall)',
                    'Document disease progression',
                    'Keep treatment records'
                ],
                'cost_estimate': {
                    'fungicide_cost': '₹500-800 per acre',
                    'labor_cost': '₹200-500 per acre',
                    'total_estimated': '₹700-1300 per acre'
                }
            }
        }
