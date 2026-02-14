"""
Scheme Recommender Service
Recommends government schemes and subsidies for farmers.
"""

from typing import Dict, List, Any
from services.data_loader import get_data_loader


class SchemeRecommender:
    """Recommends government schemes and subsidies."""
    
    # Government schemes database
    SCHEMES_DATABASE = [
        {
            'id': 'pmnsy',
            'name': 'Pradhan Mantri Kisan SammanNidhi Yojana (PM-KISAN)',
            'category': 'Income Support',
            'description': 'Direct income support to farmers',
            'eligibility': ['All farmers'],
            'benefit': '₹6000 per year in 3 installments',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://pmkisan.gov.in/',
            'priority': 'High'
        },
        {
            'id': 'pmfby',
            'name': 'Pradhan Mantri Fasal Bima Yojana (PM-FBY)',
            'category': 'Crop Insurance',
            'description': 'Crop insurance for yield loss and damage',
            'eligibility': ['All farmers practicing agriculture'],
            'benefit': 'Insurance coverage up to 200% of premium',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://pmfby.gov.in/',
            'priority': 'High'
        },
        {
            'id': 'krishi_sinchayee',
            'name': 'Accelerated Irrigation Benefits Programme (AIBP)',
            'category': 'Irrigation',
            'description': 'Subsidies for irrigation infrastructure',
            'eligibility': ['Farmers in notified shallow/deep water zones'],
            'benefit': 'Subsidy up to 50% for irrigation systems',
            'regions': ['All States'],
            'crops': ['Sugarcane', 'Cotton', 'Rice'],
            'url': 'https://aibp.gov.in/',
            'priority': 'High'
        },
        {
            'id': 'soil_health',
            'name': 'Soil Health Card Scheme',
            'category': 'Soil Management',
            'description': 'Free soil testing and nutrient recommendations',
            'eligibility': ['All farmers'],
            'benefit': 'Free soil testing + customized recommendations',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://soilhealth.dac.gov.in/',
            'priority': 'Medium'
        },
        {
            'id': 'paramparagat',
            'name': 'Paramparagat Krishi Vikas Yojana (PKVY)',
            'category': 'Organic Farming',
            'description': 'Subsidies for organic farming adoption',
            'eligibility': ['Farmers willing to adopt organic farming'],
            'benefit': '₹500/acre for inputs, ₹50-83/acre premium for products',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://pkvy.gov.in/',
            'priority': 'Medium'
        },
        {
            'id': 'kisan_credit',
            'name': 'Kisan Credit Card (KCC)',
            'category': 'Credit',
            'description': 'Flexible credit for agricultural needs',
            'eligibility': ['All farmers'],
            'benefit': 'Low-interest credit up to ₹2 lakhs',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://agricredit.gov.in/',
            'priority': 'High'
        },
        {
            'id': 'subsidy_seeds',
            'name': 'Seed Subsidy Scheme',
            'category': 'Input Subsidy',
            'description': 'Subsidized certified seeds',
            'eligibility': ['All farmers'],
            'benefit': '30-50% subsidy on certified seeds',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://seedsubsidy.gov.in/',
            'priority': 'Medium'
        },
        {
            'id': 'subsidy_fertilizer',
            'name': 'Fertilizer Subsidy Scheme',
            'category': 'Input Subsidy',
            'description': 'Subsidized fertilizers through PDS',
            'eligibility': ['All farmers'],
            'benefit': 'Subsidized rates for urea, phosphate, potash',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://ifcl.gov.in/',
            'priority': 'High'
        },
        {
            'id': 'atmanirbhar_krishi',
            'name': 'Atmanirbhar Krishi Scheme',
            'category': 'Agricultural Equipment',
            'description': 'Subsidies for modern farm equipment',
            'eligibility': ['All farmers'],
            'benefit': '40-50% subsidy on equipment',
            'regions': ['All States'],
            'crops': ['All crops'],
            'url': 'https://atmanirbharkrishi.gov.in/',
            'priority': 'Medium'
        },
        {
            'id': 'dbt_farmer_crop',
            'name': 'Direct Benefit Transfer Scheme',
            'category': 'Income Support',
            'description': 'State-level crop support schemes',
            'eligibility': ['Varies by state'],
            'benefit': 'Direct cash transfer (₹500-2000/acre)',
            'regions': ['All States'],
            'crops': ['State-specific'],
            'url': 'https://dbt.gov.in/',
            'priority': 'High'
        }
    ]
    
    def __init__(self):
        """Initialize scheme recommender."""
        self.data_loader = get_data_loader()
    
    def recommend_schemes(
        self,
        crop_id: str,
        region: str,
        farm_size: str = 'small'
    ) -> Dict[str, Any]:
        """
        Recommend schemes for a farmer's profile.
        
        Args:
            crop_id: Crop identifier
            region: Region/state name
            farm_size: Farm size category (small/medium/large)
            
        Returns:
            dict: Recommended schemes
        """
        
        # Filter schemes applicable to crop and region
        applicable_schemes = self._filter_schemes(crop_id, region)
        
        # Rank by priority and relevance
        ranked_schemes = self._rank_schemes(applicable_schemes, crop_id, farm_size)
        
        # Format response
        return {
            'success': True,
            'crop_id': crop_id,
            'region': region,
            'farm_size': farm_size,
            'total_schemes': len(ranked_schemes),
            'recommended_schemes': ranked_schemes,
            'estimated_benefit': self._calculate_total_benefit(ranked_schemes, farm_size),
            'next_steps': [
                'Visit nearest agriculture office',
                'Collect required documents',
                'Apply for schemes online or offline',
                'Monitor application status'
            ]
        }
    
    def get_scheme_details(self, scheme_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a scheme.
        
        Args:
            scheme_id: Scheme identifier
            
        Returns:
            dict: Scheme details
        """
        
        scheme = next((s for s in self.SCHEMES_DATABASE if s['id'] == scheme_id), None)
        
        if not scheme:
            return {'success': False, 'error': 'Scheme not found'}
        
        # Add application details
        scheme_with_details = {
            **scheme,
            'application_process': self._get_application_process(scheme_id),
            'documents_required': self._get_required_documents(scheme_id),
            'important_dates': self._get_important_dates(scheme_id)
        }
        
        return {
            'success': True,
            'scheme': scheme_with_details
        }
    
    def search_schemes(self, keyword: str) -> Dict[str, Any]:
        """
        Search schemes by keyword.
        
        Args:
            keyword: Search keyword
            
        Returns:
            dict: Search results
        """
        
        keyword_lower = keyword.lower()
        results = [
            s for s in self.SCHEMES_DATABASE
            if keyword_lower in s['name'].lower() or 
               keyword_lower in s['description'].lower() or
               keyword_lower in s['category'].lower()
        ]
        
        return {
            'success': True,
            'query': keyword,
            'results_count': len(results),
            'schemes': results
        }
    
    def _filter_schemes(self, crop_id: str, region: str) -> List[Dict[str, Any]]:
        """
        Filter schemes applicable to crop and region.
        
        Args:
            crop_id: Crop identifier
            region: Region name
            
        Returns:
            list: Filtered schemes
        """
        
        crop_name = crop_id.capitalize()
        
        applicable = []
        for scheme in self.SCHEMES_DATABASE:
            # Check crop eligibility
            crop_eligible = (
                'All crops' in scheme['crops'] or
                crop_name in scheme['crops'] or
                crop_id.lower() in [c.lower() for c in scheme['crops']]
            )
            
            # Check regional eligibility
            region_eligible = (
                'All States' in scheme['regions'] or
                region in scheme['regions']
            )
            
            if crop_eligible and region_eligible:
                applicable.append(scheme)
        
        return applicable
    
    def _rank_schemes(
        self,
        schemes: List[Dict[str, Any]],
        crop_id: str,
        farm_size: str
    ) -> List[Dict[str, Any]]:
        """
        Rank schemes by priority and relevance.
        
        Args:
            schemes: List of schemes
            crop_id: Crop identifier
            farm_size: Farm size
            
        Returns:
            list: Ranked schemes
        """
        
        # Sort by priority
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        
        ranked = sorted(
            schemes,
            key=lambda s: (priority_order.get(s['priority'], 3), s['name'])
        )
        
        # Limit to top 5 most relevant
        return ranked[:5]
    
    def _calculate_total_benefit(
        self,
        schemes: List[Dict[str, Any]],
        farm_size: str
    ) -> Dict[str, Any]:
        """
        Estimate total benefit from schemes.
        
        Args:
            schemes: List of schemes
            farm_size: Farm size
            
        Returns:
            dict: Benefit estimates
        """
        
        farm_size_acres = {
            'small': 2.5,
            'medium': 5,
            'large': 10
        }.get(farm_size.lower(), 2.5)
        
        return {
            'farm_size_acres': farm_size_acres,
            'estimated_annual_benefit': f"₹{int(6000 + 1000 * farm_size_acres*2)}-15000",
            'note': 'Actual benefit depends on scheme-specific terms and conditions'
        }
    
    def _get_application_process(self, scheme_id: str) -> List[str]:
        """Get application process for a scheme."""
        
        # Generic process - customize as needed
        return [
            '1. Check eligibility on official website',
            '2. Gather required documents',
            '3. Visit agriculture office or apply online',
            '4. Submit application with documents',
            '5. Verification and approval process',
            '6. Benefit transfer to registered bank account'
        ]
    
    def _get_required_documents(self, scheme_id: str) -> List[str]:
        """Get required documents for a scheme."""
        
        # Common documents - vary by scheme
        return [
            'Aadhaar card',
            'Land ownership documents/lease deed',
            'Bank account details',
            'Mobile number',
            'Crop details (variety, area, etc.)'
        ]
    
    def _get_important_dates(self, scheme_id: str) -> Dict[str, str]:
        """Get important dates for a scheme."""
        
        return {
            'application_deadline': 'Ongoing/Announced annually',
            'verification_period': '30-45 days',
            'benefit_disbursement': 'Within 60-90 days of approval'
        }
