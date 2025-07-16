from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import structlog

from app.core.database import get_db
from app.services.palantir_service import palantir_service

logger = structlog.get_logger()
router = APIRouter()

@router.post("/analyze")
async def analyze_crop_damage(
    pre_event_image: UploadFile = File(...),
    post_event_image: UploadFile = File(...),
    farm_id: Optional[str] = None,
    event_type: Optional[str] = None
):
    """Analyze crop damage using AI and satellite imagery"""
    try:
        # Validate file types
        if not pre_event_image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Pre-event file must be an image"
            )
        
        if not post_event_image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Post-event file must be an image"
            )
        
        # Read image data
        pre_event_data = await pre_event_image.read()
        post_event_data = await post_event_image.read()
        
        # Convert to base64 or save temporarily
        # For now, we'll use placeholder data
        pre_event_url = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
        post_event_url = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
        
        # Use AIP to detect damage
        damage_analysis = await palantir_service.detect_damage_with_aip(
            pre_event_url, post_event_url
        )
        
        # Add metadata
        result = {
            "farm_id": farm_id,
            "event_type": event_type,
            "analysis_date": datetime.now().isoformat(),
            "damage_percentage": damage_analysis.get("damage_percentage", 0),
            "damage_type": damage_analysis.get("damage_type", "unknown"),
            "confidence_score": damage_analysis.get("confidence_score", 0),
            "affected_areas": damage_analysis.get("affected_areas", []),
            "recommendations": _generate_damage_recommendations(
                damage_analysis.get("damage_percentage", 0),
                damage_analysis.get("damage_type", "unknown")
            )
        }
        
        logger.info(f"Damage analysis completed for farm {farm_id}")
        return result
        
    except Exception as e:
        logger.error(f"Damage analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Damage analysis failed: {str(e)}"
        )

@router.post("/satellite-analysis")
async def analyze_satellite_damage(
    farm_id: str,
    event_date: datetime,
    event_type: str
):
    """Analyze crop damage using satellite imagery from Palantir"""
    try:
        # Get farm location (this would need to be implemented)
        farm_bounds = {
            "min_lat": 40.0,
            "max_lat": 41.0,
            "min_lon": -105.0,
            "max_lon": -104.0
        }
        
        # Get satellite data before and after event
        pre_event_range = {
            "start": (event_date - timedelta(days=7)).isoformat(),
            "end": event_date.isoformat()
        }
        
        post_event_range = {
            "start": event_date.isoformat(),
            "end": (event_date + timedelta(days=7)).isoformat()
        }
        
        # Get satellite imagery
        pre_event_satellite = await palantir_service.get_satellite_data(
            farm_bounds, pre_event_range
        )
        
        post_event_satellite = await palantir_service.get_satellite_data(
            farm_bounds, post_event_range
        )
        
        # Analyze damage using AIP
        damage_analysis = await palantir_service.detect_damage_with_aip(
            pre_event_satellite.get("imagery_url", ""),
            post_event_satellite.get("imagery_url", "")
        )
        
        result = {
            "farm_id": farm_id,
            "event_date": event_date.isoformat(),
            "event_type": event_type,
            "analysis_date": datetime.now().isoformat(),
            "damage_percentage": damage_analysis.get("damage_percentage", 0),
            "damage_type": damage_analysis.get("damage_type", "unknown"),
            "confidence_score": damage_analysis.get("confidence_score", 0),
            "ndvi_change": {
                "pre_event": pre_event_satellite.get("ndvi_data", {}).get("value"),
                "post_event": post_event_satellite.get("ndvi_data", {}).get("value")
            },
            "affected_areas": damage_analysis.get("affected_areas", []),
            "recommendations": _generate_damage_recommendations(
                damage_analysis.get("damage_percentage", 0),
                event_type
            )
        }
        
        logger.info(f"Satellite damage analysis completed for farm {farm_id}")
        return result
        
    except Exception as e:
        logger.error(f"Satellite damage analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Satellite damage analysis failed: {str(e)}"
        )

@router.get("/history/{farm_id}")
async def get_damage_history(
    farm_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get historical damage assessments for a farm"""
    # This would query a damage_assessments table
    # For now, return mock data
    return [
        {
            "id": "damage_001",
            "farm_id": farm_id,
            "event_date": "2023-07-15T14:30:00Z",
            "event_type": "hail",
            "damage_percentage": 0.25,
            "damage_type": "crop_damage",
            "confidence_score": 0.85,
            "analysis_date": "2023-07-16T10:00:00Z"
        },
        {
            "id": "damage_002",
            "farm_id": farm_id,
            "event_date": "2023-06-20T16:45:00Z",
            "event_type": "drought",
            "damage_percentage": 0.15,
            "damage_type": "stress",
            "confidence_score": 0.78,
            "analysis_date": "2023-06-25T09:30:00Z"
        }
    ]

def _generate_damage_recommendations(damage_percentage: float, damage_type: str) -> List[str]:
    """Generate recommendations based on damage analysis"""
    recommendations = []
    
    if damage_percentage > 0.5:
        recommendations.append("Severe damage detected - consider replanting")
        recommendations.append("File insurance claim immediately")
        recommendations.append("Assess soil conditions before replanting")
    elif damage_percentage > 0.25:
        recommendations.append("Moderate damage - monitor crop recovery")
        recommendations.append("Consider partial insurance claim")
        recommendations.append("Implement damage mitigation measures")
    else:
        recommendations.append("Minor damage - continue monitoring")
        recommendations.append("No immediate action required")
    
    if damage_type == "hail":
        recommendations.append("Check for hail damage to irrigation systems")
        recommendations.append("Monitor for disease development in damaged areas")
    elif damage_type == "drought":
        recommendations.append("Implement water conservation measures")
        recommendations.append("Consider drought-resistant crop varieties")
    elif damage_type == "flood":
        recommendations.append("Assess soil drainage and erosion")
        recommendations.append("Check for nutrient leaching")
    
    return recommendations[:5]  # Limit to top 5 recommendations 