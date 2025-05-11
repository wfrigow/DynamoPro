"""
API de test avec connexion à la base de données
"""

import os
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    """Test simple de connexion à la base de données"""
    try:
        # Exécuter une requête simple pour vérifier la connexion
        db.execute("SELECT 1")
        return {"database_connection": "successful"}
    except Exception as e:
        return {"database_connection": "failed", "error": str(e)}
