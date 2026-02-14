"""
Price Trend Analyzer Service
Analyzes price trends, volatility, and provides sell/hold recommendations.
"""

from typing import Dict, List, Any
from services.data_loader import get_data_loader
from datetime import datetime, timedelta
import random  # Mock data generation


class PriceTrendAnalyzer:
    """Analyzes crop price trends and provides market insights."""
    
    def __init__(self):
        """Initialize price analyzer with data loader."""
        self.data_loader = get_data_loader()
    
    def get_price_trend(self, crop_id: str, region: str) -> Dict[str, Any]:
        """
        Get detailed price trend analysis for a crop.
        
        Args:
            crop_id: Crop identifier
            region: Region/district name
            
        Returns:
            dict: Price trend with history, volatility, and recommendation
        """
        
        # Get current price data
        price_data = self.data_loader.get_price_for_crop_region(crop_id, region)
        
        if not price_data:
            return {
                'success': False,
                'error': f'No price data for {crop_id} in {region}'
            }
        
        # Generate mock 30-day trend (in production, fetch from API)
        trend_data = self._generate_trend_data(price_data)
        
        # Calculate volatility
        volatility = self._calculate_volatility(trend_data['daily_prices'])
        
        # Get simple moving average
        ma_7 = self._calculate_moving_average(trend_data['daily_prices'], 7)
        ma_14 = self._calculate_moving_average(trend_data['daily_prices'], 14)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            trend_data['daily_prices'],
            volatility,
            price_data.get('price_trend', 'stable')
        )
        
        return {
            'success': True,
            'crop_id': crop_id,
            'region': region,
            'current_price': price_data.get('current_price', 0),
            'price_history': {
                'daily_prices': trend_data['daily_prices'],
                'dates': trend_data['dates']
            },
            'moving_averages': {
                'ma_7': round(ma_7, 2),
                'ma_14': round(ma_14, 2)
            },
            'volatility': {
                'percentage': round(volatility, 2),
                'level': self._categorize_volatility(volatility)
            },
            'trend': price_data.get('price_trend', 'stable'),
            'recommendation': recommendation,
            'stats': {
                'avg_price': round(sum(trend_data['daily_prices']) / len(trend_data['daily_prices']), 2),
                'max_price': round(max(trend_data['daily_prices']), 2),
                'min_price': round(min(trend_data['daily_prices']), 2),
                'price_range': round(max(trend_data['daily_prices']) - min(trend_data['daily_prices']), 2)
            }
        }
    
    def _generate_trend_data(self, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate 30-day price trend (mock data for now).
        
        In production: Fetch from real mandi API.
        
        Args:
            price_data: Current price data
            
        Returns:
            dict: Daily prices and dates
        """
        current_price = price_data.get('current_price', 2000)
        avg_price = price_data.get('avg_price_6m', 2000)
        
        # Mock trend based on price trend indicator
        trend = price_data.get('price_trend', 'stable').lower()
        trend_direction = {
            'up': 1.005,      # 0.5% daily increase
            'stable': 1.0,    # Flat
            'down': 0.995     # 0.5% daily decrease
        }.get(trend, 1.0)
        
        # Generate 30 daily prices
        prices = []
        current = current_price
        
        for _ in range(30):
            # Add small random variation
            variation = random.uniform(0.98, 1.02)
            current = current * trend_direction * variation
            prices.append(current)
        
        # Generate dates
        dates = []
        today = datetime.now()
        for i in range(29, -1, -1):
            date = today - timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d'))
        
        return {
            'daily_prices': prices,
            'dates': dates
        }
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """
        Calculate price volatility as percentage change.
        
        Args:
            prices: List of prices
            
        Returns:
            float: Volatility percentage
        """
        if len(prices) < 2:
            return 0.0
        
        # Calculate daily percentage changes
        changes = []
        for i in range(1, len(prices)):
            change = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
            changes.append(abs(change))
        
        # Return average daily volatility
        return sum(changes) / len(changes) if changes else 0.0
    
    def _calculate_moving_average(self, prices: List[float], period: int) -> float:
        """
        Calculate simple moving average.
        
        Args:
            prices: List of prices
            period: Number of days for average
            
        Returns:
            float: Moving average price
        """
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        return sum(prices[-period:]) / period
    
    def _categorize_volatility(self, volatility: float) -> str:
        """
        Categorize volatility level.
        
        Args:
            volatility: Volatility percentage
            
        Returns:
            str: Volatility level
        """
        if volatility < 1.0:
            return 'Low'
        elif volatility < 2.5:
            return 'Moderate'
        else:
            return 'High'
    
    def _generate_recommendation(
        self,
        prices: List[float],
        volatility: float,
        trend: str
    ) -> Dict[str, str]:
        """
        Generate sell/hold/buy recommendation.
        
        Args:
            prices: Daily prices
            volatility: Volatility percentage
            trend: Price trend indicator
            
        Returns:
            dict: Recommendation and reasoning
        """
        current_price = prices[-1]
        avg_price = sum(prices) / len(prices)
        price_ratio = current_price / avg_price
        
        # Simple logic
        if trend == 'up' and price_ratio > 1.02:
            recommendation = 'Hold/Sell Soon'
            reasoning = 'Prices rising but near short-term highs. Consider selling if your target is met.'
        elif trend == 'down' and price_ratio < 0.98:
            recommendation = 'Hold/Wait'
            reasoning = 'Prices declining. Consider holding if long-term price expected to recover.'
        elif volatility > 2.5:
            recommendation = 'Wait'
            reasoning = 'High price volatility. Better prices may come soon. Wait for stability.'
        else:
            recommendation = 'Fair Time to Sell'
            reasoning = 'Prices are steady. This may be a good time to sell your harvest.'
        
        return {
            'recommendation': recommendation,
            'reasoning': reasoning,
            'confidence': 'Moderate'  # Always moderate for mock data
        }
