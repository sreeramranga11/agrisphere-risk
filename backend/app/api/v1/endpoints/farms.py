from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.models.farm import Farm, FarmAssessment
from app.schemas.farm import (
    FarmCreate, FarmUpdate, FarmResponse, 
    FarmAssessmentCreate, FarmAssessmentResponse
)
from app.services.risk_assessment_service import risk_assessment_service

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(farm_data: FarmCreate, db: Session = Depends(get_db)):
    """Create a new farm"""
    try:
        # Create farm object
        farm = Farm(
            name=farm_data.name,
            owner_name=farm_data.owner_name,
            location=farm_data.location,
            area_hectares=farm_data.area_hectares,
            soil_type=farm_data.soil_type,
            elevation_m=farm_data.elevation_m,
            slope_percent=farm_data.slope_percent
        )
        
        db.add(farm)
        db.commit()
        db.refresh(farm)
        
        logger.info(f"Created farm {farm.id} for owner {farm.owner_name}")
        return farm
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create farm: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create farm: {str(e)}"
        )

@router.get("/", response_model=List[FarmResponse])
async def get_farms(
    skip: int = 0,
    limit: int = 100,
    owner_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of farms with optional filtering"""
    query = db.query(Farm).filter(Farm.is_active == True)
    
    if owner_name:
        query = query.filter(Farm.owner_name.ilike(f"%{owner_name}%"))
    
    farms = query.offset(skip).limit(limit).all()
    return farms

@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: str, db: Session = Depends(get_db)):
    """Get a specific farm by ID"""
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    return farm

@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: str,
    farm_data: FarmUpdate,
    db: Session = Depends(get_db)
):
    """Update farm information"""
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Update fields
    update_data = farm_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    
    db.commit()
    db.refresh(farm)
    
    logger.info(f"Updated farm {farm_id}")
    return farm

@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(farm_id: str, db: Session = Depends(get_db)):
    """Soft delete a farm"""
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    farm.is_active = False
    db.commit()
    
    logger.info(f"Deleted farm {farm_id}")
    return None

@router.post("/{farm_id}/assessments", response_model=FarmAssessmentResponse)
async def create_farm_assessment(
    farm_id: str,
    assessment_data: FarmAssessmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new farm assessment"""
    # Verify farm exists
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Create assessment
    assessment = FarmAssessment(
        farm_id=farm_id,
        overall_risk_score=assessment_data.overall_risk_score,
        drought_risk_score=assessment_data.drought_risk_score,
        flood_risk_score=assessment_data.flood_risk_score,
        hail_risk_score=assessment_data.hail_risk_score,
        pest_risk_score=assessment_data.pest_risk_score,
        ndvi_value=assessment_data.ndvi_value,
        soil_moisture=assessment_data.soil_moisture,
        temperature_avg=assessment_data.temperature_avg,
        rainfall_total=assessment_data.rainfall_total,
        assessment_notes=assessment_data.assessment_notes
    )
    
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    
    logger.info(f"Created assessment {assessment.id} for farm {farm_id}")
    return assessment

@router.get("/{farm_id}/assessments", response_model=List[FarmAssessmentResponse])
async def get_farm_assessments(
    farm_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get historical assessments for a farm"""
    # Verify farm exists
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    assessments = db.query(FarmAssessment)\
        .filter(FarmAssessment.farm_id == farm_id)\
        .order_by(FarmAssessment.assessment_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return assessments 