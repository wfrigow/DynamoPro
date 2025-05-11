"""
Configuration de la base de données pour l'API de subventions
----------------------------------------------------------
Gère la connexion à la base de données et les sessions
"""

import sys
import os
# Ajouter le répertoire parent au sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Création de l'URL de connexion à la base de données
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Création du moteur de base de données
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

# Création de la session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base déclarative pour les modèles
Base = declarative_base()


# Fonction de dépendance pour obtenir une session de base de données
def get_db():
    """
    Crée une nouvelle session de base de données pour chaque requête
    et la ferme à la fin de la requête.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
