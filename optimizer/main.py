"""
Optimizer Agent pour DynamoPro
-----------------------------
Ce module est responsable de l'analyse des données utilisateur et de la génération
de recommandations personnalisées pour optimiser la durabilité.
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any, Union

import uvicorn
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, UUID4, Field

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.auth import get_current_active_user, UserInDB
from common.config import settings
from common.models import (
    UserProfile, ConsumptionData, Property, Recommendation, 
    DomainType, UserType, BelgiumRegion
)
from common.ai_utils import LLMService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("optimizer")

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DynamoPro Optimizer Agent",
    description="Agent d'optimisation pour DynamoPro",
    version="0.1.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données spécifiques à l'agent
class OptimizationRequest(BaseModel):
    """Requête d'optimisation"""
    user_id: UUID4
    domains: List[DomainType] = [DomainType.ENERGY, DomainType.WATER]
    property_id: Optional[UUID4] = None

class OptimizationResponse(BaseModel):
    """Réponse à une requête d'optimisation"""
    user_id: UUID4
    recommendations: List[Recommendation]
    summary: str
    potential_savings_per_year: float

class RecommendationFeedback(BaseModel):
    """Feedback utilisateur sur une recommandation"""
    recommendation_id: UUID4
    user_id: UUID4
    status: str  # accepted, rejected, implemented
    user_comment: Optional[str] = None


# Base de données de recommandations (pour le MVP, à remplacer par une vraie DB)
ENERGY_RECOMMENDATIONS = [
    {
        "title": "Installation de panneaux solaires",
        "description": "Installation de panneaux photovoltaïques sur le toit pour produire de l'électricité.",
        "estimated_cost_min": 5000,
        "estimated_cost_max": 15000,
        "estimated_roi_months": 60,
        "ecological_impact_score": 9,
        "difficulty": 7,
        "applicable_conditions": {
            "property_types": ["house", "office", "building"],
            "min_roof_area": 20,
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"]
        }
    },
    {
        "title": "Remplacement des ampoules par LED",
        "description": "Remplacer toutes les ampoules traditionnelles ou halogènes par des LED basse consommation.",
        "estimated_cost_min": 100,
        "estimated_cost_max": 500,
        "estimated_roi_months": 12,
        "ecological_impact_score": 6,
        "difficulty": 2,
        "applicable_conditions": {
            "property_types": ["apartment", "house", "office", "building"],
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"]
        }
    },
    {
        "title": "Installation de pompe à chaleur",
        "description": "Remplacer le système de chauffage actuel par une pompe à chaleur plus efficace.",
        "estimated_cost_min": 8000,
        "estimated_cost_max": 20000,
        "estimated_roi_months": 84,
        "ecological_impact_score": 8,
        "difficulty": 8,
        "applicable_conditions": {
            "property_types": ["house", "building"],
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"],
            "min_property_size": 80
        }
    },
    {
        "title": "Isolation du toit/combles",
        "description": "Améliorer l'isolation du toit ou des combles pour réduire les pertes de chaleur.",
        "estimated_cost_min": 2000,
        "estimated_cost_max": 8000,
        "estimated_roi_months": 48,
        "ecological_impact_score": 7,
        "difficulty": 6,
        "applicable_conditions": {
            "property_types": ["house", "building"],
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"]
        }
    },
    {
        "title": "Installation de thermostat intelligent",
        "description": "Installer un thermostat programmable et connecté pour optimiser le chauffage.",
        "estimated_cost_min": 200,
        "estimated_cost_max": 500,
        "estimated_roi_months": 24,
        "ecological_impact_score": 5,
        "difficulty": 3,
        "applicable_conditions": {
            "property_types": ["apartment", "house", "office", "building"],
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"]
        }
    }
]

