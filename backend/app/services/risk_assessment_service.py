import asyncio
import structlog
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from shapely.geometry import Polygon
import json

from app.services.palantir_service import palantir_service
from app.models.farm import Farm, FarmAssessment
from app.schemas.farm import RiskAssessmentRequest, RiskAssessmentResponse

logger = structlog.get_logger()

class RiskAssessmentService:
    """Service for comprehensive agricultural risk assessment"""
    
    def __init__(self):
        self.risk_weights = {
            "drought": 0.35,
            "flood": 0.25,
            "hail": 0.20,
            "pest": 0.15,
            "frost": 0.05
        }
    
    async def assess_farm_risk(self, farm: Farm, 
                             request: RiskAssessmentRequest) -> RiskAssessmentResponse:
        """Perform comprehensive risk assessment for a farm"""
        logger.info(f"Starting risk assessment for farm {farm.id}")
        
        try:
            # Extract farm location bounds
            location_bounds = self._extract_bounds_from_farm(farm)
            
            # Gather data from multiple sources
            satellite_data = await self._get_satellite_data(location_bounds)
            weather_data = await self._get_weather_data(location_bounds)
            soil_data = await self._get_soil_data(location_bounds)
            historical_data = await self._get_historical_data(str(farm.id))
            
            # Prepare farm data for AIP analysis
            farm_data = self._prepare_farm_data(farm, satellite_data, 
                                              weather_data, soil_data, historical_data)
            
            # Get AI-powered risk assessment from AIP
            aip_assessment = await palantir_service.assess_risk_with_aip(farm_data)
            
            # Calculate comprehensive risk scores
            risk_scores = self._calculate_risk_scores(farm_data, aip_assessment)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_scores, farm_data)
            
            # Calculate premium suggestion
            premium_data = await palantir_service.calculate_premium_with_aip(
                aip_assessment, farm_data
            )
            
            # Prepare response
            response = RiskAssessmentResponse(
                farm_id=farm.id,
                assessment_date=datetime.now(),
                overall_risk_score=risk_scores["overall"],
                risk_breakdown=risk_scores["breakdown"],
                recommendations=recommendations,
                confidence_score=aip_assessment.get("confidence_score", 0.8),
                data_sources=["satellite", "weather", "soil", "historical", "aip"],
                premium_suggestion=premium_data.get("premium_amount")
            )
            
            logger.info(f"Risk assessment completed for farm {farm.id}")
            return response
            
        except Exception as e:
            logger.error(f"Risk assessment failed for farm {farm.id}: {e}")
            raise
    
    def _extract_bounds_from_farm(self, farm: Farm) -> Dict:
        """Extract bounding box from farm geometry"""
        # This would need to be implemented based on your geometry format
        # For now, return a mock bounding box
        return {
            "min_lat": 40.0,
            "max_lat": 41.0,
            "min_lon": -105.0,
            "max_lon": -104.0
        }
    
    async def _get_satellite_data(self, bounds: Dict) -> Dict:
        """Get satellite imagery and NDVI data"""
        date_range = {
            "start": (datetime.now() - timedelta(days=30)).isoformat(),
            "end": datetime.now().isoformat()
        }
        
        return await palantir_service.get_satellite_data(bounds, date_range)
    
    async def _get_weather_data(self, bounds: Dict) -> Dict:
        """Get historical and current weather data"""
        date_range = {
            "start": (datetime.now() - timedelta(days=90)).isoformat(),
            "end": datetime.now().isoformat()
        }
        
        return await palantir_service.get_weather_data(bounds, date_range)
    
    async def _get_soil_data(self, bounds: Dict) -> Dict:
        """Get soil composition and moisture data"""
        return await palantir_service.get_soil_data(bounds)
    
    async def _get_historical_data(self, farm_id: str) -> Dict:
        """Get historical farm performance data"""
        date_range = {
            "start": (datetime.now() - timedelta(days=365*3)).isoformat(),
            "end": datetime.now().isoformat()
        }
        
        return await palantir_service.get_historical_data(farm_id, date_range)
    
    def _prepare_farm_data(self, farm: Farm, satellite_data: Dict, 
                          weather_data: Dict, soil_data: Dict, 
                          historical_data: Dict) -> Dict:
        """Prepare comprehensive farm data for analysis"""
        return {
            "farm_id": str(farm.id),
            "area_hectares": farm.area_hectares,
            "soil_type": farm.soil_type or soil_data.get("soil_type"),
            "elevation_m": farm.elevation_m,
            "slope_percent": farm.slope_percent,
            
            # Satellite data
            "ndvi_value": satellite_data.get("ndvi_data", {}).get("value"),
            "satellite_timestamp": satellite_data.get("ndvi_data", {}).get("timestamp"),
            
            # Weather data
            "current_temperature": weather_data.get("temperature", {}).get("current"),
            "temperature_range": {
                "min": weather_data.get("temperature", {}).get("min"),
                "max": weather_data.get("temperature", {}).get("max")
            },
            "precipitation_total": weather_data.get("precipitation", {}).get("total"),
            "humidity": weather_data.get("humidity"),
            "wind_speed": weather_data.get("wind_speed"),
            
            # Soil data
            "soil_moisture": soil_data.get("moisture_content"),
            "ph_level": soil_data.get("ph_level"),
            "organic_matter": soil_data.get("organic_matter"),
            
            # Historical data
            "yield_history": historical_data.get("yield_history", []),
            "claim_history": historical_data.get("claim_history", []),
            
            # Location
            "location": {
                "bounds": self._extract_bounds_from_farm(farm),
                "coordinates": "mock_coordinates"  # Would be actual coordinates
            }
        }
    
    def _calculate_risk_scores(self, farm_data: Dict, aip_assessment: Dict) -> Dict:
        """Calculate comprehensive risk scores"""
        # Use AIP assessment as base
        risk_breakdown = aip_assessment.get("risk_breakdown", {})
        
        # Apply environmental factors
        adjusted_risks = {}
        
        # Drought risk adjustment based on soil moisture and precipitation
        drought_base = risk_breakdown.get("drought", 0.3)
        soil_moisture = farm_data.get("soil_moisture", 0.5)
        precipitation = farm_data.get("precipitation_total", 0)
        
        drought_adjustment = (1 - soil_moisture) * 0.3 + (1 - min(precipitation/100, 1)) * 0.2
        adjusted_risks["drought"] = min(drought_base + drought_adjustment, 1.0)
        
        # Flood risk adjustment based on elevation and slope
        flood_base = risk_breakdown.get("flood", 0.2)
        elevation = farm_data.get("elevation_m", 1000)
        slope = farm_data.get("slope_percent", 5)
        
        flood_adjustment = (1 - min(elevation/2000, 1)) * 0.2 + (1 - min(slope/20, 1)) * 0.1
        adjusted_risks["flood"] = min(flood_base + flood_adjustment, 1.0)
        
        # Hail risk (mostly from AIP)
        adjusted_risks["hail"] = risk_breakdown.get("hail", 0.15)
        
        # Pest risk adjustment based on historical data
        pest_base = risk_breakdown.get("pest", 0.2)
        claim_history = farm_data.get("claim_history", [])
        pest_claims = sum(1 for claim in claim_history if claim.get("claim_amount", 0) > 0)
        pest_adjustment = min(pest_claims / 10, 0.3)  # Max 30% adjustment
        adjusted_risks["pest"] = min(pest_base + pest_adjustment, 1.0)
        
        # Calculate overall risk score
        overall_risk = sum(
            adjusted_risks[risk_type] * self.risk_weights[risk_type]
            for risk_type in adjusted_risks
        )
        
        return {
            "overall": overall_risk,
            "breakdown": adjusted_risks
        }
    
    def _generate_recommendations(self, risk_scores: Dict, farm_data: Dict) -> List[str]:
        """Generate actionable recommendations based on risk assessment"""
        recommendations = []
        
        # Drought recommendations
        if risk_scores["breakdown"].get("drought", 0) > 0.4:
            recommendations.append("Consider drought-resistant crop varieties")
            recommendations.append("Implement or upgrade irrigation system")
            recommendations.append("Monitor soil moisture levels regularly")
        
        # Flood recommendations
        if risk_scores["breakdown"].get("flood", 0) > 0.3:
            recommendations.append("Implement drainage improvements")
            recommendations.append("Consider crop insurance with flood coverage")
            recommendations.append("Monitor weather forecasts during planting season")
        
        # Hail recommendations
        if risk_scores["breakdown"].get("hail", 0) > 0.25:
            recommendations.append("Consider hail-resistant crop varieties")
            recommendations.append("Implement hail protection measures")
            recommendations.append("Monitor storm patterns in your region")
        
        # Pest recommendations
        if risk_scores["breakdown"].get("pest", 0) > 0.3:
            recommendations.append("Implement integrated pest management")
            recommendations.append("Consider crop rotation strategies")
            recommendations.append("Monitor for early pest detection")
        
        # General recommendations
        if risk_scores["overall"] > 0.5:
            recommendations.append("Consider comprehensive crop insurance coverage")
            recommendations.append("Implement precision agriculture technologies")
            recommendations.append("Develop contingency plans for weather events")
        
        return recommendations[:5]  # Limit to top 5 recommendations

# Global service instance
risk_assessment_service = RiskAssessmentService() 