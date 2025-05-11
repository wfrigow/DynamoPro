"""
Configuration de l'API de subventions
------------------------------------
Paramètres de configuration pour l'API de subventions
"""

import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Paramètres de configuration pour l'API de subventions"""
    
    # Configuration générale
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
    
    # Configuration de l'authentification
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Configuration de la base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./subsidy.db")
    
    # Configuration des services externes
    RECOMMENDATION_SERVICE_URL: str = os.getenv("RECOMMENDATION_SERVICE_URL", "http://localhost:8002/api")
    OPTIMIZATION_SERVICE_URL: str = os.getenv("OPTIMIZATION_SERVICE_URL", "http://localhost:8003/api")
    GREEN_PASSPORT_SERVICE_URL: str = os.getenv("GREEN_PASSPORT_SERVICE_URL", "http://localhost:8004/api")
    
    # Configuration de l'API OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_TEST_MODE: bool = os.getenv("LLM_TEST_MODE", "True").lower() in ("true", "1", "t")
    
    # Configuration CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://localhost:8003",
        "http://localhost:8004",
        "http://localhost:8010",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance singleton des paramètres
settings = Settings()
