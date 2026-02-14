"""
Recommendation API Routes
Handles crop recommendation requests from the frontend.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from services.scoring_engine import ScoringEngine
from services.data_loader import get_data_loader
from services.price_analyzer import PriceTrendAnalyzer
from services.water_advisory import WaterAdvisory
from services.disease_detector import DiseaseDetector
from services.scheme_recommender import SchemeRecommender
from services.crop_rotator import CropRotationAdvisor
from services.export_opportunity import ExportOpportunityIndicator

# Create blueprint for recommendation routes
recommendation_bp = Blueprint('recommendation', __name__, url_prefix='/api')

# Initialize services
scoring_engine = ScoringEngine()
data_loader = get_data_loader()
price_analyzer = PriceTrendAnalyzer()
water_advisor = WaterAdvisory()
disease_detector = DiseaseDetector()
scheme_recommender = SchemeRecommender()
crop_rotator = CropRotationAdvisor()
export_indicator = ExportOpportunityIndicator()


@recommendation_bp.route('/recommend', methods=['POST'])
def get_recommendations():
    """
    Main recommendation endpoint.
    
    Request JSON format:
    {
        "location": "Nashik",
        "season": "Kharif",
        "water_availability": "High",
        "risk_preference": "balanced",
        "top_n": 3
    }
    
    Response JSON format:
    {
        "success": true,
        "data": [
            {
                "crop_id": "rice",
                "crop_name": "Rice",
                "final_score": 85.5,
                "risk": {...},
                "profit_estimate": {...},
                "demand": {...},
                "explanation": "..."
            }
        ],
        "metadata": {
            "location": "Nashik",
            "season": "Kharif",
            "water_availability": "High",
            "risk_preference": "balanced"
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['location', 'season', 'water_availability']
        missing = [f for f in required_fields if f not in data]
        
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}',
                'code': 'INVALID_INPUT'
            }), 400
        
        location = data.get('location', '').strip()
        season = data.get('season', '').strip()
        water_availability = data.get('water_availability', '').strip()
        risk_preference = data.get('risk_preference', 'balanced').strip().lower()
        top_n = data.get('top_n', 3)
        
        # Validate season
        valid_seasons = ['Kharif', 'Rabi', 'Zaid']
        if season not in valid_seasons:
            return jsonify({
                'success': False,
                'error': f'Invalid season. Must be one of: {", ".join(valid_seasons)}',
                'code': 'INVALID_SEASON'
            }), 400
        
        # Validate water availability
        valid_water = ['Low', 'Medium', 'High']
        if water_availability not in valid_water:
            return jsonify({
                'success': False,
                'error': f'Invalid water availability. Must be one of: {", ".join(valid_water)}',
                'code': 'INVALID_WATER'
            }), 400
        
        # Validate risk preference
        valid_risk_preferences = ['conservative', 'balanced', 'aggressive']
        if risk_preference not in valid_risk_preferences:
            return jsonify({
                'success': False,
                'error': f'Invalid risk preference. Must be one of: {", ".join(valid_risk_preferences)}',
                'code': 'INVALID_RISK_PREFERENCE'
            }), 400
        
        # Validate location
        if not data_loader.validate_location(location):
            available = data_loader.get_available_regions()
            return jsonify({
                'success': False,
                'error': f'Location "{location}" not found',
                'available_locations': available,
                'code': 'INVALID_LOCATION'
            }), 400
        
        # Get recommendations with risk preference
        recommendations = scoring_engine.recommend(
            location=location,
            season=season,
            water_availability=water_availability,
            top_n=top_n,
            risk_preference=risk_preference
        )
        
        # Success response
        return jsonify({
            'success': True,
            'data': recommendations,
            'metadata': {
                'location': location,
                'season': season,
                'water_availability': water_availability,
                'risk_preference': risk_preference,
                'recommendation_count': len(recommendations)
            }
        }), 200
    
    except ValueError as e:
        # Handle known validation errors
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    
    except Exception as e:
        # Handle unexpected errors
        print(f"Recommendation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'code': 'SERVER_ERROR'
        }), 500


