"""
Script de démarrage du serveur API enrichi pour les subventions.
Intègre les nouvelles routes avec support multilingue et données enrichies.
"""

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .api.enriched_subsidy_routes import router as enriched_subsidy_router
from .api.integration_routes import router as integration_router
from .api.green_passport_routes import router as green_passport_router
from .api.auth_routes import router as auth_router
from .api.application_routes import router as application_router
from .api.audit_routes import router as audit_router

# Import des routes d'audit modifiées (sans authentification)
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import uuid
from datetime import datetime
import json
import os
from pydantic import BaseModel

# Chemin vers le fichier de stockage des audits
AUDITS_FILE = os.path.join(os.path.dirname(__file__), "data/audits.json")

# S'assurer que le répertoire data existe
os.makedirs(os.path.dirname(AUDITS_FILE), exist_ok=True)

# Créer le fichier s'il n'existe pas
if not os.path.exists(AUDITS_FILE):
    with open(AUDITS_FILE, 'w', encoding='utf-8') as f:
        f.write('{}')

# Classe pour les requêtes d'audit
class AuditRequest(BaseModel):
    user_id: str
    audit_data: Dict[str, Any]

# Classe pour les réponses d'audit
class AuditResponse(BaseModel):
    id: str
    userId: str
    createdAt: str
    updatedAt: str
    auditData: Dict[str, Any]

# Classe pour les résumés d'audit
class AuditSummary(BaseModel):
    id: str
    userId: str
    createdAt: str

# Fonctions de gestion des audits
def load_audits():
    """Charge les audits depuis le fichier"""
    try:
        if os.path.exists(AUDITS_FILE):
            with open(AUDITS_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        else:
            return {}
    except Exception as e:
        print(f"Erreur lors du chargement des audits: {e}")
        return {}

def save_audits(audits):
    """Sauvegarde les audits dans le fichier"""
    try:
        with open(AUDITS_FILE, 'w', encoding='utf-8') as f:
            json.dump(audits, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des audits: {e}")
from .config import settings
from .auth import get_current_active_subsidy_user

# Création de l'application FastAPI
app = FastAPI(
    title="API de Subventions Enrichies",
    description="API pour accéder aux données de subventions enrichies",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs
app.include_router(auth_router, prefix=settings.API_PREFIX, tags=["authentication"])

# Ajouter le routeur d'audit (sans authentification)
app.include_router(audit_router, prefix="", tags=["audits"])

# Route pour créer un nouvel audit
@audit_router.post("", response_model=AuditResponse)
async def create_audit(request: AuditRequest):
    """Crée un nouvel audit vocal"""
    # Créer l'audit
    audit_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    audit = {
        "id": audit_id,
        "userId": request.user_id,
        "createdAt": now,
        "updatedAt": now,
        "auditData": request.audit_data
    }
    
    # Charger les audits existants
    audits = load_audits()
    
    # Ajouter l'audit à la collection
    if request.user_id not in audits:
        audits[request.user_id] = []
    
    audits[request.user_id].append(audit)
    save_audits(audits)
    
    return audit

# Route pour récupérer les audits d'un utilisateur
@audit_router.get("", response_model=List[AuditSummary])
async def get_user_audits(user_id: str):
    """Récupère tous les audits d'un utilisateur"""
    # Charger les audits
    audits = load_audits()
    
    # Récupérer les audits de l'utilisateur
    user_audits = audits.get(user_id, [])
    
    return user_audits

# Route pour générer des recommandations détaillées
@audit_router.post("/detailed-recommendations")
async def generate_detailed_recommendations(audit_data: Dict[str, Any]):
    """Génère des recommandations détaillées basées sur les données d'audit"""
    # Générer des recommandations de base (pour les tests)
    recommendations = {
        "energy": [
            {
                "title": "Installation de panneaux solaires",
                "description": "Les panneaux solaires peuvent réduire votre facture d'électricité jusqu'à 70%.",
                "cost": "8000-12000",
                "savings": "800-1200",
                "roi": "10-15",
                "subsidies": ["Prime Habitation Wallonie", "Réduction fiscale fédérale"]
            },
            {
                "title": "Pompe à chaleur",
                "description": "Une pompe à chaleur est 3 à 4 fois plus efficace qu'un système de chauffage traditionnel.",
                "cost": "10000-15000",
                "savings": "900-1500",
                "roi": "7-10",
                "subsidies": ["Prime Habitation Wallonie", "Prime Énergie"]
            }
        ],
        "water": [
            {
                "title": "Système de récupération d'eau de pluie",
                "description": "Un système de récupération d'eau de pluie peut réduire votre consommation d'eau potable de 50%.",
                "cost": "3000-5000",
                "savings": "200-400",
                "roi": "12-15",
                "subsidies": ["Prime communale pour la récupération d'eau de pluie"]
            }
        ]
    }
    
    return recommendations

# Routes publiques (sans authentification)
app.include_router(
    enriched_subsidy_router, 
    prefix=f"{settings.API_PREFIX}/subsidies", 
    tags=["subsidies"]
)

# Routes protégées (avec authentification)
app.include_router(
    integration_router, 
    prefix=f"{settings.API_PREFIX}/integrations", 
    tags=["integration"],
    dependencies=[Depends(get_current_active_subsidy_user)]
)
app.include_router(
    green_passport_router, 
    prefix=f"{settings.API_PREFIX}/green-passport", 
    tags=["green-passport"],
    dependencies=[Depends(get_current_active_subsidy_user)]
)
app.include_router(
    application_router,
    prefix=f"{settings.API_PREFIX}",
    tags=["applications"],
    dependencies=[Depends(get_current_active_subsidy_user)]
)

# Route racine pour vérifier que l'API fonctionne
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API de Subventions Enrichies", "docs": f"{settings.API_PREFIX}/docs"}

@app.get(settings.API_PREFIX)
async def api_root():
    return {
        "message": "API de Subventions Enrichies", 
        "version": settings.API_VERSION,
        "features": [
            "Données de subventions enrichies",
            "Support multilingue (FR/NL)",
            "Intégration avec le service de recommandations",
            "Intégration avec le service d'optimisation",
            "Intégration avec le service de passeport vert",
            "Gestion des applications de subventions",
            "Authentification JWT"
        ]
    }

# Point d'entrée pour exécuter le serveur
if __name__ == "__main__":
    print("Démarrage du serveur API de subventions DynamoPro...")
    print("Documentation disponible à l'adresse: http://localhost:8010/docs")
    uvicorn.run(app, host="0.0.0.0", port=8010)
