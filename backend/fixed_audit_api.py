"""
Version corrigée de l'API d'audit pour DynamoPro avec imports corrects
"""

import sys
import os
import json
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

# Ajouter le répertoire parent au chemin d'importation Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Maintenant les imports fonctionneront correctement
from backend.app.db.session import get_db
from backend.app.models.audit_model import Audit as AuditModel

app = FastAPI()

# Modèles Pydantic simplifiés
class AuditBase(BaseModel):
    event_name: str
    details: Optional[Dict[str, Any]] = None

class AuditCreate(AuditBase):
    pass

class AuditSchema(AuditBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

@app.get("/")
async def root():
    return {"message": "Fixed Audit API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/api/v1/audits", response_model=AuditSchema, status_code=201)
def create_audit_entry(audit_request: AuditCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle entrée d'audit dans la base de données."""
    try:
        # Créer un nouvel objet Audit
        db_audit = AuditModel(
            event_name=audit_request.event_name,
            details=audit_request.details
        )
        
        # Ajouter à la session et commit
        db.add(db_audit)
        db.commit()
        db.refresh(db_audit)
        
        return db_audit
    except Exception as e:
        # Log l'erreur et renvoyer une réponse d'erreur
        print(f"Erreur lors de la création de l'audit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'audit: {str(e)}")

@app.get("/api/v1/audits", response_model=List[AuditSchema])
def get_all_audits(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Récupère une liste paginée de tous les audits."""
    try:
        audits = db.query(AuditModel).offset(skip).limit(limit).all()
        return audits
    except Exception as e:
        # Log l'erreur et renvoyer une réponse d'erreur
        print(f"Erreur lors de la récupération des audits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des audits: {str(e)}")