WATER_RECOMMENDATIONS = [
    {
        "title": "Installation de réducteurs de débit",
        "description": "Installer des réducteurs de débit sur les robinets et douches pour diminuer la consommation d'eau.",
        "estimated_cost_min": 50,
        "estimated_cost_max": 150,
        "estimated_roi_months": 6,
        "ecological_impact_score": 6,
        "difficulty": 2,
        "applicable_conditions": {
            "property_types": ["apartment", "house", "office", "building"],
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"]
        }
    },
    {
        "title": "Installation d'un système de récupération d'eau de pluie",
        "description": "Installer un système de collecte et stockage d'eau de pluie pour usage non potable.",
        "estimated_cost_min": 1500,
        "estimated_cost_max": 5000,
        "estimated_roi_months": 60,
        "ecological_impact_score": 8,
        "difficulty": 7,
        "applicable_conditions": {
            "property_types": ["house", "building"],
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"],
            "has_garden": True
        }
    },
    {
        "title": "Remplacement des toilettes par chasse d'eau double commande",
        "description": "Installer des toilettes à double commande pour réduire la consommation d'eau.",
        "estimated_cost_min": 200,
        "estimated_cost_max": 500,
        "estimated_roi_months": 36,
        "ecological_impact_score": 5,
        "difficulty": 4,
        "applicable_conditions": {
            "property_types": ["apartment", "house", "office", "building"],
            "user_types": ["individual", "self_employed", "small_business", "medium_business", "large_business"]
        }
    }
]


