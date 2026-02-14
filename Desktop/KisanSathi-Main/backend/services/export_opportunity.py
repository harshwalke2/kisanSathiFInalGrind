"""
Export Opportunity Indicator Service
Identifies export opportunities and global demand for crops.
"""

from typing import Dict, List, Any
from services.data_loader import get_data_loader
from datetime import datetime


class ExportOpportunityIndicator:
    """Identifies export market opportunities for crops."""
    
    # Global export demand by crop (mock data based on real trends)
    EXPORT_DEMAND = {
        'rice': {
            'demand_level': 'Very High',
            'growth_rate': 3.2,  # % annually
            'major_markets': ['East Asia', 'Middle East', 'Africa'],
            'price_premium': 15,  # % over domestic
            'export_value': 1500  # $/tonne
        },
        'wheat': {
            'demand_level': 'High',
            'growth_rate': 2.5,
            'major_markets': ['Middle East', 'North Africa', 'Southeast Asia'],
            'price_premium': 12,
            'export_value': 1200
        },
        'cotton': {
            'demand_level': 'Very High',
            'growth_rate': 4.1,
            'major_markets': ['Bangladesh', 'Vietnam', 'Indonesia'],
            'price_premium': 18,
            'export_value': 1800
        },
        'sugarcane': {
            'demand_level': 'High',
            'growth_rate': 2.8,
            'major_markets': ['EU', 'Middle East', 'Africa'],
            'price_premium': 20,  # Higher value product (sugar)
            'export_value': 2000
        },
        'groundnut': {
            'demand_level': 'High',
            'growth_rate': 3.5,
            'major_markets': ['Japan', 'South Korea', 'Europe'],
            'price_premium': 22,
            'export_value': 2500
        },
        'maize': {
            'demand_level': 'Very High',
            'growth_rate': 2.9,
            'major_markets': ['Southeast Asia', 'Middle East', 'Africa'],
            'price_premium': 10,
            'export_value': 1000
        },
        'soybean': {
            'demand_level': 'Very High',
            'growth_rate': 3.7,
            'major_markets': ['Japan', 'South Korea', 'Singapore'],
            'price_premium': 16,
            'export_value': 1600
        },
        'potato': {
            'demand_level': 'Medium',
            'growth_rate': 2.2,
            'major_markets': ['Bangladesh', 'Nepal', 'Middle East'],
            'price_premium': 8,
            'export_value': 400
        },
        'onion': {
            'demand_level': 'Medium',
            'growth_rate': 2.0,
            'major_markets': ['Bangladesh', 'Malaysia', 'Middle East'],
            'price_premium': 10,
            'export_value': 600
        },
        'tomato': {
            'demand_level': 'Medium',
            'growth_rate': 2.5,
            'major_markets': ['European Union', 'Middle East', 'Southeast Asia'],
            'price_premium': 12,
            'export_value': 1000
        }
    }
    
    # Certification requirements for exports
    CERTIFICATIONS = {
        'organic': {
            'premium': 30,  # % price premium
            'cost': 15000,  # One-time cost in INR
            'time': 12  # Months to certify
        },
        'gmp': {
            'premium': 15,
            'cost': 5000,
            'time': 3
        },
        'food_safety': {
            'premium': 10,
            'cost': 8000,
            'time': 6
        },
        'fair_trade': {
            'premium': 20,
            'cost': 12000,
            'time': 9
        }
    }
    
    def __init__(self):
        """Initialize export opportunity indicator."""
        self.data_loader = get_data_loader()
    
    def assess_export_potential(self, crop_id: str) -> Dict[str, Any]:
        """
        Assess export potential for a crop.
        
        Args:
            crop_id: Crop identifier
            
        Returns:
            dict: Export opportunity assessment
        """
        
        crop_key = crop_id.lower()
        
        if crop_key not in self.EXPORT_DEMAND:
            return {
                'success': False,
                'error': f'Export data not available for {crop_id}'
            }
        
        demand_data = self.EXPORT_DEMAND[crop_key]
        
        # Calculate export opportunity score
        opportunity_score = self._calculate_opportunity_score(demand_data)
        
        # Get export potential recommendations
        recommendations = self._get_export_recommendations(crop_key, opportunity_score)
        
        # Calculate potential export revenue
        export_revenue = self._estimate_export_revenue(crop_key, demand_data)
        
        return {
            'success': True,
            'crop_id': crop_id.capitalize(),
            'export_opportunity': {
                'score': round(opportunity_score, 1),
                'level': self._score_to_level(opportunity_score),
                'suitable_for_export': opportunity_score >= 60,
                'growth_trajectory': 'Rising' if demand_data['growth_rate'] > 3.0 else 'Stable'
            },
            'market_analysis': {
                'demand_level': demand_data['demand_level'],
                'growth_rate_percent': demand_data['growth_rate'],
                'major_export_markets': demand_data['major_markets'],
                'international_price_premium': f"{demand_data['price_premium']}% above domestic"
            },
            'revenue_potential': export_revenue,
            'export_readiness': self._assess_readiness(crop_key),
            'recommendations': recommendations,
            'next_steps': [
                'Connect with export trade associations',
                'Get quality certifications (if needed)',
                'Identify export-oriented buyers/traders',
                'Ensure compliance with food safety standards'
            ]
        }
    
    def get_certification_requirements(self, destination: str) -> Dict[str, Any]:
        """
        Get certification requirements for export destination.
        
        Args:
            destination: Export destination country/region
            
        Returns:
            dict: Certification requirements
        """
        
        # Simplified certification mapping
        destination_lower = destination.lower()
        
        certifications_needed = []
        
        if destination_lower in ['eu', 'europe', 'france', 'germany']:
            certifications_needed = ['gmp', 'food_safety', 'organic_optional']
        elif destination_lower in ['japan', 'korea', 'singapore']:
            certifications_needed = ['food_safety', 'gmp', 'fair_trade_optional']
        elif destination_lower in ['bangladesh', 'nepal', 'middle east']:
            certifications_needed = ['food_safety', 'gmp']
        elif destination_lower in ['africa', 'southeast asia']:
            certifications_needed = ['food_safety', 'gmp']
        else:
            certifications_needed = ['food_safety', 'gmp']
        
        # Build certification details
        required_certifications = []
        optional_certifications = []
        
        for cert in certifications_needed:
            cert_clean = cert.rstrip('_optional')
            if cert_clean in self.CERTIFICATIONS:
                cert_info = {
                    **self.CERTIFICATIONS[cert_clean],
                    'name': cert_clean.replace('_', ' ').title()
                }
                
                if '_optional' in cert:
                    optional_certifications.append(cert_info)
                else:
                    required_certifications.append(cert_info)
        
        return {
            'success': True,
            'destination': destination.title(),
            'required_certifications': required_certifications,
            'optional_certifications': optional_certifications,
            'total_cost_estimate': sum(c['cost'] for c in required_certifications),
            'timeline_months': max((c['time'] for c in required_certifications), default=0)
        }
    
    def compare_domestic_vs_export(self, crop_id: str, domestic_price: float) -> Dict[str, Any]:
        """
        Compare domestic vs export price potential.
        
        Args:
            crop_id: Crop identifier
            domestic_price: Current domestic price per kg
            
        Returns:
            dict: Price comparison analysis
        """
        
        crop_key = crop_id.lower()
        
        if crop_key not in self.EXPORT_DEMAND:
            return {
                'success': False,
                'error': f'Export data not available for {crop_id}'
            }
        
        export_data = self.EXPORT_DEMAND[crop_key]
        price_premium = export_data['price_premium']
        export_value = export_data['export_value']
        
        # Convert $/tonne to ₹/kg (1 tonne = 1000 kg, approx $1 = ₹80)
        export_price_per_kg = (export_value / 1000) * 80
        
        # Calculate premium
        premium_amount = (domestic_price * price_premium) / 100
        potential_export_price = domestic_price + premium_amount
        
        # Calculate per hectare benefit (assuming 5 tonnes/hectare average)
        avg_yield_per_hectare = 5000  # kg
        
        domestic_revenue = domestic_price * avg_yield_per_hectare
        export_revenue = potential_export_price * avg_yield_per_hectare
        additional_revenue = export_revenue - domestic_revenue
        
        return {
            'success': True,
            'crop_id': crop_id.capitalize(),
            'price_analysis': {
                'domestic_price_per_kg': round(domestic_price, 2),
                'export_potential_per_kg': round(potential_export_price, 2),
                'price_premium_percent': price_premium,
                'additional_earnings_per_kg': round(premium_amount, 2)
            },
            'per_hectare_revenues': {
                'domestic_revenue': round(domestic_revenue, 0),
                'export_revenue': round(export_revenue, 0),
                'additional_potential': round(additional_revenue, 0),
                'revenue_increase_percent': round((additional_revenue / domestic_revenue) * 100, 1)
            },
            'investment_vs_return': {
                'certification_cost': 5000,  # Average
                'break_even_quantity': round(5000 / premium_amount, 0) if premium_amount > 0 else 0,
                'annual_potential_with_1hectare': round(additional_revenue, 0)
            }
        }
    
    def get_export_contacts(self, crop_id: str) -> Dict[str, Any]:
        """
        Get export contacts and resources.
        
        Args:
            crop_id: Crop identifier
            
        Returns:
            dict: Export contacts and resources
        """
        
        # General export resources
        resources = {
            'success': True,
            'crop_id': crop_id.capitalize(),
            'export_bodies': [
                {
                    'name': 'APEDA (Agricultural & Processed Food Export Development Authority)',
                    'focus': 'Agricultural products export promotion',
                    'website': 'www.apeda.gov.in',
                    'phone': '+91-11-4161-2001'
                },
                {
                    'name': 'FIEO (Federation of Indian Export Organisations)',
                    'focus': 'All export sectors',
                    'website': 'www.fieoworld.com',
                    'phone': '+91-11-4141-2700'
                },
                {
                    'name': 'State Agriculture Departments',
                    'focus': 'Regional agricultural exports',
                    'website': 'State-specific',
                    'phone': 'Check state government website'
                }
            ],
            'certifications_bodies': [
                {
                    'name': 'Bureau of Indian Standards (BIS)',
                    'focus': 'Quality certification',
                    'certification': 'ISI Mark'
                },
                {
                    'name': 'CAB India',
                    'focus': 'Organic certification',
                    'certification': 'Organic'
                },
                {
                    'name': 'Various agencies',
                    'focus': 'Food safety certifications',
                    'certification': 'FSSAI license (mandatory for all)'
                }
            ],
            'online_platforms': [
                'Trade India (www.tradeindia.com)',
                'Global Sources (www.globalsources.com)',
                'Alibaba (www.alibaba.com)',
                'India Trade Portal (www.indiatrade.gov.in)'
            ]
        }
        
        return resources
    
    def _calculate_opportunity_score(self, demand_data: Dict[str, Any]) -> float:
        """
        Calculate export opportunity score (0-100).
        
        Args:
            demand_data: Demand data for crop
            
        Returns:
            float: Opportunity score
        """
        
        # Score based on demand and growth
        demand_scores = {
            'Very High': 90,
            'High': 75,
            'Medium': 50,
            'Low': 30
        }
        
        demand_score = demand_scores.get(demand_data['demand_level'], 50)
        
        # Growth rate bonus (up to 10 points)
        growth_bonus = min(10, (demand_data['growth_rate'] / 5) * 10)
        
        # Price premium bonus (up to 10 points)
        premium_bonus = min(10, (demand_data['price_premium'] / 30) * 10)
        
        total_score = demand_score + growth_bonus + premium_bonus
        
        return min(100, total_score)
    
    def _score_to_level(self, score: float) -> str:
        """Convert score to opportunity level."""
        if score >= 80:
            return 'Excellent'
        elif score >= 65:
            return 'Very Good'
        elif score >= 50:
            return 'Good'
        elif score >= 35:
            return 'Fair'
        else:
            return 'Limited'
    
    def _get_export_recommendations(self, crop_id: str, score: float) -> List[str]:
        """Get specific export recommendations."""
        
        recommendations = []
        
        if score >= 80:
            recommendations.append('Strong export market - actively pursue export opportunities')
            recommendations.append('Invest in quality certifications for premium markets')
            recommendations.append('Connect with bulk export traders')
        elif score >= 65:
            recommendations.append('Good export potential - consider exporting select batches')
            recommendations.append('Get basic food safety certifications first')
            recommendations.append('Research specific buyer requirements')
        elif score >= 50:
            recommendations.append('Moderate export potential - may be viable with right channels')
            recommendations.append('Focus on quality improvement first')
            recommendations.append('Build relationships with local traders first')
        else:
            recommendations.append('Limited direct export opportunities')
            recommendations.append('Supply to domestic processing units instead')
            recommendations.append('Focus on domestic premium markets')
        
        return recommendations
    
    def _assess_readiness(self, crop_id: str) -> Dict[str, str]:
        """Assess farmer readiness for exports."""
        
        return {
            'scale_requirement': 'Minimum 5-10 hectares recommended',
            'quality_standards': 'Must meet international food safety standards',
            'certifications': 'FSSAI mandatory, others based on destination',
            'cold_chain': 'May require temperature-controlled storage',
            'documentation': 'Extensive documentation and traceability required'
        }
    
    def _estimate_export_revenue(
        self,
        crop_id: str,
        demand_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Estimate export revenue potential."""
        
        # Assume small farmer with 5 hectares
        avg_yield_per_hectare = 5000  # kg
        total_production = avg_yield_per_hectare * 5  # 5 hectares
        
        # Convert export value from $/tonne to INR/kg
        export_price_per_kg = (demand_data['export_value'] / 1000) * 80  # Approx $1 = ₹80
        
        gross_revenue = total_production * export_price_per_kg
        
        # Subtract export costs (logistics, certification, trader margin)
        export_costs = gross_revenue * 0.15  # 15% typically
        net_revenue = gross_revenue - export_costs
        
        return {
            'assuming_5hectares': 'Base calculation',
            'annual_export_volume_kg': total_production,
            'expected_price_per_kg': round(export_price_per_kg, 2),
            'gross_revenue_estimate': round(gross_revenue, 0),
            'export_costs_estimated': round(export_costs, 0),
            'net_revenue_potential': round(net_revenue, 0),
            'note': 'Estimates are indicative. Actual depends on quality, market conditions, certification'
        }
