"""
Configuration centralisée pour tous les composants de DynamoPro
--------------------------------------------------------------
Ce module gère le chargement et l'accès à la configuration pour tous les services
"""

import os
from typing import Any, Dict, Optional
import sys
from pathlib import Path

# Chargement explicite du fichier .env
from dotenv import load_dotenv

# Essayer de charger .env depuis le répertoire courant et le répertoire parent
env_paths = [
    Path(os.getcwd()) / ".env",
    Path(os.getcwd()).parent / ".env",
    Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "subsidy" / ".env"
]

for env_path in env_paths:
    if env_path.exists():
        print(f"Chargement des variables d'environnement depuis {env_path}")
        load_dotenv(dotenv_path=str(env_path))
        break

from decouple import config as decouple_config


class Settings:
    """Classe centralisant la configuration de l'application"""
    
    # Informations de base
    APP_NAME: str = "DynamoPro"
    VERSION: str = "0.1.0"
    
    # Environnement
    ENV: str = decouple_config("ENV", default="development")
    DEBUG: bool = ENV == "development"
    
    # Sécurité
    SECRET_KEY: str = decouple_config("SECRET_KEY", default="changeme_in_production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = decouple_config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # Base de données
    DATABASE_URL: str = decouple_config(
        "DATABASE_URL", 
        default="postgresql://postgres:postgres@localhost:5432/dynamopro"
    )
    
    # Redis (pour files d'attente et caching)
    REDIS_URL: str = decouple_config("REDIS_URL", default="redis://localhost:6379/0")
    
    # MongoDB (pour données non structurées)
    MONGODB_URL: str = decouple_config("MONGODB_URL", default="mongodb://localhost:27017/dynamopro")
    
    # OpenAI et LLM
    OPENAI_API_KEY: str = decouple_config("OPENAI_API_KEY", default="")
    DEFAULT_LLM_MODEL: str = "gpt-4"
    
    # Services URLs (pour communication inter-services)
    AGENT_MANAGER_URL: str = decouple_config("AGENT_MANAGER_URL", default="http://localhost:8000")
    DATA_COLLECTOR_URL: str = decouple_config("DATA_COLLECTOR_URL", default="http://localhost:8001")
    OPTIMIZER_URL: str = decouple_config("OPTIMIZER_URL", default="http://localhost:8002")
    SUBSIDY_URL: str = decouple_config("SUBSIDY_URL", default="http://localhost:8003")
    PROCUREMENT_URL: str = decouple_config("PROCUREMENT_URL", default="http://localhost:8004")
    MONITORING_URL: str = decouple_config("MONITORING_URL", default="http://localhost:8005")
    
    # Intégrations externes
    STRIPE_API_KEY: str = decouple_config("STRIPE_API_KEY", default="")
    
    # Paramètres spécifiques de la Belgique
    BELGIUM_REGIONS = ["wallonie", "flandre", "bruxelles"]
    DEFAULT_LANGUAGE = "fr"  # Options: fr, nl, de, en
    
    def get_service_url(self, service_name: str) -> str:
        """Récupère l'URL d'un service par son nom"""
        mapping = {
            "agent-manager": self.AGENT_MANAGER_URL,
            "data-collector": self.DATA_COLLECTOR_URL,
            "optimizer": self.OPTIMIZER_URL,
            "subsidy": self.SUBSIDY_URL,
            "procurement": self.PROCUREMENT_URL,
            "monitoring": self.MONITORING_URL,
        }
        return mapping.get(service_name, "")


# Instance de configuration globale
settings = Settings()
