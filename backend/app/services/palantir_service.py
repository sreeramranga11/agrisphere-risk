import aiohttp
import asyncio
import structlog
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from app.core.config import settings

logger = structlog.get_logger()

class PalantirService:
    """Service for interacting with Palantir Foundry and AIP API"""
    
    def __init__(self):
        self.foundry_url = settings.FOUNDRY_URL
        self.aip_url = settings.AIP_API_URL
        self.foundry_token = settings.FOUNDRY_TOKEN
        self.aip_token = settings.AIP_API_TOKEN
        
        if not self.foundry_token or not self.aip_token:
            logger.warning("Palantir tokens not configured - using mock data")
    
    async def _make_request(self, url: str, method: str = "GET", 
                          headers: Optional[Dict] = None, 
                          data: Optional[Dict] = None) -> Dict:
        """Make HTTP request to Palantir services"""
        if not headers:
            headers = {}
        
        if self.foundry_token:
            headers["Authorization"] = f"Bearer {self.foundry_token}"
        
        async with aiohttp.ClientSession() as session:
            try:
                if method.upper() == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await response.json()
                elif method.upper() == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        return await response.json()
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
            except Exception as e:
                logger.error(f"Palantir API request failed: {e}")
                return {}
    
    async def get_satellite_data(self, bounds: Dict, date_range: Dict) -> Dict:
        """Retrieve satellite imagery data from Foundry"""
        if not self.foundry_token:
            # Return mock satellite data
            return {
                "ndvi_data": {
                    "value": 0.65,
                    "timestamp": datetime.now().isoformat(),
                    "source": "mock_satellite"
                },
                "imagery_url": "https://example.com/satellite_image.jpg",
                "resolution": "10m"
            }
        
        url = f"{self.foundry_url}/api/v1/satellite/data"
        data = {
            "bounds": bounds,
            "start_date": date_range["start"],
            "end_date": date_range["end"],
            "data_types": ["ndvi", "rgb", "thermal"]
        }
        
        return await self._make_request(url, method="POST", data=data)
    
    async def get_weather_data(self, location: Dict, date_range: Dict) -> Dict:
        """Retrieve weather data from Foundry"""
        if not self.foundry_token:
            # Return mock weather data
            return {
                "temperature": {
                    "current": 22.5,
                    "min": 15.2,
                    "max": 28.7,
                    "unit": "celsius"
                },
                "precipitation": {
                    "total": 45.2,
                    "unit": "mm"
                },
                "humidity": 65.0,
                "wind_speed": 12.3,
                "timestamp": datetime.now().isoformat()
            }
        
        url = f"{self.foundry_url}/api/v1/weather/data"
        data = {
            "location": location,
            "start_date": date_range["start"],
            "end_date": date_range["end"]
        }
        
        return await self._make_request(url, method="POST", data=data)
    
    async def get_soil_data(self, location: Dict) -> Dict:
        """Retrieve soil composition and moisture data"""
        if not self.foundry_token:
            return {
                "soil_type": "loam",
                "moisture_content": 0.35,
                "ph_level": 6.8,
                "organic_matter": 2.5,
                "nitrogen": 0.15,
                "phosphorus": 0.08,
                "potassium": 0.12
            }
        
        url = f"{self.foundry_url}/api/v1/soil/data"
        data = {"location": location}
        
        return await self._make_request(url, method="POST", data=data)
    
    async def assess_risk_with_aip(self, farm_data: Dict) -> Dict:
        """Use AIP API to assess farm risk"""
        if not self.aip_token:
            # Return mock risk assessment
            return {
                "overall_risk_score": 0.42,
                "risk_breakdown": {
                    "drought": 0.35,
                    "flood": 0.28,
                    "hail": 0.15,
                    "pest": 0.22
                },
                "confidence_score": 0.85,
                "model_version": "mock_v1.0",
                "recommendations": [
                    "Consider drought-resistant crop varieties",
                    "Implement irrigation system",
                    "Monitor soil moisture levels"
                ]
            }
        
        url = f"{self.aip_url}/api/v1/risk/assess"
        data = {
            "farm_data": farm_data,
            "assessment_type": "comprehensive",
            "include_historical": True
        }
        
        return await self._make_request(url, method="POST", data=data)
    
    async def detect_damage_with_aip(self, pre_event_image: str, 
                                   post_event_image: str) -> Dict:
        """Use AIP to detect crop damage from satellite imagery"""
        if not self.aip_token:
            return {
                "damage_percentage": 0.25,
                "damage_type": "hail",
                "confidence_score": 0.78,
                "affected_areas": [
                    {"coordinates": [0, 0], "severity": "moderate"}
                ]
            }
        
        url = f"{self.aip_url}/api/v1/damage/detect"
        data = {
            "pre_event_image": pre_event_image,
            "post_event_image": post_event_image,
            "detection_type": "crop_damage"
        }
        
        return await self._make_request(url, method="POST", data=data)
    
    async def calculate_premium_with_aip(self, risk_assessment: Dict, 
                                       farm_data: Dict) -> Dict:
        """Use AIP to calculate optimal insurance premium"""
        if not self.aip_token:
            base_premium = farm_data.get("area_hectares", 100) * 25  # $25/hectare
            risk_multiplier = 1 + risk_assessment.get("overall_risk_score", 0.5)
            return {
                "premium_amount": base_premium * risk_multiplier,
                "coverage_amount": base_premium * 3,
                "risk_multiplier": risk_multiplier,
                "factors_considered": ["area", "risk_score", "crop_type"]
            }
        
        url = f"{self.aip_url}/api/v1/premium/calculate"
        data = {
            "risk_assessment": risk_assessment,
            "farm_data": farm_data,
            "market_conditions": "current"
        }
        
        return await self._make_request(url, method="POST", data=data)
    
    async def get_historical_data(self, farm_id: str, 
                                date_range: Dict) -> Dict:
        """Retrieve historical farm performance data"""
        if not self.foundry_token:
            return {
                "yield_history": [
                    {"year": 2022, "yield_per_hectare": 8.5},
                    {"year": 2021, "yield_per_hectare": 7.8},
                    {"year": 2020, "yield_per_hectare": 9.2}
                ],
                "claim_history": [
                    {"year": 2022, "claim_amount": 0},
                    {"year": 2021, "claim_amount": 15000},
                    {"year": 2020, "claim_amount": 0}
                ]
            }
        
        url = f"{self.foundry_url}/api/v1/farm/{farm_id}/history"
        data = {"date_range": date_range}
        
        return await self._make_request(url, method="POST", data=data)

# Global service instance
palantir_service = PalantirService() 