@recommendation_bp.route('/locations', methods=['GET'])
def get_available_locations():
    """
    Get list of available locations/regions.
    
    Response format:
    {
        "success": true,
        "locations": ["Nashik", "Aurangabad", "Kolhapur", ...]
    }
    """
    try:
        locations = data_loader.get_available_regions()
        return jsonify({
            'success': True,
            'locations': sorted(locations)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/crops', methods=['GET'])
def get_all_crops():
    """
    Get all available crops in database.
    
    Response format:
    {
        "success": true,
        "crops": [
            {
                "id": "rice",
                "name": "Rice",
                "hindi_name": "चावल",
                "season": "Kharif",
                ...
            }
        ]
    }
    """
    try:
        crops = data_loader.get_all_crops()
        return jsonify({
            'success': True,
            'crops': crops
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/crops/season/<season>', methods=['GET'])
def get_crops_by_season(season: str):
    """
    Get crops available for a specific season.
    
    URL parameters:
    - season: Kharif, Rabi, or Zaid
    
    Response format:
    {
        "success": true,
        "season": "Kharif",
        "crops": [...]
    }
    """
    try:
        valid_seasons = ['Kharif', 'Rabi', 'Zaid']
        
        if season not in valid_seasons:
            return jsonify({
                'success': False,
                'error': f'Invalid season. Must be one of: {", ".join(valid_seasons)}'
            }), 400
        
        crops = data_loader.get_crops_by_season(season)
        
        return jsonify({
            'success': True,
            'season': season,
            'crops': crops
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/price-trend', methods=['POST'])
def get_price_trend():
    """
    Get price trend analysis for a crop.
    
    Request JSON:
    {
        "crop_id": "rice",
        "region": "Nashik"
    }
    """
    try:
        data = request.get_json()
        crop_id = data.get('crop_id', '').strip()
        region = data.get('region', '').strip()
        
        if not crop_id or not region:
            return jsonify({
                'success': False,
                'error': 'crop_id and region are required'
            }), 400
        
        result = price_analyzer.get_price_trend(crop_id, region)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/water-advisory', methods=['POST'])
def get_water_advisory():
    """
    Get water and irrigation advisory for a crop.
    
    Request JSON:
    {
        "crop_id": "rice",
        "region": "Nashik",
        "season": "Kharif",
        "water_availability": "Medium"
    }
    """
    try:
        data = request.get_json()
        crop_id = data.get('crop_id', '').strip()
        region = data.get('region', '').strip()
        season = data.get('season', '').strip()
        water_availability = data.get('water_availability', '').strip()
        
        required = ['crop_id', 'region', 'season', 'water_availability']
        if not all(data.get(r, '').strip() for r in required):
            return jsonify({
                'success': False,
                'error': f'All fields required: {", ".join(required)}'
            }), 400
        
        result = water_advisor.get_water_advisory(crop_id, region, season, water_availability)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/disease-detect', methods=['POST'])
def detect_disease():
    """
    Detect disease from image description.
    
    Request JSON:
    {
        "crop_id": "rice",
        "image_description": "White spots on leaves, circular pattern"
    }
    """
    try:
        data = request.get_json()
        crop_id = data.get('crop_id', '').strip()
        image_description = data.get('image_description', '').strip()
        
        if not crop_id or not image_description:
            return jsonify({
                'success': False,
                'error': 'crop_id and image_description are required'
            }), 400
        
        result = disease_detector.detect_disease(crop_id, image_description)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/disease-info/<crop_id>/<disease_id>', methods=['GET'])
def get_disease_info(crop_id, disease_id):
    """Get detailed disease information."""
    try:
        result = disease_detector.get_disease_info(crop_id, disease_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/disease-list/<crop_id>', methods=['GET'])
def list_crop_diseases(crop_id):
    """List all diseases for a crop."""
    try:
        result = disease_detector.list_crop_diseases(crop_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/schemes', methods=['POST'])
def recommend_schemes():
    """
    Recommend government schemes for farmer.
    
    Request JSON:
    {
        "crop_id": "rice",
        "region": "Maharashtra",
        "farm_size": "small"
    }
    """
    try:
        data = request.get_json()
        crop_id = data.get('crop_id', '').strip()
        region = data.get('region', '').strip()
        farm_size = data.get('farm_size', 'small').strip()
        
        if not crop_id or not region:
            return jsonify({
                'success': False,
                'error': 'crop_id and region are required'
            }), 400
        
        result = scheme_recommender.recommend_schemes(crop_id, region, farm_size)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/scheme-details/<scheme_id>', methods=['GET'])
def get_scheme_details(scheme_id):
    """Get detailed scheme information."""
    try:
        result = scheme_recommender.get_scheme_details(scheme_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/crop-rotation', methods=['POST'])
def get_crop_rotation():
    """
    Get crop rotation recommendations.
    
    Request JSON:
    {
        "current_crop": "rice"
    }
    """
    try:
        data = request.get_json()
        current_crop = data.get('current_crop', '').strip()
        
        if not current_crop:
            return jsonify({
                'success': False,
                'error': 'current_crop is required'
            }), 400
        
        result = crop_rotator.recommend_rotation(current_crop)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/crop-rotation-plan', methods=['POST'])
def get_rotation_plan():
    """
    Get 3-year crop rotation plan.
    
    Request JSON:
    {
        "initial_crop": "rice"
    }
    """
    try:
        data = request.get_json()
        initial_crop = data.get('initial_crop', '').strip()
        
        if not initial_crop:
            return jsonify({
                'success': False,
                'error': 'initial_crop is required'
            }), 400
        
        result = crop_rotator.plan_3_year_rotation(initial_crop)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/export-potential', methods=['POST'])
def assess_export_potential():
    """
    Assess export potential for a crop.
    
    Request JSON:
    {
        "crop_id": "rice"
    }
    """
    try:
        data = request.get_json()
        crop_id = data.get('crop_id', '').strip()
        
        if not crop_id:
            return jsonify({
                'success': False,
                'error': 'crop_id is required'
            }), 400
        
        result = export_indicator.assess_export_potential(crop_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/export-certifications/<destination>', methods=['GET'])
def get_export_certifications(destination):
    """Get certification requirements for export destination."""
    try:
        result = export_indicator.get_certification_requirements(destination)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/export-comparison', methods=['POST'])
def compare_prices():
    """
    Compare domestic vs export prices.
    
    Request JSON:
    {
        "crop_id": "rice",
        "domestic_price": 2500
    }
    """
    try:
        data = request.get_json()
        crop_id = data.get('crop_id', '').strip()
        domestic_price = data.get('domestic_price', 0)
        
        if not crop_id or domestic_price <= 0:
            return jsonify({
                'success': False,
                'error': 'crop_id and valid domestic_price are required'
            }), 400
        
        result = export_indicator.compare_domestic_vs_export(crop_id, domestic_price)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@recommendation_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    
    Response:
    {
        "status": "healthy",
        "timestamp": "2026-02-14T10:30:00Z"
    }
    """
    from datetime import datetime
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200
