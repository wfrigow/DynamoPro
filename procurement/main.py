"""
Procurement Agent pour DynamoPro
------------------------------
Ce module est responsable de la mise en relation des utilisateurs avec des
fournisseurs qualifiés pour implémenter les recommandations.
"""

import logging
import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, UUID4, Field, EmailStr

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.auth import get_current_active_user, UserInDB
from common.config import settings
from common.models import (
    UserProfile, Recommendation, Supplier, Project,
    DomainType, UserType, BelgiumRegion
)
from common.ai_utils import LLMService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("procurement")

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DynamoPro Procurement Agent",
    description="Agent de mise en relation avec les fournisseurs pour DynamoPro",
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
class SupplierSearchRequest(BaseModel):
    """Requête de recherche de fournisseurs"""
    user_id: UUID4
    recommendation_id: UUID4
    postal_code: Optional[str] = None
    max_distance_km: Optional[int] = 50

class SupplierSearchResponse(BaseModel):
    """Réponse à une requête de recherche de fournisseurs"""
    recommendation_id: UUID4
    suppliers: List[Supplier]
    summary: str

class QuoteRequest(BaseModel):
    """Requête de devis auprès d'un fournisseur"""
    user_id: UUID4
    recommendation_id: UUID4
    supplier_id: UUID4
    property_id: Optional[UUID4] = None
    details: str
    preferred_contact_method: str = "email"
    preferred_timeframe: Optional[str] = None

class QuoteResponse(BaseModel):
    """Réponse à une demande de devis"""
    request_id: UUID4
    status: str = "sent"
    estimated_response_time: str

class SupplierRegistration(BaseModel):
    """Inscription d'un nouveau fournisseur"""
    name: str
    description: str
    domains: List[DomainType]
    regions_served: List[BelgiumRegion]
    address: str
    postal_code: str
    city: str
    contact_email: EmailStr
    contact_phone: str
    website: Optional[str] = None
    vat_number: str

class ProjectCreationRequest(BaseModel):
    """Requête de création de projet"""
    user_id: UUID4
    recommendation_id: UUID4
    supplier_id: UUID4
    property_id: Optional[UUID4] = None
    start_date: Optional[datetime] = None
    notes: Optional[str] = None

# Base de données de fournisseurs (pour le MVP, à remplacer par une vraie DB)
SUPPLIERS_DATABASE = [
    {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "name": "EcoSolar Belgique",
        "description": "Installation de panneaux solaires et solutions photovoltaïques pour particuliers et entreprises.",
        "domains": ["energy"],
        "regions_served": ["wallonie", "bruxelles"],
        "address": "Rue de l'Innovation 45",
        "postal_code": "4000",
        "city": "Liège",
        "contact_email": "contact@ecosolar.be",
        "contact_phone": "+32 4 123 45 67",
        "website": "https://www.ecosolar.be",
        "vat_number": "BE0123456789",
        "rating": 4.8,
        "verified": True,
        "active": True
    },
    {
        "id": "c0a80121-9e7a-4b4a-9b96-4c6b5308c30c",
        "name": "ThermoConfort",
        "description": "Spécialistes en isolation thermique, audit énergétique et pompes à chaleur.",
        "domains": ["energy"],
        "regions_served": ["wallonie"],
        "address": "Avenue Thermique 23",
        "postal_code": "5000",
        "city": "Namur",
        "contact_email": "info@thermoconfort.be",
        "contact_phone": "+32 81 234 567",
        "website": "https://www.thermoconfort.be",
        "vat_number": "BE0234567891",
        "rating": 4.6,
        "verified": True,
        "active": True
    },
    {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "name": "AquaSave",
        "description": "Solutions pour l'économie d'eau: récupération d'eau de pluie, systèmes économes et audits.",
        "domains": ["water"],
        "regions_served": ["wallonie", "bruxelles", "flandre"],
        "address": "Waterstraat 78",
        "postal_code": "6700",
        "city": "Arlon",
        "contact_email": "contact@aquasave.be",
        "contact_phone": "+32 63 345 678",
        "website": "https://www.aquasave.be",
        "vat_number": "BE0345678912",
        "rating": 4.5,
        "verified": True,
        "active": True
    },
    {
        "id": "55401b9c-0d2a-4b5a-b6c1-4bb35d01b499",
        "name": "ÉcoRénov",
        "description": "Entreprise spécialisée dans la rénovation durable et l'amélioration de l'efficacité énergétique.",
        "domains": ["energy"],
        "regions_served": ["wallonie"],
        "address": "Rue de la Rénovation 56",
        "postal_code": "4800",
        "city": "Verviers",
        "contact_email": "info@ecorenov.be",
        "contact_phone": "+32 87 456 789",
        "website": "https://www.ecorenov.be",
        "vat_number": "BE0456789123",
        "rating": 4.7,
        "verified": True,
        "active": True
    },
    {
        "id": "7e8f4c1a-6c9d-4b6e-8c7b-9b3a7b4c5d6e",
        "name": "BioConstruct",
        "description": "Construction et rénovation écologique avec matériaux biosourcés et techniques durables.",
        "domains": ["energy", "water"],
        "regions_served": ["wallonie", "bruxelles"],
        "address": "Rue Verte 89",
        "postal_code": "1348",
        "city": "Louvain-la-Neuve",
        "contact_email": "contact@bioconstruct.be",
        "contact_phone": "+32 10 567 890",
        "website": "https://www.bioconstruct.be",
        "vat_number": "BE0567891234",
        "rating": 4.9,
        "verified": True,
        "active": True
    }
]

