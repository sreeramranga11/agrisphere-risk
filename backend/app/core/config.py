from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Precision Risk for Agriculture"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/agrisphere_risk"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Palantir Foundry
    FOUNDRY_URL: str = "https://your-foundry-instance.palantirfoundry.com"
    FOUNDRY_TOKEN: Optional[str] = None
    FOUNDRY_DATASET_ID: Optional[str] = None
    
    # AIP API
    AIP_API_URL: str = "https://your-aip-instance.palantirfoundry.com"
    AIP_API_TOKEN: Optional[str] = None
    
    # External APIs
    NOAA_API_KEY: Optional[str] = None
    USDA_API_KEY: Optional[str] = None
    SATELLITE_API_KEY: Optional[str] = None
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # AI Model Settings
    MODEL_PATH: str = "./ai-models"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Geospatial
    DEFAULT_CRS: str = "EPSG:4326"
    MAX_POLYGON_AREA: float = 10000.0  # hectares
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True) 