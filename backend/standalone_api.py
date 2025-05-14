"""
API d'audit autonome pour DynamoPro
Cette version est entièrement autonome et ne dépend pas des modules existants
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, ConfigDict

app = FastAPI()

# Configurer CORS - Configuration très permissive pour le débogage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permettre toutes les origines
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], # Lister explicitement OPTIONS
    allow_headers=["*"], # Permettre tous les en-têtes
)

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèle SQLAlchemy
class Audit(Base):
    __tablename__ = "audits"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    event_name = Column(String(255), index=True)
    details = Column(Text, nullable=True)  # Stocké comme TEXT pour éviter les problèmes avec JSON

# Dépendance pour obtenir la session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modèles Pydantic
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
    return {"message": "Standalone Audit API"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/db-info")
async def db_info():
    """Affiche des informations sur la connexion à la base de données"""
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
    
    return {
        "database_url_present": db_url != "Non défini",
        "database_url_masked": masked_url,
        "database_url_converted_masked": masked_converted_url,
        "conversion_needed": db_url and db_url.startswith("postgres://")
    }

@app.post("/api/v1/audits", response_model=AuditSchema, status_code=201)
def create_audit_entry(audit_request: AuditCreate, db: Session = Depends(get_db)):
    """Crée une nouvelle entrée d'audit dans la base de données."""
    try:
        # Convertir les détails en JSON string si présents
        details_json = None
        if audit_request.details:
            details_json = json.dumps(audit_request.details)
        
        # Créer un nouvel objet Audit
        db_audit = Audit(
            event_name=audit_request.event_name,
            details=details_json  # Stocké comme TEXT
        )
        
        # Ajouter à la session et commit
        db.add(db_audit)
        db.commit()
        db.refresh(db_audit)
        
        # Reconvertir le TEXT en dict pour la réponse
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

@app.get("/api/v1/audits", response_model=List[AuditSchema])
def get_all_audits(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    """Récupère une liste paginée de tous les audits."""
    try:
        audits = db.query(Audit).offset(skip).limit(limit).all()
        
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
