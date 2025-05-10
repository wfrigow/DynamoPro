"""
Modèles de données partagés pour tous les composants DynamoPro
--------------------------------------------------------------
Ce module définit les modèles de base utilisés par tous les services
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr


class UserType(str, Enum):
    """Types d'utilisateurs supportés par le système"""
    INDIVIDUAL = "individual"  # Particulier
    SELF_EMPLOYED = "self_employed"  # Indépendant
    SMALL_BUSINESS = "small_business"  # TPE
    MEDIUM_BUSINESS = "medium_business"  # PME
    LARGE_BUSINESS = "large_business"  # Grande entreprise


class BelgiumRegion(str, Enum):
    """Régions belges pour les calculs de subventions et réglementations"""
    WALLONIA = "wallonie"
    FLANDERS = "flandre"
    BRUSSELS = "bruxelles"


class Language(str, Enum):
    """Langues supportées par l'application"""
    FRENCH = "fr"
    DUTCH = "nl"
    GERMAN = "de"
    ENGLISH = "en"


class DomainType(str, Enum):
    """Domaines d'optimisation couverts par DynamoPro"""
    ENERGY = "energy"
    WATER = "water"
    WASTE = "waste"  # Future extension
    BIODIVERSITY = "biodiversity"  # Future extension


class SubscriptionType(str, Enum):
    """Types d'abonnements disponibles"""
    FREE = "free"
    PREMIUM = "premium"  # 9.99€ premium


class UserProfile(BaseModel):
    """Profil utilisateur complet"""
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: str
    user_type: UserType
    region: BelgiumRegion
    postal_code: str
    address: Optional[str] = None
    phone: Optional[str] = None
    language: Language = Language.FRENCH
    company_name: Optional[str] = None
    company_size: Optional[int] = None  # Nombre d'employés si applicable
    company_vat: Optional[str] = None  # Numéro TVA si applicable
    subscription_type: SubscriptionType = SubscriptionType.FREE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True


class ConsumptionData(BaseModel):
    """Données de consommation (énergie ou eau)"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    domain: DomainType
    start_date: datetime
    end_date: datetime
    consumption_kwh: Optional[float] = None  # Pour l'énergie
    consumption_m3: Optional[float] = None  # Pour l'eau
    cost: float  # Coût en euros
    provider: str
    contract_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "manual"  # manual, ocr, api, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Property(BaseModel):
    """Informations sur la propriété (bâtiment/logement)"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    name: str  # Ex: "Maison principale", "Bureau"
    type: str  # Appartement, Maison, Bureau, etc.
    size_m2: float
    built_year: Optional[int] = None
    renovation_year: Optional[int] = None
    energy_class: Optional[str] = None  # A, B, C, etc.
    heating_type: Optional[str] = None
    occupants: Optional[int] = None
    address: Optional[str] = None
    postal_code: str
    city: str
    region: BelgiumRegion
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Recommendation(BaseModel):
    """Recommandation d'amélioration générée par l'Optimizer Agent"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    property_id: Optional[UUID] = None
    domain: DomainType
    title: str
    description: str
    estimated_cost_min: float
    estimated_cost_max: float
    estimated_savings_per_year: float
    estimated_roi_months: int
    ecological_impact_score: int  # Score de 1 à 10
    difficulty: int  # Score de 1 à 10
    applicable_subsidies: List[UUID] = Field(default_factory=list)
    priority_score: float  # Score calculé pour priorisation
    status: str = "pending"  # pending, accepted, rejected, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Subsidy(BaseModel):
    """Subvention ou aide financière disponible"""
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    provider: str  # Ex: "Région Wallonne", "Gouvernement Fédéral"
    regions: List[BelgiumRegion]
    eligible_user_types: List[UserType]
    domains: List[DomainType]
    max_amount: Optional[float] = None
    percentage: Optional[float] = None  # % du coût total couvert
    conditions: str
    documentation_url: str
    application_process: str
    expiration_date: Optional[datetime] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubsidyApplication(BaseModel):
    """Demande de subvention initiée par un utilisateur"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    subsidy_id: UUID
    recommendation_id: Optional[UUID] = None
    status: str  # draft, submitted, pending, approved, rejected
    submission_date: Optional[datetime] = None
    response_date: Optional[datetime] = None
    amount_requested: float
    amount_approved: Optional[float] = None
    documents: List[str] = Field(default_factory=list)  # Chemins vers documents
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Supplier(BaseModel):
    """Fournisseur dans le réseau DynamoPro"""
    id: UUID = Field(default_factory=uuid4)
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
    rating: Optional[float] = None
    verified: bool = False
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Project(BaseModel):
    """Projet d'amélioration initié par un utilisateur"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    recommendation_id: UUID
    property_id: Optional[UUID] = None
    supplier_id: Optional[UUID] = None
    status: str  # planning, in_progress, completed, cancelled
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    actual_cost: Optional[float] = None
    notes: Optional[str] = None
    verification_status: str = "pending"  # pending, verified
    verification_date: Optional[datetime] = None
    verification_documents: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GreenPassport(BaseModel):
    """Passeport Vert pour valorisation des actions environnementales"""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    total_score: int
    label: str  # Bronze, Silver, Gold
    completed_projects: List[UUID]  # IDs des projets complétés
    energy_savings_kwh: float = 0
    water_savings_m3: float = 0
    cost_savings_total: float = 0
    co2_savings_kg: float = 0
    issued_date: datetime = Field(default_factory=datetime.utcnow)
    valid_until: Optional[datetime] = None
