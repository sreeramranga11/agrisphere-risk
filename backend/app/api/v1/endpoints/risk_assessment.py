from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.models.farm import Farm, FarmAssessment
from app.schemas.farm import RiskAssessmentRequest, RiskAssessmentResponse
from app.services.risk_assessment_service import risk_assessment_service

logger = structlog.get_logger()
router = APIRouter()

@router.post("/assess/{farm_id}", response_model=RiskAssessmentResponse)
async def assess_farm_risk(
    farm_id: str,
    request: RiskAssessmentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Perform comprehensive risk assessment for a farm"""
    # Get farm
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    try:
        # Perform risk assessment
        assessment = await risk_assessment_service.assess_farm_risk(farm, request)
        
        # Save assessment to database in background
        background_tasks.add_task(
            _save_assessment_to_db,
            farm_id=farm_id,
            assessment=assessment,
            db=db
        )
        
        logger.info(f"Risk assessment completed for farm {farm_id}")
        return assessment
        
    except Exception as e:
        logger.error(f"Risk assessment failed for farm {farm_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment failed: {str(e)}"
        )

@router.get("/assess/{farm_id}/latest", response_model=RiskAssessmentResponse)
async def get_latest_assessment(farm_id: str, db: Session = Depends(get_db)):
    """Get the latest risk assessment for a farm"""
    # Get farm
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Get latest assessment
    latest_assessment = db.query(FarmAssessment)\
        .filter(FarmAssessment.farm_id == farm_id)\
        .order_by(FarmAssessment.assessment_date.desc())\
        .first()
    
    if not latest_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No assessments found for this farm"
        )
    
    # Convert to response format
    return RiskAssessmentResponse(
        farm_id=farm_id,
        assessment_date=latest_assessment.assessment_date,
        overall_risk_score=latest_assessment.overall_risk_score,
        risk_breakdown={
            "drought": latest_assessment.drought_risk_score or 0,
            "flood": latest_assessment.flood_risk_score or 0,
            "hail": latest_assessment.hail_risk_score or 0,
            "pest": latest_assessment.pest_risk_score or 0
        },
        recommendations=[],  # Would need to be stored separately
        confidence_score=latest_assessment.confidence_score or 0.8,
        data_sources=["database"],
        premium_suggestion=None
    )

@router.get("/assess/{farm_id}/history", response_model=List[RiskAssessmentResponse])
async def get_assessment_history(
    farm_id: str,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get historical risk assessments for a farm"""
    # Get farm
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found"
        )
    
    # Get assessments
    assessments = db.query(FarmAssessment)\
        .filter(FarmAssessment.farm_id == farm_id)\
        .order_by(FarmAssessment.assessment_date.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    # Convert to response format
    return [
        RiskAssessmentResponse(
            farm_id=farm_id,
            assessment_date=assessment.assessment_date,
            overall_risk_score=assessment.overall_risk_score,
            risk_breakdown={
                "drought": assessment.drought_risk_score or 0,
                "flood": assessment.flood_risk_score or 0,
                "hail": assessment.hail_risk_score or 0,
                "pest": assessment.pest_risk_score or 0
            },
            recommendations=[],
            confidence_score=assessment.confidence_score or 0.8,
            data_sources=["database"],
            premium_suggestion=None
        )
        for assessment in assessments
    ]

@router.post("/assess/batch", response_model=List[RiskAssessmentResponse])
async def assess_multiple_farms(
    farm_ids: List[str],
    request: RiskAssessmentRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Perform risk assessment for multiple farms"""
    if len(farm_ids) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 10 farms can be assessed in a single request"
        )
    
    assessments = []
    
    for farm_id in farm_ids:
        # Get farm
        farm = db.query(Farm).filter(Farm.id == farm_id, Farm.is_active == True).first()
        if not farm:
            logger.warning(f"Farm {farm_id} not found, skipping")
            continue
        
        try:
            # Perform assessment
            assessment = await risk_assessment_service.assess_farm_risk(farm, request)
            assessments.append(assessment)
            
            # Save to database in background
            background_tasks.add_task(
                _save_assessment_to_db,
                farm_id=farm_id,
                assessment=assessment,
                db=db
            )
            
        except Exception as e:
            logger.error(f"Risk assessment failed for farm {farm_id}: {e}")
            # Continue with other farms
    
    return assessments

@router.get("/portfolio/summary")
async def get_portfolio_summary(db: Session = Depends(get_db)):
    """Get summary statistics for all farms in portfolio"""
    # Get all active farms
    farms = db.query(Farm).filter(Farm.is_active == True).all()
    
    if not farms:
        return {
            "total_farms": 0,
            "total_area_hectares": 0,
            "average_risk_score": 0,
            "risk_distribution": {},
            "total_premium": 0
        }
    
    # Calculate statistics
    total_farms = len(farms)
    total_area = sum(farm.area_hectares for farm in farms)
    total_premium = sum(farm.premium_amount or 0 for farm in farms)
    
    # Risk distribution
    risk_scores = [farm.risk_score for farm in farms if farm.risk_score is not None]
    average_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0
    
    risk_distribution = {
        "low": len([r for r in risk_scores if r < 0.3]),
        "medium": len([r for r in risk_scores if 0.3 <= r < 0.7]),
        "high": len([r for r in risk_scores if r >= 0.7])
    }
    
    return {
        "total_farms": total_farms,
        "total_area_hectares": total_area,
        "average_risk_score": average_risk,
        "risk_distribution": risk_distribution,
        "total_premium": total_premium
    }

async def _save_assessment_to_db(farm_id: str, assessment: RiskAssessmentResponse, db: Session):
    """Save assessment to database (background task)"""
    try:
        db_assessment = FarmAssessment(
            farm_id=farm_id,
            overall_risk_score=assessment.overall_risk_score,
            drought_risk_score=assessment.risk_breakdown.get("drought"),
            flood_risk_score=assessment.risk_breakdown.get("flood"),
            hail_risk_score=assessment.risk_breakdown.get("hail"),
            pest_risk_score=assessment.risk_breakdown.get("pest"),
            confidence_score=assessment.confidence_score,
            assessment_notes="AI-generated assessment"
        )
        
        db.add(db_assessment)
        db.commit()
        
        logger.info(f"Saved assessment to database for farm {farm_id}")
        
    except Exception as e:
        logger.error(f"Failed to save assessment to database: {e}")
        db.rollback() 