"""
API d'audit autonome pour DynamoPro
Cette version est entièrement autonome et ne dépend pas des modules existants
"""

import os
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, ConfigDict

# Import des routers externes
import httpx

# Router LLM proxy
try:
    from routes.llm_proxy import router as llm_router
    HAS_LLM_PROXY = True
except (ImportError, ModuleNotFoundError):
    print("AVERTISSEMENT: Module LLM proxy non disponible. Les fonctionnalités IA seront limitées.")
    HAS_LLM_PROXY = False

# Router Audit API
try:
    from routes.audit_api import router as audit_router
    HAS_AUDIT_API = True
except (ImportError, ModuleNotFoundError):
    print("AVERTISSEMENT: Module Audit API non disponible. Les fonctionnalités d'audit seront limitées.")
    HAS_AUDIT_API = False

app = FastAPI(title="DynamoPro API", description="API pour l'application DynamoPro")

# Configurer CORS - Configuration très permissive pour le débogage
# Liste des origines permises
allowed_origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost:8003",
    "https://dynamopro-app.windsurf.build",
    "https://dynamopro-app-b0d7b735d20c.netlify.app",  # Si vous utilisez Netlify
    # Ajouter d'autres origines au besoin
]

# Configuration CORS avec des origines spécifiques
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    # Important: Exposer ces en-têtes pour les requêtes cross-origin
    expose_headers=["Content-Type", "Authorization"],
)

# Middleware pour rediriger les routes et assurer la compatibilité API
@app.middleware("http")
async def route_compatibility_middleware(request: Request, call_next):
    path = request.url.path
    original_path = path
    redirect_needed = False
    
    # 1. Rediriger /audits vers /api/audits
    if path.startswith("/audits") and not path.startswith("/api/"):
        path = f"/api{path}"
        redirect_needed = True
    
    # 2. Rediriger /api/audits vers /api/v1/audits si nécessaire
    # Exceptions : ne pas rediriger si c'est déjà un chemin v1 ou si c'est un endpoint spécifique
    if path.startswith("/api/audits") and not path.startswith("/api/v1/"):
        path = path.replace("/api/audits", "/api/v1/audits")
        redirect_needed = True
        
    # Si une redirection est nécessaire, renvoyer la réponse appropriée
    if redirect_needed:
        url = str(request.url).replace(original_path, path)
        print(f"Redirection: {original_path} -> {path}")
        return RedirectResponse(url=url)
        
    # Journaliser tous les chemins d'accès pour le débogage
    print(f"Accès à: {path}")
    
    # Continuer normalement pour les autres chemins    
    response = await call_next(request)
    return response

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
    return {
        "message": "DynamoPro API",
        "version": "1.0.0",
        "features": {
            "llm_proxy": HAS_LLM_PROXY,
            "audit_api": HAS_AUDIT_API
        },
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    # Vérifier si la clé API OpenAI est configurée
    openai_status = "configured" if os.getenv("OPENAI_API_KEY") else "missing"
    return {"status": "ok", "openai_api": openai_status}

# Inclure les routers disponibles
if HAS_LLM_PROXY:
    app.include_router(llm_router)
    print("LLM proxy router intégré avec succès.")

if HAS_AUDIT_API:
    app.include_router(audit_router)
    print("Audit API router intégré avec succès.")

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
