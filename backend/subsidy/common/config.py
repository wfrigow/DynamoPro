"""
Configuration partagée pour l'application
"""

from pydantic import BaseSettings, Field
from typing import List


class Settings(BaseSettings):
    """Paramètres de configuration de l'application"""
    
    # Préfixe de l'API
    API_PREFIX: str = ""
    
    # Configuration CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Configuration de la base de données
    DATABASE_URL: str = "sqlite:///./subsidy.db"
    
    # Clé secrète pour JWT
    SECRET_KEY: str = "dynamopro-secret-key-for-development"
    
    # Algorithme pour JWT
    ALGORITHM: str = "HS256"
    
    # Durée de validité du token JWT (en minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuration OpenAI
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"


# Instance des paramètres
settings = Settings()
