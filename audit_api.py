"""
API d'audit simplifiée pour DynamoPro
------------------------------------
Cette API expose les routes nécessaires pour gérer les audits et générer des recommandations.
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Création de l'application FastAPI
app = FastAPI(
    title="DynamoPro Audit API",
    description="API pour gérer les audits et générer des recommandations",
    version="1.0.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemin vers le fichier de stockage des audits
AUDITS_FILE = os.path.join(os.path.dirname(__file__), "audits.json")

# S'assurer que le fichier existe
if not os.path.exists(AUDITS_FILE):
    with open(AUDITS_FILE, 'w', encoding='utf-8') as f:
        f.write('{}')

# Modèles de données
class AuditRequest(BaseModel):
    user_id: str
    audit_data: Dict[str, Any]

class AuditResponse(BaseModel):
    id: str
    userId: str
    createdAt: str
    updatedAt: str
    auditData: Dict[str, Any]

class AuditSummary(BaseModel):
    id: str
    userId: str
    createdAt: str

# Fonctions utilitaires
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

# Routes API
@app.post("/api/v1/audits", response_model=AuditResponse)
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

@app.get("/api/v1/audits", response_model=List[AuditSummary])
async def get_user_audits(user_id: str):
    """Récupère tous les audits d'un utilisateur"""
    # Charger les audits
    audits = load_audits()
    
    # Récupérer les audits de l'utilisateur
    user_audits = audits.get(user_id, [])
    
    return user_audits

@app.post("/api/v1/detailed-recommendations")
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
        ],
        "waste": [
            {
                "title": "Compostage domestique",
                "description": "Le compostage peut réduire vos déchets ménagers de 30%.",
                "cost": "50-200",
                "savings": "20-50",
                "roi": "2-4",
                "subsidies": ["Prime communale pour le compostage"]
            }
        ],
        "biodiversity": [
            {
                "title": "Toiture végétalisée",
                "description": "Une toiture végétalisée améliore l'isolation et favorise la biodiversité.",
                "cost": "5000-10000",
                "savings": "300-600",
                "roi": "15-20",
                "subsidies": ["Prime régionale pour les toitures vertes"]
            }
        ]
    }
    
    return recommendations

# Point d'entrée pour l'exécution directe
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("audit_api:app", host="0.0.0.0", port=8024, reload=True)