class OptimizerService:
    """Service principal d'optimisation"""
    
    def __init__(self):
        """Initialise le service d'optimisation"""
        self.llm_service = LLMService()
    
    async def get_user_data(self, user_id: UUID4) -> Dict[str, Any]:
        """Récupère les données de l'utilisateur (stub, à implémenter avec DB)"""
        # Ceci est un stub, à remplacer par des requêtes à la base de données
        return {
            "profile": {
                "id": str(user_id),
                "user_type": "individual",
                "region": "wallonie",
                "postal_code": "4000"
            },
            "properties": [
                {
                    "id": "property-1",
                    "type": "house",
                    "size_m2": 150,
                    "built_year": 1990,
                    "heating_type": "gas",
                    "has_garden": True,
                    "occupants": 4
                }
            ],
            "consumption": {
                "energy": [
                    {
                        "type": "electricity",
                        "consumption_kwh": 4500,
                        "cost": 1200,
                        "period_months": 12
                    },
                    {
                        "type": "gas",
                        "consumption_kwh": 18000,
                        "cost": 2000,
                        "period_months": 12
                    }
                ],
                "water": [
                    {
                        "consumption_m3": 120,
                        "cost": 360,
                        "period_months": 12
                    }
                ]
            }
        }
    
    def calculate_savings(
        self, 
        recommendation: Dict[str, Any], 
        user_data: Dict[str, Any]
    ) -> float:
        """Calcule les économies estimées pour une recommandation"""
        # Logique simplifiée, à améliorer avec des modèles plus précis
        if recommendation["title"].startswith("Installation de panneaux solaires"):
            # Estimer 30% d'économie sur l'électricité
            electricity_data = next((c for c in user_data["consumption"]["energy"] 
                                    if c.get("type") == "electricity"), None)
            if electricity_data:
                return electricity_data["cost"] * 0.3
        
        elif recommendation["title"].startswith("Remplacement des ampoules"):
            # Estimer 10% d'économie sur l'électricité
            electricity_data = next((c for c in user_data["consumption"]["energy"] 
                                    if c.get("type") == "electricity"), None)
            if electricity_data:
                return electricity_data["cost"] * 0.1
        
        elif recommendation["title"].startswith("Installation de pompe à chaleur"):
            # Estimer 25% d'économie sur le chauffage
            gas_data = next((c for c in user_data["consumption"]["energy"] 
                            if c.get("type") == "gas"), None)
            if gas_data:
                return gas_data["cost"] * 0.25
        
        elif recommendation["title"].startswith("Isolation du toit"):
            # Estimer 15% d'économie sur le chauffage
            gas_data = next((c for c in user_data["consumption"]["energy"] 
                            if c.get("type") == "gas"), None)
            if gas_data:
                return gas_data["cost"] * 0.15
        
        elif recommendation["title"].startswith("Installation de thermostat"):
            # Estimer 10% d'économie sur le chauffage
            gas_data = next((c for c in user_data["consumption"]["energy"] 
                            if c.get("type") == "gas"), None)
            if gas_data:
                return gas_data["cost"] * 0.1
        
        elif recommendation["title"].startswith("Installation de réducteurs"):
            # Estimer 15% d'économie sur l'eau
            water_data = next((c for c in user_data["consumption"].get("water", [])), None)
            if water_data:
                return water_data["cost"] * 0.15
        
        elif recommendation["title"].startswith("Installation d'un système de récupération"):
            # Estimer 30% d'économie sur l'eau
            water_data = next((c for c in user_data["consumption"].get("water", [])), None)
            if water_data:
                return water_data["cost"] * 0.3
        
        elif recommendation["title"].startswith("Remplacement des toilettes"):
            # Estimer 8% d'économie sur l'eau
            water_data = next((c for c in user_data["consumption"].get("water", [])), None)
            if water_data:
                return water_data["cost"] * 0.08
        
        return 0.0
    
    def is_recommendation_applicable(
        self, 
        recommendation: Dict[str, Any], 
        user_data: Dict[str, Any]
    ) -> bool:
        """Vérifie si une recommandation est applicable à l'utilisateur"""
        conditions = recommendation.get("applicable_conditions", {})
        
        # Vérifier le type d'utilisateur
        user_types = conditions.get("user_types", [])
        if user_types and user_data["profile"]["user_type"] not in user_types:
            return False
        
        # Vérifier le type de propriété
        if "property_types" in conditions:
            property_types = conditions["property_types"]
            properties = user_data.get("properties", [])
            if not any(p.get("type") in property_types for p in properties):
                return False
        
        # Vérifier la taille minimale de propriété
        min_property_size = conditions.get("min_property_size")
        if min_property_size is not None:
            properties = user_data.get("properties", [])
            if not any(p.get("size_m2", 0) >= min_property_size for p in properties):
                return False
        
        # Vérifier la présence d'un jardin
        if conditions.get("has_garden") is True:
            properties = user_data.get("properties", [])
            if not any(p.get("has_garden") for p in properties):
                return False
        
        # Vérifier la superficie minimale du toit
        min_roof_area = conditions.get("min_roof_area")
        if min_roof_area is not None:
            properties = user_data.get("properties", [])
            # Estimation simplifiée: 50% de la superficie au sol pour un toit incliné
            if not any(p.get("size_m2", 0) * 0.5 >= min_roof_area for p in properties):
                return False
        
        return True
    
    def calculate_priority_score(
        self,
        recommendation: Dict[str, Any],
        yearly_savings: float
    ) -> float:
        """Calcule un score de priorité pour ordonner les recommandations"""
        # Paramètres de pondération
        roi_weight = 0.4
        savings_weight = 0.3
        ecological_weight = 0.2
        difficulty_weight = 0.1
        
        # Normalisation des valeurs
        roi_months = recommendation["estimated_roi_months"]
        roi_score = max(0, 1 - (roi_months / 120))  # 10 ans max
        
        savings_score = min(1, yearly_savings / 1000)  # Max 1000€ d'économies
        
        eco_score = recommendation["ecological_impact_score"] / 10
        
        # Pour la difficulté, un score inversé (plus facile = meilleur score)
        ease_score = 1 - (recommendation["difficulty"] / 10)
        
        # Calcul du score final
        priority = (
            roi_weight * roi_score +
            savings_weight * savings_score +
            ecological_weight * eco_score +
            difficulty_weight * ease_score
        )
        
        return priority
    
    async def generate_recommendations(
        self,
        user_id: UUID4,
        domains: List[DomainType],
        property_id: Optional[UUID4] = None
    ) -> OptimizationResponse:
        """Génère des recommandations personnalisées pour l'utilisateur"""
        # Récupérer les données utilisateur
        user_data = await self.get_user_data(user_id)
        
        all_recommendations = []
        
        # Filtrer par domaine
        if DomainType.ENERGY in domains:
            all_recommendations.extend(ENERGY_RECOMMENDATIONS)
        
        if DomainType.WATER in domains:
            all_recommendations.extend(WATER_RECOMMENDATIONS)
        
        # Filtrer les recommandations applicables
        applicable_recommendations = []
        total_potential_savings = 0.0
        
        for rec in all_recommendations:
            if self.is_recommendation_applicable(rec, user_data):
                # Calculer les économies estimées
                yearly_savings = self.calculate_savings(rec, user_data)
                
                # Créer un objet Recommendation complet
                recommendation = Recommendation(
                    id=UUID4(),
                    user_id=user_id,
                    property_id=property_id,
                    domain=DomainType.ENERGY if rec in ENERGY_RECOMMENDATIONS else DomainType.WATER,
                    title=rec["title"],
                    description=rec["description"],
                    estimated_cost_min=rec["estimated_cost_min"],
                    estimated_cost_max=rec["estimated_cost_max"],
                    estimated_savings_per_year=yearly_savings,
                    estimated_roi_months=rec["estimated_roi_months"],
                    ecological_impact_score=rec["ecological_impact_score"],
                    difficulty=rec["difficulty"],
                    applicable_subsidies=[],  # À remplir par le Subsidy Agent
                    priority_score=self.calculate_priority_score(rec, yearly_savings),
                    status="pending"
                )
                
                applicable_recommendations.append(recommendation)
                total_potential_savings += yearly_savings
        
        # Trier par score de priorité
        applicable_recommendations.sort(key=lambda x: x.priority_score, reverse=True)
        
        # Générer un résumé avec LLM
        summary = await self.generate_summary(applicable_recommendations, total_potential_savings)
        
        return OptimizationResponse(
            user_id=user_id,
            recommendations=applicable_recommendations,
            summary=summary,
            potential_savings_per_year=total_potential_savings
        )
    
    async def generate_summary(
        self,
        recommendations: List[Recommendation],
        total_savings: float
    ) -> str:
        """Génère un résumé des recommandations avec le LLM"""
        if not recommendations:
            return "Aucune recommandation applicable n'a été trouvée."
        
        # Préparer le contexte pour le LLM
        context = {
            "recommendations_count": len(recommendations),
            "top_recommendations": [r.title for r in recommendations[:3]],
            "total_savings": round(total_savings, 2),
            "domains": list(set(r.domain for r in recommendations)),
            "highest_impact": recommendations[0].title,
            "lowest_cost": min(recommendations, key=lambda x: x.estimated_cost_min).title,
            "quickest_roi": min(recommendations, key=lambda x: x.estimated_roi_months).title
        }
        
        # Créer le prompt
        prompt = f"""
        Génère un résumé concis (max 150 mots) des recommandations d'optimisation de durabilité.
        
        Informations clés:
        - Nombre de recommandations: {context['recommendations_count']}
        - Domaines concernés: {', '.join(context['domains'])}
        - Économies totales estimées: {context['total_savings']}€ par an
        - Recommandations principales: {', '.join(context['top_recommendations'])}
        - Recommandation à plus fort impact: {context['highest_impact']}
        - Recommandation à moindre coût: {context['lowest_cost']}
        - Retour sur investissement le plus rapide: {context['quickest_roi']}
        
        Le résumé doit être informatif, encourageant et mettre en avant les bénéfices financiers et écologiques.
        """
        
        # Générer le résumé
        system_message = "Tu es un expert en optimisation énergétique et durabilité en Belgique."
        summary = await self.llm_service.generate_response(prompt, system_message)
        
        return summary


# Initialisation du service
optimizer_service = OptimizerService()

# Routes API
@app.post("/api/v1/optimize", response_model=OptimizationResponse)
async def optimize(
    request: OptimizationRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour les requêtes d'optimisation"""
    return await optimizer_service.generate_recommendations(
        user_id=request.user_id,
        domains=request.domains,
        property_id=request.property_id
    )


@app.post("/api/v1/recommendation-feedback")
async def provide_feedback(
    feedback: RecommendationFeedback,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour le feedback sur les recommandations"""
    # Logique à implémenter pour traiter le feedback
    return {"status": "feedback_received", "recommendation_id": feedback.recommendation_id}


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Lancer le serveur en mode développement
    port = int(os.getenv("PORT", "8002"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
