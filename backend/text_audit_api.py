"""
Version simplifiée de l'API d'audit pour DynamoPro avec stockage en TEXT
"""

import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.db.session import get_db
from app.models.audit_model import Audit as AuditModel
from pydantic import BaseModel, ConfigDict
from starlette.responses import Response

app = FastAPI()

# Configurer CORS - Configuration très permissive pour le débogage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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
    return {"message": "Text Audit API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.options("/health")
async def options_health():
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

@app.post("/api/v1/audits", response_model=AuditSchema, status_code=201)
def create_audit_entry(audit_request: AuditCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle entrée d'audit dans la base de données."""
    try:
        # Convertir les détails en JSON string si présents
        details_json = None
        if audit_request.details:
            details_json = json.dumps(audit_request.details)
        
        # Créer un nouvel objet Audit
        db_audit = AuditModel(
            event_name=audit_request.event_name,
            details=details_json  # Stocké comme TEXT
        )
        
        # Ajouter à la session et commit
        db.add(db_audit)
        db.commit()
        db.refresh(db_audit)
        
        # Reconvertir le TEXT en dict pour la réponse si nécessaire
        if db_audit.details and isinstance(db_audit.details, str):
            try:
                db_audit.details = json.loads(db_audit.details)
            except:
                pass
        
        return db_audit
    except Exception as e:
        # Log l'erreur et renvoyer une réponse d'erreur
        print(f"Erreur lors de la création de l'audit: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de l'audit: {str(e)}")

@app.options("/api/v1/audits")
async def options_audits():
    return Response(status_code=200, headers={
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "*",
    })

@app.get("/api/v1/audits", response_model=List[AuditSchema])
def get_all_audits(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Récupère une liste paginée de tous les audits."""
    try:
        audits = db.query(AuditModel).offset(skip).limit(limit).all()
        
        # Convertir les détails TEXT en dict pour chaque audit
        for audit in audits:
            if audit.details and isinstance(audit.details, str):
                try:
                    audit.details = json.loads(audit.details)
                except:
                    pass
        
        return audits
    except Exception as e:
        # Log l'erreur et renvoyer une réponse d'erreur
        print(f"Erreur lors de la récupération des audits: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des audits: {str(e)}")
