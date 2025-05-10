"""
Subsidy Agent pour DynamoPro
---------------------------
Ce module est responsable de l'identification des subventions applicables et
de l'aide aux utilisateurs dans les procédures de demande.
"""

import logging
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, UUID4, Field

import sys
# Ajoute le dossier subsidy au PYTHONPATH pour les imports internes
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)
sys.path.append(os.path.dirname(CURRENT_DIR))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.auth import get_current_active_user, UserInDB
from common.config import settings
from common.models import (
    UserProfile, Recommendation, Subsidy as CommonSubsidy, SubsidyApplication,
    DomainType, UserType, BelgiumRegion
)
from common.ai_utils import LLMService, OCRService

# Import de la base de données de subventions
from subsidy_db import (
    SubsidyDatabase, get_subsidy_database, Subsidy,
    SubsidyType, SubsidyConditionType, SubsidyProvider,
    SubsidyCondition, SubsidyKeyword, SubsidyDocumentType, RequiredDocument
)
from subsidy_data import initialize_subsidy_database

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("subsidy")

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DynamoPro Subsidy Agent",
    description="Agent de gestion des subventions pour DynamoPro",
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

# --- Inclusion du routeur LLM pour l'IA conversationnelle ---
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../app'))
from app.api.llm import router as llm_router
app.include_router(llm_router)
# Modèles de données spécifiques à l'agent
class SubsidyRequest(BaseModel):
    """Requête de recherche de subventions"""
    user_id: UUID4
    recommendation_ids: Optional[List[UUID4]] = None
    domains: List[DomainType] = [DomainType.ENERGY, DomainType.WATER]

class SubsidyResponse(BaseModel):
    """Réponse à une requête de subventions"""
    user_id: UUID4
    subsidies: List[Subsidy]
    total_potential_amount: float
    summary: str

class ApplicationFormRequest(BaseModel):
    """Requête de génération de formulaire de demande"""
    user_id: UUID4
    subsidy_id: UUID4
    recommendation_id: Optional[UUID4] = None

class ApplicationFormResponse(BaseModel):
    """Réponse à une requête de génération de formulaire"""
    user_id: UUID4
    subsidy_id: UUID4
    application_id: UUID4
    form_data: Dict[str, Any]
    required_documents: List[str]
    next_steps: str

class ApplicationStatusUpdate(BaseModel):
    """Mise à jour du statut d'une demande de subvention"""
    application_id: UUID4
    status: str
    notes: Optional[str] = None
    amount_approved: Optional[float] = None

# Initialisation de la base de données de subventions
subsidy_db = get_subsidy_database()

# Chargement des données de subvention initiales
num_subsidies, num_providers = initialize_subsidy_database(subsidy_db)
logging.info(f"Base de données des subventions initialisée avec {num_subsidies} subventions et {num_providers} fournisseurs")

# Conversion d'un modèle Subsidy de notre base de données vers le modèle CommonSubsidy utilisé par l'API
def convert_to_common_subsidy(subsidy: Subsidy) -> CommonSubsidy:
    """Convertit un modèle Subsidy de la base de données en modèle CommonSubsidy pour l'API"""
    # Construction d'une représentation des conditions sous forme de chaîne
    conditions_str = "\n".join([cond.description for cond in subsidy.conditions]) if subsidy.conditions else ""
    
    # Construction d'une représentation du fournisseur
    provider_obj = subsidy_db.get_provider(subsidy.provider_id)
    provider_name = provider_obj.name if provider_obj else subsidy.provider_id
    
    return CommonSubsidy(
        id=subsidy.id,
        name=subsidy.name,
        description=subsidy.description,
        provider=provider_name,
        regions=subsidy.regions,
        eligible_user_types=subsidy.eligible_user_types,
        domains=subsidy.domains,
        max_amount=subsidy.max_amount,
        percentage=subsidy.percentage,
        conditions=conditions_str,
        documentation_url=subsidy.documentation_url,
        application_process=subsidy.application_process,
        active=subsidy.active
    )


