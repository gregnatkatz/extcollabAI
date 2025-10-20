"""
Configuration management for ContosoHealth Research Platform.
Loads settings from environment variables and Azure Key Vault in production.
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    MOCK_AUTH_MODE: bool = os.getenv("MOCK_AUTH_MODE", "true").lower() == "true"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "mock-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    
    ENTRA_TENANT_ID: str = os.getenv("ENTRA_TENANT_ID", "mock-tenant-id")
    ENTRA_CLIENT_ID: str = os.getenv("ENTRA_CLIENT_ID", "mock-client-id")
    ENTRA_CLIENT_SECRET: str = os.getenv("ENTRA_CLIENT_SECRET", "mock-client-secret")
    ENTRA_AUTHORITY: str = f"https://login.microsoftonline.com/{os.getenv('ENTRA_TENANT_ID', 'mock-tenant-id')}"
    
    ALLOWED_ORIGINS: list = os.getenv(
        "ALLOWED_ORIGINS",
        "https://research.contosohealth.com,https://research-portal-2fbfvjbt.devinapps.com"
    ).split(",")
    
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_EXPORTS: str = os.getenv("AZURE_STORAGE_CONTAINER_EXPORTS", "exports")
    AZURE_STORAGE_CONTAINER_AUDIT: str = os.getenv("AZURE_STORAGE_CONTAINER_AUDIT", "audit-logs")
    
    AZURE_SUBSCRIPTION_ID: Optional[str] = os.getenv("AZURE_SUBSCRIPTION_ID")
    AZURE_RESOURCE_GROUP: Optional[str] = os.getenv("AZURE_RESOURCE_GROUP")
    
    FABRIC_CAPACITY_ID: Optional[str] = os.getenv("FABRIC_CAPACITY_ID")
    FABRIC_API_BASE: str = "https://api.fabric.microsoft.com/v1"
    
    ML_WORKSPACE_NAME: Optional[str] = os.getenv("ML_WORKSPACE_NAME")
    ML_REGION: str = os.getenv("ML_REGION", "eastus")
    
    FOUNDRY_PROJECT_CONNECTION_STRING: Optional[str] = os.getenv("FOUNDRY_PROJECT_CONNECTION_STRING")
    
    EMAIL_FROM_ADDRESS: str = os.getenv("EMAIL_FROM_ADDRESS", "noreply@contosohealth.com")
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    
    EXPORT_SAS_TOKEN_EXPIRY_HOURS: int = int(os.getenv("EXPORT_SAS_TOKEN_EXPIRY_HOURS", "24"))
    EXPORT_AUTO_DELETE_HOURS: int = int(os.getenv("EXPORT_AUTO_DELETE_HOURS", "24"))
    
    AUDIT_LOG_RETENTION_YEARS: int = int(os.getenv("AUDIT_LOG_RETENTION_YEARS", "7"))
    
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production"""
        return cls.ENVIRONMENT == "production"
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development"""
        return cls.ENVIRONMENT == "development"
    
    @classmethod
    def validate(cls):
        """Validate required settings for production"""
        if cls.is_production():
            required_settings = [
                ("ENTRA_TENANT_ID", cls.ENTRA_TENANT_ID),
                ("ENTRA_CLIENT_ID", cls.ENTRA_CLIENT_ID),
                ("ENTRA_CLIENT_SECRET", cls.ENTRA_CLIENT_SECRET),
                ("DATABASE_URL", cls.DATABASE_URL),
                ("AZURE_STORAGE_CONNECTION_STRING", cls.AZURE_STORAGE_CONNECTION_STRING),
                ("AZURE_SUBSCRIPTION_ID", cls.AZURE_SUBSCRIPTION_ID),
                ("AZURE_RESOURCE_GROUP", cls.AZURE_RESOURCE_GROUP),
            ]
            
            missing = [name for name, value in required_settings if not value or value.startswith("mock-")]
            
            if missing:
                raise ValueError(
                    f"Missing required production settings: {', '.join(missing)}. "
                    f"Please configure these in Azure Key Vault or environment variables."
                )
            
            if cls.MOCK_AUTH_MODE:
                raise ValueError(
                    "MOCK_AUTH_MODE must be disabled in production. "
                    "Set MOCK_AUTH_MODE=false in environment variables."
                )

settings = Settings()

if settings.is_production():
    settings.validate()
