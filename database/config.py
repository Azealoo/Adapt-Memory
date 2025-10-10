"""
Database configuration for Adapt-Memory
Supports both local PostgreSQL and Neon cloud database
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    
    # Database connection settings
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "adapt_memory"
    db_user: str = "postgres"
    db_password: str = ""
    
    # Neon cloud database URL (if using Neon)
    neon_database_url: Optional[str] = None
    
    # Connection pool settings
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_prefix = "ADAPT_"

# Global settings instance
settings = DatabaseSettings()

def get_database_url() -> str:
    """Get the appropriate database URL based on configuration"""
    if settings.neon_database_url:
        return settings.neon_database_url
    
    return f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

def create_database_engine():
    """Create SQLAlchemy engine with appropriate configuration"""
    database_url = get_database_url()
    
    engine_kwargs = {
        "pool_size": settings.pool_size,
        "max_overflow": settings.max_overflow,
        "pool_timeout": settings.pool_timeout,
        "pool_recycle": settings.pool_recycle,
    }
    
    # Add SSL settings for production/cloud databases
    if settings.environment == "production" or "neon" in database_url:
        engine_kwargs["connect_args"] = {"sslmode": "require"}
    
    return create_engine(database_url, **engine_kwargs)

# Create engine and session factory
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
