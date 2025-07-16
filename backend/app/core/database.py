from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import redis
import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Database engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database tables and extensions"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Enable PostGIS extension if using PostgreSQL
        with engine.connect() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS postgis")
            conn.commit()
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

def get_redis():
    """Get Redis client"""
    return redis_client 