"""
API de test pour diagnostiquer les problèmes de connexion à la base de données
"""

import os
import sys
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/db-info")
async def db_info():
    """Affiche des informations détaillées sur la connexion à la base de données"""
    db_url = os.getenv("DATABASE_URL", "Non défini")
    
    # Masquer les informations sensibles pour la sécurité
    if db_url != "Non défini":
        # Extraire seulement le type de base de données et le host
        parts = db_url.split("://")
        if len(parts) > 1:
            auth_parts = parts[1].split("@")
            if len(auth_parts) > 1:
                host_parts = auth_parts[1].split("/")
                masked_url = f"{parts[0]}://****:****@{host_parts[0]}/****"
            else:
                masked_url = f"{parts[0]}://****"
        else:
            masked_url = "Format non reconnu"
    else:
        masked_url = "Non défini"
    
    # Convertir postgres:// en postgresql:// si nécessaire
    converted_url = None
    if db_url and db_url.startswith("postgres://"):
        converted_url = db_url.replace("postgres://", "postgresql://", 1)
        masked_converted_url = masked_url.replace("postgres://", "postgresql://", 1)
    else:
        converted_url = db_url
        masked_converted_url = masked_url
    
    result = {
        "database_url_present": db_url != "Non défini",
        "database_url_masked": masked_url,
        "database_url_converted_masked": masked_converted_url,
        "conversion_needed": db_url and db_url.startswith("postgres://"),
        "python_version": sys.version,
        "sqlalchemy_version": "Non disponible"  # Sera mis à jour ci-dessous
    }
    
    # Tester la connexion à la base de données
    if converted_url and converted_url != "Non défini":
        try:
            import sqlalchemy
            result["sqlalchemy_version"] = sqlalchemy.__version__
            
            # Créer un moteur SQLAlchemy avec l'URL convertie
            engine = create_engine(converted_url)
            
            # Tester la connexion
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                result["database_connection"] = "successful"
        except Exception as e:
            result["database_connection"] = "failed"
            result["error"] = str(e)
    
    return result
