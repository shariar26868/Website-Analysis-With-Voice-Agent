"""
Configuration and Environment Variables
All values must be set in .env file
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application Settings - All values loaded from .env"""
    
    # ===== App Settings =====
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # ===== MongoDB =====
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "trufindai"
    
    # ===== Twilio =====
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    # ===== OpenAI =====
    OPENAI_API_KEY: str
    
    # ===== PageSpeed Insights =====
    PAGESPEED_API_KEY: str
    
    # ===== AWS S3 (Optional) =====
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_BUCKET_NAME: str = "trufindai-recordings"
    AWS_REGION: str = "us-east-1"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Initialize settings
try:
    settings = Settings()
    print(f"✅ Configuration loaded successfully")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   MongoDB: {settings.MONGODB_URL}")
    print(f"   Twilio: {settings.TWILIO_PHONE_NUMBER}")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    print(f"⚠️  Make sure .env file exists with all required variables")
    raise


# MongoDB connection
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    """Database connection handler"""
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    def get_client(cls):
        """Get MongoDB client (singleton pattern)"""
        if cls.client is None:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        return cls.client
    
    @classmethod
    def get_database(cls):
        """Get database instance"""
        client = cls.get_client()
        return client[settings.MONGODB_DB_NAME]
    
    @classmethod
    def close(cls):
        """Close database connection"""
        if cls.client:
            cls.client.close()
            cls.client = None


def get_db():
    """Get database instance (FastAPI dependency)"""
    return Database.get_database()