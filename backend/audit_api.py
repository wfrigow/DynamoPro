"""
API d'audit simplifiée pour DynamoPro
------------------------------------
Cette API expose les routes nécessaires pour gérer les audits et générer des recommandations.
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.audit_model import Audit as AuditModel

app = FastAPI(
    title="DynamoPro Audit API",
    description="API pour gérer les audits et générer des recommandations",
    version="1.0.0"
)

origins = [
    "https://dynamopro-app.windsurf.build",
    # Vous pouvez ajouter d'autres origines ici si nécessaire, par exemple:
    # "http://localhost:3000", # Si votre frontend local tourne sur le port 3000
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditBase(BaseModel):
    event_name: str
    details: Optional[Dict[str, Any]] = None

class AuditCreate(AuditBase):
    pass

class AuditSchema(AuditBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

@app.post("/api/v1/audits", response_model=AuditSchema, status_code=201)
def create_audit_entry(audit_request: AuditCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle entrée d'audit dans la base de données."""
    db_audit = AuditModel(
        event_name=audit_request.event_name,
        details=audit_request.details
    )
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit

@app.get("/api/v1/audits", response_model=List[AuditSchema])
def get_all_audits(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Récupère une liste paginée de tous les audits."""
    audits = db.query(AuditModel).offset(skip).limit(limit).all()
    return audits

@app.post("/api/v1/detailed-recommendations")
async def generate_detailed_recommendations(audit_data: dict):
    """Génère des recommandations détaillées basées sur les données d'audit"""
    # Placeholder logic
    recommendations = {
        "energy": [
            {"recommendation": "Vérifiez l'isolation de votre grenier.", "priority": "Haute"},
            {"recommendation": "Passez à des ampoules LED.", "priority": "Moyenne"}
        ],
        "water": [
            {"recommendation": "Réparez les fuites de robinet.", "priority": "Haute"}
        ]
    }
    # Ici, vous pourriez avoir une logique plus complexe pour générer des recommandations
    # basées sur `audit_data`
    return recommendations

# Point d'entrée pour l'exécution directe
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("audit_api:app", host="0.0.0.0", port=8024, reload=True)
