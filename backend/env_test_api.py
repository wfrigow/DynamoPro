"""
API de test pour afficher les variables d'environnement
"""

import os
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/env")
async def env_info():
    """Affiche des informations sur les variables d'environnement (masquées pour la sécurité)"""
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
    
    return {
        "database_url_present": db_url != "Non défini",
        "database_url_masked": masked_url,
        "python_version": os.getenv("PYTHON_VERSION", "Non défini"),
        "dyno": os.getenv("DYNO", "Non défini"),
        "port": os.getenv("PORT", "Non défini")
    }