class SubsidyService:
    """Service principal de gestion des subventions"""
    
    def __init__(self):
        """Initialise le service de gestion des subventions"""
        self.llm_service = LLMService()
        self.ocr_service = OCRService()
    
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
                    "has_garden": True
                }
            ]
        }
    
    async def get_recommendations(self, recommendation_ids: List[UUID4]) -> List[Dict[str, Any]]:
        """Récupère les recommandations (stub, à implémenter avec DB)"""
        # Ceci est un stub, à remplacer par des requêtes à la base de données
        return [
            {
                "id": str(recommendation_ids[0]) if recommendation_ids else "rec-1",
                "title": "Installation de panneaux solaires",
                "domain": "energy",
                "estimated_cost_min": 5000,
                "estimated_cost_max": 15000
            },
            {
                "id": str(recommendation_ids[1]) if len(recommendation_ids) > 1 else "rec-2",
                "title": "Isolation du toit/combles",
                "domain": "energy",
                "estimated_cost_min": 2000,
                "estimated_cost_max": 8000
            }
        ]
    
    def is_subsidy_applicable(
        self,
        subsidy: Subsidy,
        user_data: Dict[str, Any],
        recommendation: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Détermine si une subvention est applicable à un utilisateur"""
        # Vérifier la région
        user_region = user_data.get("profile", {}).get("region", "")
        if user_region and user_region.lower() not in subsidy.regions:
            return False
        
        # Vérifier le type d'utilisateur
        if user_data["profile"]["user_type"] not in subsidy.eligible_user_types:
            return False
        
        # Si une recommandation est spécifiée, vérifier le domaine
        if recommendation:
            if recommendation["domain"] not in subsidy.domains:
                return False
            
            # Vérifications spécifiques par type de subvention et recommandation
            title_lower = recommendation["title"].lower()
            subsidy_keywords = [k.value.lower() for k in subsidy.keywords] if subsidy.keywords else []
            
            # Vérifier la correspondance entre les mots-clés de la subvention et les recommandations
            if "solaire" in title_lower or "photovoltaïque" in title_lower:
                if SubsidyKeyword.SOLAR.value.lower() not in subsidy_keywords:
                    return False
            
            if "isolation" in title_lower or "isoler" in title_lower or "toit" in title_lower:
                if SubsidyKeyword.INSULATION.value.lower() not in subsidy_keywords:
                    return False
            
            if "pompe à chaleur" in title_lower or "chauffage" in title_lower:
                if SubsidyKeyword.HEAT_PUMP.value.lower() not in subsidy_keywords and SubsidyKeyword.HEATING.value.lower() not in subsidy_keywords:
                    return False
            
            if "eau" in title_lower and ("pluie" in title_lower or "récupération" in title_lower):
                if SubsidyKeyword.RAINWATER.value.lower() not in subsidy_keywords and SubsidyKeyword.WATER_SAVING.value.lower() not in subsidy_keywords:
                    return False
            
            if "fenêtre" in title_lower or "châssis" in title_lower or "vitrage" in title_lower:
                if SubsidyKeyword.WINDOWS.value.lower() not in subsidy_keywords:
                    return False
        
        return True
    
    def calculate_subsidy_amount(
        self, 
        subsidy: Subsidy, 
        recommendation: Optional[Dict[str, Any]] = None
    ) -> float:
        """Calcule le montant potentiel de la subvention"""
        if not recommendation:
            # Si pas de recommandation, retourner le montant maximum
            return subsidy.max_amount or 0
        
        # Calculer sur la base du coût estimé de la recommandation
        avg_cost = (recommendation["estimated_cost_min"] + recommendation["estimated_cost_max"]) / 2
        
        if subsidy.percentage:
            amount = avg_cost * (subsidy.percentage / 100)
        else:
            amount = 0
        
        # Plafonner au montant maximum
        if subsidy.max_amount and amount > subsidy.max_amount:
            amount = subsidy.max_amount
        
        return amount
    
    async def find_applicable_subsidies(
        self,
        user_id: UUID4,
        recommendation_ids: Optional[List[UUID4]] = None,
        domains: List[DomainType] = [DomainType.ENERGY, DomainType.WATER]
    ) -> SubsidyResponse:
        """Trouve les subventions applicables pour l'utilisateur et les recommandations"""
        # Récupérer les données utilisateur
        user_data = await self.get_user_data(user_id)
        
        # Récupérer les recommandations si spécifiées
        recommendations = await self.get_recommendations(recommendation_ids) if recommendation_ids else []
        
        applicable_subsidies = []
        total_potential_amount = 0.0
        
        # Filtrer les subventions par domaine
        domain_values = [d.value for d in domains]
        
        # Récupérer toutes les subventions actives de la base de données
        all_subsidies = subsidy_db.get_all_subsidies(active_only=True)
        
        # Filtrer les subventions par domaine
        filtered_subsidies = [s for s in all_subsidies if any(d in domain_values for d in s.domains)]
        
        # Traiter les subventions pour les recommandations spécifiques
        if recommendations:
            for recommendation in recommendations:
                rec_subsidies = []
                for subsidy in filtered_subsidies:
                    if await self.is_subsidy_applicable(subsidy, user_data, recommendation):
                        # Convertir de notre modèle Subsidy vers CommonSubsidy pour l'API
                        common_subsidy = convert_to_common_subsidy(subsidy)
                        
                        # Calculer le montant potentiel
                        amount = self.calculate_subsidy_amount(subsidy, recommendation)
                        total_potential_amount += amount
                        
                        rec_subsidies.append(common_subsidy)
                
                # Ajouter les subventions pour cette recommandation
                applicable_subsidies.extend(rec_subsidies)
        else:
            # Traiter toutes les subventions générales
            for subsidy in filtered_subsidies:
                if await self.is_subsidy_applicable(subsidy, user_data):
                    # Convertir de notre modèle Subsidy vers CommonSubsidy pour l'API
                    common_subsidy = convert_to_common_subsidy(subsidy)
                    
                    # Calculer le montant potentiel (approximatif sans recommandation)
                    amount = self.calculate_subsidy_amount(subsidy)
                    total_potential_amount += amount
                    
                    applicable_subsidies.append(common_subsidy)
        
        # Éliminer les doublons potentiels
        unique_subsidies = list({s.id: s for s in applicable_subsidies}.values())
        
        # Générer un résumé avec LLM
        summary = await self.generate_summary(unique_subsidies, total_potential_amount)
        
        return SubsidyResponse(
            user_id=user_id,
            subsidies=unique_subsidies,
            total_potential_amount=total_potential_amount,
            summary=summary
        )
    
    async def generate_summary(
        self,
        subsidies: List[Subsidy],
        total_amount: float
    ) -> str:
        """Génère un résumé des subventions avec le LLM"""
        if not subsidies:
            return "Aucune subvention applicable n'a été trouvée."
        
        # Préparer le contexte pour le LLM
        context = {
            "subsidies_count": len(subsidies),
            "top_subsidies": [s.name for s in subsidies[:3]],
            "total_amount": round(total_amount, 2),
            "providers": list(set(s.provider for s in subsidies)),
            "highest_subsidy": max(subsidies, key=lambda x: x.max_amount or 0).name,
            "highest_amount": max(subsidies, key=lambda x: x.max_amount or 0).max_amount
        }
        
        # Créer le prompt
        prompt = f"""
        Génère un résumé concis (max 150 mots) des subventions applicables.
        
        Informations clés:
        - Nombre de subventions: {context['subsidies_count']}
        - Organismes: {', '.join(context['providers'])}
        - Montant total potentiel: {context['total_amount']}€
        - Subventions principales: {', '.join(context['top_subsidies'])}
        - Subvention la plus importante: {context['highest_subsidy']} (jusqu'à {context['highest_amount']}€)
        
        Le résumé doit encourager l'utilisateur à saisir ces opportunités, expliquer brièvement les
        prochaines étapes et souligner l'avantage financier.
        """
        
        # Générer le résumé
        system_message = "Tu es un expert en subventions belges pour l'énergie et l'environnement."
        summary = await self.llm_service.generate_response(prompt, system_message)
        
        return summary
    
    async def generate_application_form(
        self,
        user_id: UUID4,
        subsidy_id: UUID4,
        recommendation_id: Optional[UUID4] = None
    ) -> ApplicationFormResponse:
        """Génère un formulaire pré-rempli pour une demande de subvention"""
        # Récupérer les données utilisateur
        user_data = await self.get_user_data(user_id)
        
        # Récupérer la subvention depuis la base de données
        subsidy = subsidy_db.get_subsidy_by_id(str(subsidy_id))
        if not subsidy:
            raise HTTPException(status_code=404, detail="Subvention non trouvée")
        
        # Récupérer les informations du fournisseur
        provider = subsidy_db.get_provider(subsidy.provider_id)
        
        # Récupérer la recommandation si spécifiée
        recommendation = None
        if recommendation_id:
            recommendations = await self.get_recommendations([recommendation_id])
            if recommendations:
                recommendation = recommendations[0]
        
        # Générer l'ID de l'application
        application_id = uuid.uuid4()
        
        # Pré-remplir les données du formulaire
        form_data = {
            "applicant": {
                "name": "Nom Utilisateur",  # À remplacer par les vraies données
                "email": "utilisateur@exemple.com",
                "phone": "+32 123 456 789",
                "address": "Rue Example 123, 4000 Liège",
                "user_type": user_data["profile"]["user_type"]
            },
            "property": {
                "address": "Rue Example 123, 4000 Liège",
                "type": user_data["properties"][0]["type"] if user_data.get("properties") else "house",
                "year_built": user_data["properties"][0].get("built_year", "Non spécifié") if user_data.get("properties") else "Non spécifié"
            },
            "subsidy": {
                "id": str(subsidy_id),
                "name": subsidy.name,
                "provider": provider.name if provider else subsidy.provider_id
            },
            "project": {
                "description": recommendation["title"] if recommendation else "À compléter",
                "estimated_cost": (recommendation["estimated_cost_min"] + recommendation["estimated_cost_max"]) / 2 if recommendation else "À compléter",
                "estimated_completion_date": "À compléter"
            },
            "bank_details": {
                "account_holder": "À compléter",
                "iban": "À compléter"
            }
        }
        
        # Utiliser les documents requis définis dans la base de données
        required_doc_descriptions = []
        
        # Ajouter les documents généraux toujours requis
        required_doc_descriptions.append("Preuve d'identité (copie de carte d'identité)")
        required_doc_descriptions.append("Preuve de propriété ou bail")
        
        # Ajouter les documents spécifiques à cette subvention
        if subsidy.required_documents:
            for doc in subsidy.required_documents:
                required_doc_descriptions.append(doc.description)
        
        # Générer les prochaines étapes avec le LLM
        next_steps = await self.generate_next_steps_from_subsidy(subsidy, required_doc_descriptions)
        
        return ApplicationFormResponse(
            user_id=user_id,
            subsidy_id=subsidy_id,
            application_id=application_id,
            form_data=form_data,
            required_documents=required_doc_descriptions,
            next_steps=next_steps
        )
    
    async def generate_next_steps_from_subsidy(
        self,
        subsidy: Subsidy,
        required_documents: List[str]
    ) -> str:
        """Génère les prochaines étapes pour la demande de subvention"""
        # Récupérer le fournisseur
        provider = subsidy_db.get_provider(subsidy.provider_id)
        provider_name = provider.name if provider else subsidy.provider_id
        
        # Créer le prompt
        prompt = f"""
        Génère une explication concise des prochaines étapes pour demander la subvention "{subsidy.name}".
        
        Informations clés:
        - Fournisseur: {provider_name}
        - Processus de demande: {subsidy.application_process}
        - Documents requis: {', '.join(required_documents)}
        - URL de documentation: {subsidy.documentation_url}
        - Délai de traitement typique: {subsidy.typical_processing_time_days} jours
        
        Explique le processus étape par étape, de manière claire et pratique. Mentionne aussi les délais
        typiques et tout conseil utile pour maximiser les chances d'obtenir la subvention.
        """
        
        # Générer les prochaines étapes
        system_message = "Tu es un expert en subventions belges et processus administratifs."
        next_steps = await self.llm_service.generate_response(prompt, system_message)
        
        return next_steps
        
    # Pour la compatibilité avec le code existant
    async def generate_next_steps(
        self,
        subsidy: Dict[str, Any],
        required_documents: List[str]
    ) -> str:
        """Méthode obsolète maintenue pour compatibilité"""
        # Créer le prompt
        prompt = f"""
        Génère une explication concise des prochaines étapes pour demander la subvention "{subsidy['name']}".
        
        Informations clés:
        - Fournisseur: {subsidy['provider']}
        - Processus de demande: {subsidy['application_process']}
        - Documents requis: {', '.join(required_documents)}
        - URL de documentation: {subsidy['documentation_url']}
        
        Explique le processus étape par étape, de manière claire et pratique. Mentionne aussi les délais
        typiques et tout conseil utile pour maximiser les chances d'obtenir la subvention.
        """
        
        # Générer les prochaines étapes
        system_message = "Tu es un expert en subventions belges et processus administratifs."
        next_steps = await self.llm_service.generate_response(prompt, system_message)
        
        return next_steps


# Initialisation du service
subsidy_service = SubsidyService()

# Intégration des routes API depuis le module api_routes
from api_routes import router as subsidy_router

# Importer les routes d'audit
from api.audit_routes import router as audit_router

# Inclure les routes de subsidy_router dans l'application principale
app.include_router(subsidy_router)
app.include_router(audit_router)

# Import du moteur de recommandations
from integrations.recommendation_engine import get_recommendation_engine

# Initialisation du moteur de recommandations
recommendation_engine = get_recommendation_engine()

# Garder les routes existantes pour la rétro-compatibilité
@app.post("/api/v1/find-subsidies", response_model=SubsidyResponse)
async def find_subsidies(
    request: SubsidyRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour les requêtes de recherche de subventions"""
    return await subsidy_service.find_applicable_subsidies(
        user_id=request.user_id,
        recommendation_ids=request.recommendation_ids,
        domains=request.domains
    )


@app.post("/api/v1/generate-application-form", response_model=ApplicationFormResponse)
async def generate_application_form(
    request: ApplicationFormRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour la génération de formulaires de demande"""
    return await subsidy_service.generate_application_form(
        user_id=request.user_id,
        subsidy_id=request.subsidy_id,
        recommendation_id=request.recommendation_id
    )


@app.post("/api/v1/update-application-status")
async def update_application_status(
    update: ApplicationStatusUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour la mise à jour du statut d'une demande"""
    # Utiliser le tracker d'applications pour mettre à jour le statut
    from application_tracker import get_application_tracker, ApplicationStatus
    
    tracker = get_application_tracker()
    application = tracker.update_application(
        application_id=str(update.application_id),
        status=update.status,
        comment=update.notes
    )
    
    return {
        "status": "updated", 
        "application_id": update.application_id,
        "current_status": application.status
    }


@app.post("/api/v1/detailed-recommendations")
async def generate_detailed_recommendations(
    audit_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Génère des recommandations détaillées basées sur l'IA"""
    return await recommendation_engine.generate_recommendations(audit_data, str(current_user.id))


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Lancer le serveur en mode développement
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
