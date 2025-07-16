from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import uuid

from app.core.database import Base

class Farm(Base):
    """Farm entity model with geospatial data"""
    __tablename__ = "farms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    owner_name = Column(String(255), nullable=False)
    location = Column(Geometry('POLYGON', srid=4326), nullable=False)
    area_hectares = Column(Float, nullable=False)
    soil_type = Column(String(100))
    elevation_m = Column(Float)
    slope_percent = Column(Float)
    
    # Risk assessment data
    risk_score = Column(Float)
    drought_risk = Column(Float)
    flood_risk = Column(Float)
    hail_risk = Column(Float)
    pest_risk = Column(Float)
    
    # Insurance data
    insurance_policy_number = Column(String(100))
    premium_amount = Column(Float)
    coverage_amount = Column(Float)
    policy_start_date = Column(DateTime)
    policy_end_date = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Additional properties as JSON
    properties = Column(JSONB)

class FarmAssessment(Base):
    """Historical risk assessments for farms"""
    __tablename__ = "farm_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farm_id = Column(UUID(as_uuid=True), nullable=False)
    assessment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Risk scores
    overall_risk_score = Column(Float, nullable=False)
    drought_risk_score = Column(Float)
    flood_risk_score = Column(Float)
    hail_risk_score = Column(Float)
    pest_risk_score = Column(Float)
    
    # Environmental data
    ndvi_value = Column(Float)
    soil_moisture = Column(Float)
    temperature_avg = Column(Float)
    rainfall_total = Column(Float)
    
    # AI model metadata
    model_version = Column(String(50))
    confidence_score = Column(Float)
    assessment_notes = Column(Text)
    
    # Raw data sources
    data_sources = Column(JSONB) 