#!/usr/bin/env python3
"""
Serveur de test pour l'endpoint de recommandations
"""
import asyncio
import json
import os
import sys
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

# Ajouter le répertoire backend au chemin d'importation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer le moteur de recommandations
from subsidy.integrations.recommendation_engine import RecommendationEngine

# Définir la clé API OpenAI
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY_REMOVED"

# Créer l'application FastAPI
app = FastAPI(
    title="API de Test pour Recommandations",
    description="API de test pour l'endpoint de recommandations",
    version="0.1.0"
)

# Configuration CORS pour permettre les requêtes depuis le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autoriser toutes les origines pour le développement
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,  # Mettre en cache les résultats des requêtes préliminaires pendant 24 heures
)

# Créer une instance du moteur de recommandations
recommendation_engine = RecommendationEngine()

# Endpoint de recommandations - exactement comme le frontend l'attend
@app.post("/api/v1/detailed-recommendations")
async def generate_detailed_recommendations(audit_data: Dict[str, Any]):
    """Génère des recommandations détaillées basées sur les données d'audit"""
    # ID utilisateur de test
    user_id = "test-user-123"
    
    try:
        # Appeler la méthode generate_recommendations
        result = await recommendation_engine.generate_recommendations(audit_data, user_id)
        return result
    except Exception as e:
        print(f"Erreur : {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Nouvel endpoint simplifié pour les recommandations
@app.post("/api/v1/simple-recommendations")
async def generate_simple_recommendations(audit_data: Dict[str, Any]):
    """Génère des recommandations à partir des données d'audit simplifiées"""
    try:
        # Log des données reçues pour débogage
        print(f"Données d'audit simplifiées reçues: {json.dumps(audit_data, indent=2)}")
        
        # Formater les données pour le moteur de recommandations
        formatted_data = {
            "profile": {
                "userType": audit_data.get("userType", "particulier"),
                "region": audit_data.get("region", "wallonie"),
                "postalCode": "1000",  # Valeur par défaut si non fournie
                "familySize": 1  # Valeur par défaut si non fournie
            },
            "consumption": {
                "electricityUsage": audit_data.get("electricityUsage", 0),
                "gasUsage": 0 if audit_data.get("gasUsage") is False else audit_data.get("gasUsage", 0),
                "waterUsage": 120  # Valeur par défaut si non fournie
            },
            "property": {
                "type": audit_data.get("propertyType", ""),
                "size": audit_data.get("area", 0),
                "constructionYear": audit_data.get("constructionYear", 0),
                "heatingSystem": "electric",  # Valeur par défaut si non fournie
                "insulation": audit_data.get("insulationStatus", "")
            }
        }
        
        print(f"Données formatées pour le moteur de recommandations: {json.dumps(formatted_data, indent=2)}")
        
        # Générer les recommandations
        user_id = "simple-user-id"
        result = await recommendation_engine.generate_recommendations(formatted_data, user_id)
        
        # Simplifier la réponse pour le frontend
        return {
            "recommendations": result.get("recommendations", []),
            "summary": result.get("analysis", "")
        }
    except Exception as e:
        print(f"Erreur de génération des recommandations: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retourner des recommandations par défaut en cas d'erreur
        return {
            "recommendations": [
                {
                    "id": "fallback-1",
                    "title": "Installation de panneaux solaires",
                    "description": "Les panneaux solaires peuvent réduire significativement votre facture d'électricité.",
                    "domain": "energy",
                    "estimated_cost_min": 4000,
                    "estimated_cost_max": 12000,
                    "estimated_savings_per_year": 800,
                    "estimated_roi_months": 60,
                    "ecological_impact_score": 8,
                    "difficulty": 6,
                    "applicable_subsidies": ["Prime Énergie"],
                    "priority_score": 80,
                    "reasoning": "Solution rentable à long terme.",
                    "status": "pending"
                },
                {
                    "id": "fallback-2",
                    "title": "Amélioration de l'isolation",
                    "description": "Une meilleure isolation permet de réduire significativement vos besoins en chauffage.",
                    "domain": "energy",
                    "estimated_cost_min": 3000,
                    "estimated_cost_max": 10000,
                    "estimated_savings_per_year": 600,
                    "estimated_roi_months": 72,
                    "ecological_impact_score": 7,
                    "difficulty": 5,
                    "applicable_subsidies": ["Prime Isolation"],
                    "priority_score": 75,
                    "reasoning": "Solution efficace pour réduire la consommation énergétique.",
                    "status": "pending"
                }
            ],
            "summary": "Recommandations de secours en raison d'une erreur technique."
        }

# Route racine
@app.get("/")
async def root():
    return {"message": "Serveur de test pour l'endpoint de recommandations"}

# Point d'entrée pour exécuter le serveur
if __name__ == "__main__":
    print("Démarrage du serveur de test pour l'endpoint de recommandations...")
    print("Documentation disponible à l'adresse: http://localhost:8003/docs")
    uvicorn.run(app, host="0.0.0.0", port=8003)
