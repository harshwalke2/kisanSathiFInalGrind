"""
Data Loader Service
Loads crops data, mandi prices, and weather information from local files.
Designed to be easily replaceable with real APIs.
"""

import json
import csv
import os
from typing import Dict, List, Any
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent.parent


class DataLoader:
    """Loads and caches agricultural data from JSON and CSV files."""
    
    def __init__(self):
        """Initialize data loader and load all data."""
        self.crops_data = None
        self.mandi_prices = None
        self.weather_data = None
        self._load_all_data()
    
    def _load_all_data(self):
        """Load all data files on initialization."""
        self.crops_data = self._load_crops()
        self.mandi_prices = self._load_mandi_prices()
        self.weather_data = self._load_weather()
    
    def _load_crops(self) -> Dict[str, Any]:
        """
        Load crops database from JSON.
        
        Returns:
            dict: Crops data organized by crop_id
        """
        crops_file = os.path.join(BASE_DIR, 'data', 'crops.json')
        
        try:
            with open(crops_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert list to dict keyed by crop_id for faster lookup
            crops_dict = {}
            for crop in data.get('crops', []):
                crops_dict[crop['id']] = crop
            
            return crops_dict
        except Exception as e:
            print(f"Error loading crops data: {e}")
            return {}
    
    def _load_mandi_prices(self) -> Dict[str, Dict[str, Any]]:
        """
        Load mandi (market) prices from CSV.
        
        Returns:
            dict: Prices organized by crop_id and region
        """
        prices_file = os.path.join(BASE_DIR, 'data', 'mandi_prices.csv')
        prices_dict = {}
        
        try:
            with open(prices_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    crop_id = row['crop_id']
                    region = row['region']
                    
                    if crop_id not in prices_dict:
                        prices_dict[crop_id] = {}
                    
                    prices_dict[crop_id][region] = {
                        'current_price': float(row.get('current_price', 0)),
                        'avg_price_6m': float(row.get('avg_price_6m', 0)),
                        'price_trend': row.get('price_trend', 'stable'),
                        'stability': row.get('stability', 'medium'),
                        'export_demand': row.get('export_demand', 'medium')
                    }
            return prices_dict
        except Exception as e:
            print(f"Error loading mandi prices: {e}")
            return {}
    
    def _load_weather(self) -> Dict[str, Any]:
        """
        Load weather mock data from JSON.
        
        Returns:
            dict: Weather data organized by region
        """
        weather_file = os.path.join(BASE_DIR, 'data', 'weather_mock.json')
        
        try:
            with open(weather_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('weather_data', {})
        except Exception as e:
            print(f"Error loading weather data: {e}")
            return {}
    
    def get_crop_by_id(self, crop_id: str) -> Dict[str, Any]:
        """
        Get crop details by ID.
        
        Args:
            crop_id: The crop identifier
            
        Returns:
            dict: Crop details or empty dict if not found
        """
        return self.crops_data.get(crop_id, {})
    
    def get_all_crops(self) -> List[Dict[str, Any]]:
        """
        Get all available crops.
        
        Returns:
            list: All crops as list of dicts
        """
        return list(self.crops_data.values())
    
    def get_crops_by_season(self, season: str) -> List[Dict[str, Any]]:
        """
        Get crops available for a specific season.
        
        Args:
            season: 'Kharif', 'Rabi', or 'Zaid'
            
        Returns:
            list: Crops matching the season
        """
        matching = []
        for crop in self.crops_data.values():
            seasons = crop.get('season', '').split('|')
            if season in seasons:
                matching.append(crop)
        return matching
    
    def get_price_for_crop_region(self, crop_id: str, region: str) -> Dict[str, Any]:
        """
        Get market price for a crop in a specific region.
        
        Args:
            crop_id: The crop identifier
            region: The region/district name
            
        Returns:
            dict: Price data or empty dict if not found
        """
        return self.mandi_prices.get(crop_id, {}).get(region, {})
    
    def get_weather_for_region(self, region: str) -> Dict[str, Any]:
        """
        Get weather data for a region.
        
        Args:
            region: The region/district name
            
        Returns:
            dict: Weather data or empty dict if not found
        """
        return self.weather_data.get(region, {})
    
    def validate_location(self, location: str) -> bool:
        """
        Check if location has weather data available.
        
        Args:
            location: Location name
            
        Returns:
            bool: True if location exists in weather data
        """
        return location in self.weather_data
    
    def get_available_regions(self) -> List[str]:
        """
        Get list of all available regions.
        
        Returns:
            list: Region names
        """
        return list(self.weather_data.keys())


# Global data loader instance (singleton pattern)
data_loader = DataLoader()


def get_data_loader() -> DataLoader:
    """
    Get the global data loader instance.
    
    Returns:
        DataLoader: Singleton instance
    """
    return data_loader
