from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import structlog

from app.core.database import get_db
from app.models.weather import WeatherStation, WeatherData, ClimateEvent
from app.services.palantir_service import palantir_service

logger = structlog.get_logger()
router = APIRouter()

@router.get("/stations")
async def get_weather_stations(
    state: Optional[str] = None,
    county: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get weather stations with optional filtering"""
    query = db.query(WeatherStation).filter(WeatherStation.is_active == True)
    
    if state:
        query = query.filter(WeatherStation.state == state)
    if county:
        query = query.filter(WeatherStation.county.ilike(f"%{county}%"))
    
    stations = query.all()
    return stations

@router.get("/data/{station_id}")
async def get_weather_data(
    station_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get weather data for a specific station"""
    if not start_date:
        start_date = datetime.now() - timedelta(days=7)
    if not end_date:
        end_date = datetime.now()
    
    data = db.query(WeatherData)\
        .filter(
            WeatherData.station_id == station_id,
            WeatherData.timestamp >= start_date,
            WeatherData.timestamp <= end_date
        )\
        .order_by(WeatherData.timestamp.desc())\
        .all()
    
    return data

@router.get("/forecast/{lat}/{lon}")
async def get_weather_forecast(lat: float, lon: float):
    """Get weather forecast for a location"""
    try:
        location = {"lat": lat, "lon": lon}
        date_range = {
            "start": datetime.now().isoformat(),
            "end": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        forecast_data = await palantir_service.get_weather_data(location, date_range)
        
        return {
            "location": {"lat": lat, "lon": lon},
            "forecast": forecast_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get weather forecast: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve weather forecast"
        ) 