def convert_dict_to_supplier(supplier_dict: Dict[str, Any]) -> Supplier:
    """Convertit un dictionnaire en objet Supplier"""
    return Supplier(
        id=supplier_dict["id"],
        name=supplier_dict["name"],
        description=supplier_dict["description"],
        domains=[DomainType(d) for d in supplier_dict["domains"]],
        regions_served=[BelgiumRegion(r) for r in supplier_dict["regions_served"]],
        address=supplier_dict["address"],
        postal_code=supplier_dict["postal_code"],
        city=supplier_dict["city"],
        contact_email=supplier_dict["contact_email"],
        contact_phone=supplier_dict["contact_phone"],
        website=supplier_dict.get("website"),
        vat_number=supplier_dict["vat_number"],
        rating=supplier_dict.get("rating"),
        verified=supplier_dict.get("verified", False),
        active=supplier_dict.get("active", True)
    )


class ProcurementService:
    """Service principal de gestion des fournisseurs"""
    
    def __init__(self):
        """Initialise le service de gestion des fournisseurs"""
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
                    "postal_code": "4000"
                }
            ]
        }
    
    async def get_recommendation(self, recommendation_id: UUID4) -> Dict[str, Any]:
        """Récupère une recommandation (stub, à implémenter avec DB)"""
        # Ceci est un stub, à remplacer par des requêtes à la base de données
        return {
            "id": str(recommendation_id),
            "title": "Installation de panneaux solaires",
            "description": "Installation de panneaux photovoltaïques sur le toit pour produire de l'électricité.",
            "domain": "energy",
            "estimated_cost_min": 5000,
            "estimated_cost_max": 15000
        }
    
    def calculate_distance(self, postal_code1: str, postal_code2: str) -> int:
        """Calcule une distance approximative entre deux codes postaux belges"""
        # Pour le MVP, cette fonction est très simplifiée
        # À remplacer par un calcul plus précis avec une API géographique
        try:
            # Première approximation basée uniquement sur les premiers chiffres
            first1 = int(postal_code1[0])
            first2 = int(postal_code2[0])
            
            # Différence absolue multipliée par un facteur (environ 30km par unité)
            return abs(first1 - first2) * 30
        except (ValueError, IndexError):
            # En cas d'erreur, retourner une grande distance
            return 100
    
    def is_supplier_suitable(
        self, 
        supplier: Dict[str, Any], 
        recommendation: Dict[str, Any],
        user_data: Dict[str, Any],
        max_distance_km: int
    ) -> bool:
        """Vérifie si un fournisseur est adapté à la recommandation et à l'utilisateur"""
        # Vérifier le domaine
        if recommendation["domain"] not in supplier["domains"]:
            return False
        
        # Vérifier la région
        if user_data["profile"]["region"] not in supplier["regions_served"]:
            return False
        
        # Vérifier la distance
        user_postal = user_data["profile"]["postal_code"]
        supplier_postal = supplier["postal_code"]
        distance = self.calculate_distance(user_postal, supplier_postal)
        
        if distance > max_distance_km:
            return False
        
        # Vérifier l'adéquation spécifique à la recommandation
        if "panneaux solaires" in recommendation["title"].lower():
            if not any("solaire" in s.lower() or "photovoltaïque" in s.lower() 
                      for s in [supplier["name"], supplier["description"]]):
                # Pas une spécialité évidente du fournisseur
                return False
        
        if "pompe à chaleur" in recommendation["title"].lower():
            if not any("pompe" in s.lower() or "chaleur" in s.lower() or "thermique" in s.lower() 
                      for s in [supplier["name"], supplier["description"]]):
                return False
        
        if "isolation" in recommendation["title"].lower():
            if not any("isolation" in s.lower() or "thermique" in s.lower() 
                      for s in [supplier["name"], supplier["description"]]):
                return False
        
        if "eau" in recommendation["title"].lower():
            if not any("eau" in s.lower() or "aqua" in s.lower() or "hydro" in s.lower() 
                      for s in [supplier["name"], supplier["description"]]):
                return False
        
        return True
    
    async def find_suitable_suppliers(
        self,
        user_id: UUID4,
        recommendation_id: UUID4,
        postal_code: Optional[str] = None,
        max_distance_km: int = 50
    ) -> SupplierSearchResponse:
        """Trouve des fournisseurs adaptés à une recommandation"""
        # Récupérer les données utilisateur
        user_data = await self.get_user_data(user_id)
        if postal_code:
            user_data["profile"]["postal_code"] = postal_code
        
        # Récupérer la recommandation
        recommendation = await self.get_recommendation(recommendation_id)
        
        suitable_suppliers = []
        
        for supplier_dict in SUPPLIERS_DATABASE:
            if self.is_supplier_suitable(supplier_dict, recommendation, user_data, max_distance_km):
                supplier = convert_dict_to_supplier(supplier_dict)
                suitable_suppliers.append(supplier)
        
        # Trier par rating et vérification
        suitable_suppliers.sort(key=lambda s: (s.verified, s.rating or 0), reverse=True)
        
        # Générer un résumé avec LLM
        summary = await self.generate_summary(suitable_suppliers, recommendation)
        
        return SupplierSearchResponse(
            recommendation_id=recommendation_id,
            suppliers=suitable_suppliers,
            summary=summary
        )
    
    async def generate_summary(
        self,
        suppliers: List[Supplier],
        recommendation: Dict[str, Any]
    ) -> str:
        """Génère un résumé des fournisseurs trouvés avec le LLM"""
        if not suppliers:
            return f"Aucun fournisseur adapté n'a été trouvé pour '{recommendation['title']}'."
        
        # Préparer le contexte pour le LLM
        context = {
            "recommendation_title": recommendation["title"],
            "suppliers_count": len(suppliers),
            "top_suppliers": [s.name for s in suppliers[:3]],
            "avg_rating": sum((s.rating or 0) for s in suppliers) / len(suppliers) if suppliers else 0,
            "verified_count": sum(1 for s in suppliers if s.verified),
            "price_range": f"{recommendation['estimated_cost_min']}€ - {recommendation['estimated_cost_max']}€"
        }
        
        # Créer le prompt
        prompt = f"""
        Génère un résumé concis (max 120 mots) des fournisseurs disponibles pour réaliser
        la recommandation "{context['recommendation_title']}".
        
        Informations clés:
        - Nombre de fournisseurs trouvés: {context['suppliers_count']}
        - Fournisseurs principaux: {', '.join(context['top_suppliers'])}
        - Note moyenne: {context['avg_rating']:.1f}/5
        - Nombre de fournisseurs vérifiés: {context['verified_count']}
        - Fourchette de prix estimée: {context['price_range']}
        
        Le résumé doit être informatif et rassurant, expliquer la prochaine étape (demander des devis)
        et encourager l'utilisateur à comparer les offres.
        """
        
        # Générer le résumé
        system_message = "Tu es un expert en mise en relation avec des fournisseurs et en travaux de durabilité."
        summary = await self.llm_service.generate_response(prompt, system_message)
        
        return summary
    
    async def request_quote(
        self,
        user_id: UUID4,
        recommendation_id: UUID4,
        supplier_id: UUID4,
        property_id: Optional[UUID4] = None,
        details: str = "",
        preferred_contact_method: str = "email",
        preferred_timeframe: Optional[str] = None
    ) -> QuoteResponse:
        """Envoie une demande de devis à un fournisseur"""
        # Vérifier que le fournisseur existe
        supplier = next((s for s in SUPPLIERS_DATABASE if s["id"] == str(supplier_id)), None)
        if not supplier:
            raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
        
        # Générer un ID de requête
        request_id = uuid.uuid4()
        
        # Pour le MVP, on simule simplement l'envoi (à implémenter: envoi réel d'email, notification, etc.)
        estimated_response_time = "3-5 jours ouvrables"
        
        # Note: dans une implémentation réelle, on sauvegarderait la demande en base de données
        # et on enverrait une notification au fournisseur
        
        return QuoteResponse(
            request_id=request_id,
            status="sent",
            estimated_response_time=estimated_response_time
        )
    
    async def register_supplier(
        self,
        registration: SupplierRegistration
    ) -> Supplier:
        """Enregistre un nouveau fournisseur"""
        # Générer un ID unique
        supplier_id = uuid.uuid4()
        
        # Pour le MVP, on simule l'enregistrement (à implémenter: sauvegarde en BD)
        new_supplier = Supplier(
            id=supplier_id,
            name=registration.name,
            description=registration.description,
            domains=registration.domains,
            regions_served=registration.regions_served,
            address=registration.address,
            postal_code=registration.postal_code,
            city=registration.city,
            contact_email=registration.contact_email,
            contact_phone=registration.contact_phone,
            website=registration.website,
            vat_number=registration.vat_number,
            rating=None,
            verified=False,
            active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return new_supplier
    
    async def create_project(
        self,
        user_id: UUID4,
        recommendation_id: UUID4,
        supplier_id: UUID4,
        property_id: Optional[UUID4] = None,
        start_date: Optional[datetime] = None,
        notes: Optional[str] = None
    ) -> Project:
        """Crée un nouveau projet pour suivre l'implémentation d'une recommandation"""
        # Vérifier que le fournisseur existe
        supplier = next((s for s in SUPPLIERS_DATABASE if s["id"] == str(supplier_id)), None)
        if not supplier:
            raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
        
        # Pour le MVP, on simule la création de projet (à implémenter: sauvegarde en BD)
        project = Project(
            id=uuid.uuid4(),
            user_id=user_id,
            recommendation_id=recommendation_id,
            property_id=property_id,
            supplier_id=supplier_id,
            status="planning",
            start_date=start_date,
            completion_date=None,
            actual_cost=None,
            notes=notes,
            verification_status="pending",
            verification_date=None,
            verification_documents=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return project


# Initialisation du service
procurement_service = ProcurementService()

# Routes API
@app.post("/api/v1/find-suppliers", response_model=SupplierSearchResponse)
async def find_suppliers(
    request: SupplierSearchRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour les requêtes de recherche de fournisseurs"""
    return await procurement_service.find_suitable_suppliers(
        user_id=request.user_id,
        recommendation_id=request.recommendation_id,
        postal_code=request.postal_code,
        max_distance_km=request.max_distance_km or 50
    )


@app.post("/api/v1/request-quote", response_model=QuoteResponse)
async def request_quote(
    request: QuoteRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour les demandes de devis"""
    return await procurement_service.request_quote(
        user_id=request.user_id,
        recommendation_id=request.recommendation_id,
        supplier_id=request.supplier_id,
        property_id=request.property_id,
        details=request.details,
        preferred_contact_method=request.preferred_contact_method,
        preferred_timeframe=request.preferred_timeframe
    )


@app.post("/api/v1/register-supplier", response_model=Supplier)
async def register_supplier(
    registration: SupplierRegistration,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour l'inscription des fournisseurs"""
    return await procurement_service.register_supplier(registration)


@app.post("/api/v1/create-project", response_model=Project)
async def create_project(
    request: ProjectCreationRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour la création de projets"""
    return await procurement_service.create_project(
        user_id=request.user_id,
        recommendation_id=request.recommendation_id,
        supplier_id=request.supplier_id,
        property_id=request.property_id,
        start_date=request.start_date,
        notes=request.notes
    )


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Lancer le serveur en mode développement
    port = int(os.getenv("PORT", "8004"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
