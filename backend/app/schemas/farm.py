from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from shapely.geometry import Polygon
import json

class FarmBase(BaseModel):
    """Base farm schema"""
    name: str = Field(..., min_length=1, max_length=255)
    owner_name: str = Field(..., min_length=1, max_length=255)
    area_hectares: float = Field(..., gt=0, le=10000)
    soil_type: Optional[str] = Field(None, max_length=100)
    elevation_m: Optional[float] = Field(None, ge=0)
    slope_percent: Optional[float] = Field(None, ge=0, le=100)

class FarmCreate(FarmBase):
    """Schema for creating a new farm"""
    location: str = Field(..., description="GeoJSON polygon string")
    
    @validator('location')
    def validate_location(cls, v):
        """Validate GeoJSON polygon"""
        try:
            geom = json.loads(v)
            if geom['type'] != 'Polygon':
                raise ValueError("Location must be a GeoJSON Polygon")
            
            # Validate polygon area
            polygon = Polygon(geom['coordinates'][0])
            area_hectares = polygon.area * 111.32 * 111.32  # Rough conversion to hectares
            if area_hectares > 10000:
                raise ValueError("Farm area cannot exceed 10,000 hectares")
            
            return v
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid GeoJSON: {e}")

class FarmUpdate(BaseModel):
    """Schema for updating farm data"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    owner_name: Optional[str] = Field(None, min_length=1, max_length=255)
    soil_type: Optional[str] = Field(None, max_length=100)
    elevation_m: Optional[float] = Field(None, ge=0)
    slope_percent: Optional[float] = Field(None, ge=0, le=100)
    properties: Optional[Dict[str, Any]] = None

class FarmResponse(FarmBase):
    """Schema for farm response"""
    id: UUID
    risk_score: Optional[float] = None
    drought_risk: Optional[float] = None
    flood_risk: Optional[float] = None
    hail_risk: Optional[float] = None
    pest_risk: Optional[float] = None
    insurance_policy_number: Optional[str] = None
    premium_amount: Optional[float] = None
    coverage_amount: Optional[float] = None
    policy_start_date: Optional[datetime] = None
    policy_end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    properties: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class FarmAssessmentBase(BaseModel):
    """Base farm assessment schema"""
    overall_risk_score: float = Field(..., ge=0, le=1)
    drought_risk_score: Optional[float] = Field(None, ge=0, le=1)
    flood_risk_score: Optional[float] = Field(None, ge=0, le=1)
    hail_risk_score: Optional[float] = Field(None, ge=0, le=1)
    pest_risk_score: Optional[float] = Field(None, ge=0, le=1)
    ndvi_value: Optional[float] = Field(None, ge=-1, le=1)
    soil_moisture: Optional[float] = Field(None, ge=0, le=1)
    temperature_avg: Optional[float] = Field(None, ge=-50, le=60)
    rainfall_total: Optional[float] = Field(None, ge=0)
    assessment_notes: Optional[str] = None

class FarmAssessmentCreate(FarmAssessmentBase):
    """Schema for creating a farm assessment"""
    farm_id: UUID

class FarmAssessmentResponse(FarmAssessmentBase):
    """Schema for farm assessment response"""
    id: UUID
    farm_id: UUID
    assessment_date: datetime
    model_version: Optional[str] = None
    confidence_score: Optional[float] = None
    data_sources: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class RiskAssessmentRequest(BaseModel):
    """Schema for risk assessment request"""
    farm_id: UUID
    include_historical: bool = True
    assessment_type: str = Field("comprehensive", regex="^(comprehensive|quick|detailed)$")

class RiskAssessmentResponse(BaseModel):
    """Schema for risk assessment response"""
    farm_id: UUID
    assessment_date: datetime
    overall_risk_score: float
    risk_breakdown: Dict[str, float]
    recommendations: List[str]
    confidence_score: float
    data_sources: List[str]
    premium_suggestion: Optional[float] = None 