from fastapi import APIRouter

from app.api.v1.endpoints import farms, risk_assessment, weather, damage_assessment

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(farms.router, prefix="/farms", tags=["farms"])
api_router.include_router(risk_assessment.router, prefix="/risk", tags=["risk-assessment"])
api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
api_router.include_router(damage_assessment.router, prefix="/damage", tags=["damage-assessment"]) 