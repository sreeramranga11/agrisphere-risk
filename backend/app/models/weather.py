from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import uuid

from app.core.database import Base

class WeatherStation(Base):
    """Weather station locations and metadata"""
    __tablename__ = "weather_stations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    elevation_m = Column(Float)
    state = Column(String(50))
    county = Column(String(100))
    
    # Station capabilities
    has_temperature = Column(Boolean, default=True)
    has_precipitation = Column(Boolean, default=True)
    has_wind = Column(Boolean, default=False)
    has_humidity = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class WeatherData(Base):
    """Historical weather data from stations"""
    __tablename__ = "weather_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Weather measurements
    temperature_celsius = Column(Float)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    precipitation_mm = Column(Float)
    humidity_percent = Column(Float)
    wind_speed_kmh = Column(Float)
    wind_direction_degrees = Column(Float)
    pressure_hpa = Column(Float)
    
    # Derived metrics
    heat_index = Column(Float)
    wind_chill = Column(Float)
    dew_point = Column(Float)
    
    # Data quality
    data_quality = Column(String(20))
    source = Column(String(50))

class ClimateEvent(Base):
    """Significant climate events (storms, droughts, etc.)"""
    __tablename__ = "climate_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)  # hail, drought, flood, frost
    event_name = Column(String(255))
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    
    # Geographic extent
    affected_area = Column(Geometry('POLYGON', srid=4326))
    severity = Column(String(20))  # low, medium, high, extreme
    
    # Impact metrics
    crop_damage_percent = Column(Float)
    economic_loss_usd = Column(Float)
    affected_farms_count = Column(Integer)
    
    # Event details
    description = Column(Text)
    source = Column(String(100))
    metadata = Column(JSONB) 