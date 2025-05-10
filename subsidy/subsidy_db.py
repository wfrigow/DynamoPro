"""
Base de données de subventions pour la Belgique
----------------------------------------------
Module contenant une base de données structurée et exhaustive des subventions 
et aides financières disponibles en Belgique pour les projets d'économie d'énergie, 
d'eau, de déchets et de biodiversité.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Set

from pydantic import BaseModel, Field, validator

from enum import Enum

class SubsidyType(str, Enum):
    """Types de subventions"""
    PRIME = "prime"                    # Subvention directe
    TAX_REDUCTION = "tax_reduction"    # Réduction d'impôt
    LOAN = "loan"                      # Prêt à taux avantageux
    GRANT = "grant"                    # Subvention sur projet
    VOUCHER = "voucher"                # Chèque-entreprise ou similaire
    TAX_CREDIT = "tax_credit"          # Crédit d'impôt
    OTHER = "other"                    # Autre type

class SubsidyConditionType(str, Enum):
    """Types de conditions pour les subventions"""
    TECHNICAL = "technical"            # Conditions techniques (ex: performance énergétique)
    FINANCIAL = "financial"            # Conditions financières (ex: revenus max)
    ADMINISTRATIVE = "administrative"  # Conditions administratives (ex: permis)
    TEMPORAL = "temporal"              # Conditions temporelles (ex: date limite)
    GEOGRAPHIC = "geographic"          # Conditions géographiques (ex: zone spécifique)
    PROVIDER = "provider"              # Conditions liées au prestataire
    OTHER = "other"                    # Autres conditions

class SubsidyProvider(BaseModel):
    """Organisation fournissant une subvention"""
    id: str
    name: str
    type: str = "public"  # public, private, mixed
    level: str  # federal, regional, provincial, municipal, private
    website: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None

class SubsidyCondition(BaseModel):
    """Condition spécifique pour l'éligibilité à une subvention"""
    type: SubsidyConditionType
    description: str
    technical_parameter: Optional[str] = None  # ex: "r_value", "cop", "efficiency"
    technical_value: Optional[Union[str, float, int]] = None
    metadata: Optional[Dict[str, Any]] = None

class SubsidyKeyword(str, Enum):
    """Mots-clés pour classifier et rechercher des subventions"""
    SOLAR = "solar"
    HEAT_PUMP = "heat_pump"
    INSULATION = "insulation"
    WINDOWS = "windows"
    LED = "led"
    RAINWATER = "rainwater"
    AUDIT = "audit"
    RENOVATION = "renovation"
    HEATING = "heating"
    VENTILATION = "ventilation"
    BIODIVERSITY = "biodiversity"
    CIRCULAR = "circular"
    WASTE = "waste"
    EV_CHARGING = "ev_charging"
    BATTERY = "battery"
    GREEN_ROOF = "green_roof"
    WATER_SAVING = "water_saving"
    BIOMASS = "biomass"
    COGENERATION = "cogeneration"

class SubsidyDocumentType(str, Enum):
    """Types de documents nécessaires pour une demande de subvention"""
    IDENTITY = "identity"              # Carte d'identité, etc.
    OWNERSHIP = "ownership"            # Preuve de propriété
    INVOICE = "invoice"                # Facture
    QUOTE = "quote"                    # Devis
    TECHNICAL_SPEC = "technical_spec"  # Spécifications techniques
    CERTIFICATE = "certificate"        # Certificat ou attestation
    PERMIT = "permit"                  # Permis (d'urbanisme, etc.)
    TAX = "tax"                        # Document fiscal
    PHOTOS = "photos"                  # Photos (avant/après)
    PLAN = "plan"                      # Plans ou schémas
    FORM = "form"                      # Formulaire spécifique
    OTHER = "other"                    # Autre type de document

class RequiredDocument(BaseModel):
    """Document requis pour une demande de subvention"""
    type: SubsidyDocumentType
    description: str
    url_template: Optional[str] = None  # Lien vers le modèle si disponible
    notes: Optional[str] = None

class Subsidy(BaseModel):
    """Modèle complet d'une subvention"""
    id: str
    name: str
    description: str
    provider_id: str
    
    # Classification
    regions: List[str]  # wallonie, flandre, bruxelles
    eligible_user_types: List[str]  # individual, self_employed, small_business, etc.
    domains: List[str]  # energy, water, waste, biodiversity
    subsidy_type: SubsidyType
    keywords: List[SubsidyKeyword] = []
    
    # Bénéfices financiers
    max_amount: Optional[float] = None
    percentage: Optional[float] = None
    min_amount: Optional[float] = None
    calculation_formula: Optional[str] = None  # Formule de calcul si complexe
    
    # Éligibilité
    conditions: List[SubsidyCondition]
    required_documents: List[RequiredDocument]
    
    # Processus
    application_process: str
    documentation_url: str
    application_url: Optional[str] = None
    typical_processing_time_days: Optional[int] = None
    
    # Métadonnées
    active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    popularity_score: Optional[float] = None  # Score interne de popularité
    success_rate: Optional[float] = None  # Taux d'acceptation estimé
    
    # Informations complémentaires
    compatibility: List[str] = []  # IDs d'autres subventions compatibles
    incompatibility: List[str] = []  # IDs d'autres subventions incompatibles
    notes: Optional[str] = None
    
    @validator('keywords')
    def check_keywords(cls, v):
        """Vérifie que les mots-clés sont valides"""
        if not v:
            return []
        return v
    
    def is_active(self) -> bool:
        """Vérifie si la subvention est active à la date actuelle"""
        now = datetime.now()
        if not self.active:
            return False
        if self.end_date and self.end_date < now:
            return False
        if self.start_date and self.start_date > now:
            return False
        return True
    
    def matches_user_profile(self, user_type: str, region: str) -> bool:
        """Vérifie si la subvention correspond au profil utilisateur"""
        return (
            user_type in self.eligible_user_types and
            region in self.regions
        )
    
    def matches_recommendation(self, recommendation: Dict[str, Any]) -> bool:
        """Vérifie si la subvention correspond à une recommandation"""
        # Vérification basique du domaine
        if recommendation.get("domain") not in self.domains:
            return False
        
        # Correspondance par mots-clés
        rec_title = recommendation.get("title", "").lower()
        rec_description = recommendation.get("description", "").lower()
        
        # Vérification plus fine par mot-clé
        for keyword in self.keywords:
            keyword_str = keyword.value
            if keyword_str in rec_title or keyword_str in rec_description:
                return True
                
        # Vérifications spécifiques par type de projet
        if "panneau" in rec_title and "solaire" in rec_title and "solar" in [k.value for k in self.keywords]:
            return True
        if "isolation" in rec_title and "insulation" in [k.value for k in self.keywords]:
            return True
        if "pompe à chaleur" in rec_title and "heat_pump" in [k.value for k in self.keywords]:
            return True
        if "fenêtre" in rec_title and "windows" in [k.value for k in self.keywords]:
            return True
        if "eau de pluie" in rec_title and "rainwater" in [k.value for k in self.keywords]:
            return True
        
        return False
    
    def calculate_amount(self, cost: float) -> Dict[str, Any]:
        """Calcule le montant de la subvention pour un coût donné"""
        result = {
            "subsidy_id": self.id,
            "subsidy_name": self.name,
            "amount": 0,
            "percentage": self.percentage,
            "calculation_method": "unknown"
        }
        
        if self.percentage is not None:
            amount = cost * (self.percentage / 100)
            result["amount"] = amount
            result["calculation_method"] = "percentage"
            
            # Appliquer min/max si définis
            if self.max_amount is not None and amount > self.max_amount:
                result["amount"] = self.max_amount
                result["calculation_method"] = "percentage_capped"
            
            if self.min_amount is not None and amount < self.min_amount:
                result["amount"] = self.min_amount
                result["calculation_method"] = "percentage_min_applied"
        
        elif self.max_amount is not None:
            # Montant fixe
            result["amount"] = self.max_amount
            result["calculation_method"] = "fixed_amount"
            
        # Arrondir le montant
        result["amount"] = round(result["amount"], 2)
        
        return result
    
    def get_application_instructions(self) -> Dict[str, Any]:
        """Obtient les instructions pour la demande"""
        return {
            "subsidy_id": self.id,
            "subsidy_name": self.name,
            "provider": self.provider_id,
            "application_process": self.application_process,
            "documentation_url": self.documentation_url,
            "application_url": self.application_url,
            "required_documents": [doc.dict() for doc in self.required_documents],
            "typical_processing_time_days": self.typical_processing_time_days
        }


class SubsidyDatabase:
    """Gestionnaire de la base de données de subventions"""
    
    def __init__(self, load_from_file: bool = True, file_path: Optional[str] = None):
        """Initialise la base de données, éventuellement à partir d'un fichier"""
        self.subsidies: Dict[str, Subsidy] = {}
        self.providers: Dict[str, SubsidyProvider] = {}
        self.logger = logging.getLogger("subsidy_db")
        
        # Chargement depuis un fichier si demandé
        if load_from_file and file_path and os.path.exists(file_path):
            self._load_from_file(file_path)
        else:
            self._load_default_data()
    
    def _load_from_file(self, file_path: str) -> None:
        """Charge les données depuis un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Charger les fournisseurs
            for provider_data in data.get("providers", []):
                provider = SubsidyProvider(**provider_data)
                self.providers[provider.id] = provider
            
            # Charger les subventions
            for subsidy_data in data.get("subsidies", []):
                subsidy = Subsidy(**subsidy_data)
                self.subsidies[subsidy.id] = subsidy
                
            self.logger.info(f"Loaded {len(self.subsidies)} subsidies and {len(self.providers)} providers from file")
        except Exception as e:
            self.logger.error(f"Error loading subsidy database from file: {e}")
            # Charger les données par défaut en cas d'erreur
            self._load_default_data()
    
    def _load_default_data(self) -> None:
        """Charge des données d'exemple par défaut"""
        # Créer quelques fournisseurs
        provider1 = SubsidyProvider(
            id="rw-energie",
            name="Service Public de Wallonie - Énergie",
            type="public",
            level="regional",
            website="https://energie.wallonie.be"
        )
        
        provider2 = SubsidyProvider(
            id="spf-finance",
            name="Service Public Fédéral Finances",
            type="public",
            level="federal",
            website="https://finances.belgium.be"
        )
        
        self.providers = {
            provider1.id: provider1,
            provider2.id: provider2
        }
        
        # Créer des documents requis
        isolation_docs = [
            RequiredDocument(
                type=SubsidyDocumentType.IDENTITY,
                description="Copie de la carte d'identité du demandeur"
            ),
            RequiredDocument(
                type=SubsidyDocumentType.OWNERSHIP,
                description="Preuve de propriété ou bail"
            ),
            RequiredDocument(
                type=SubsidyDocumentType.INVOICE,
                description="Facture détaillée des travaux"
            ),
            RequiredDocument(
                type=SubsidyDocumentType.TECHNICAL_SPEC,
                description="Fiche technique du matériau isolant utilisé"
            ),
            RequiredDocument(
                type=SubsidyDocumentType.CERTIFICATE,
                description="Attestation de l'entrepreneur"
            )
        ]
        
        # Créer des conditions
        isolation_conditions = [
            SubsidyCondition(
                type=SubsidyConditionType.TECHNICAL,
                description="Le coefficient de résistance thermique R doit être ≥ 4,5 m²K/W",
                technical_parameter="r_value",
                technical_value=4.5
            ),
            SubsidyCondition(
                type=SubsidyConditionType.PROVIDER,
                description="Les travaux doivent être réalisés par un entrepreneur enregistré"
            ),
            SubsidyCondition(
                type=SubsidyConditionType.TEMPORAL,
                description="Les travaux doivent être réalisés après le 1er janvier 2023"
            )
        ]
        
        # Créer une subvention
        subsidy1 = Subsidy(
            id="prime-isolation-toiture-rw-2023",
            name="Prime Énergie - Isolation Toiture",
            description="Prime pour l'isolation thermique du toit ou des combles dans une habitation existante. Cette prime vise à améliorer l'efficacité énergétique des habitations.",
            provider_id=provider1.id,
            regions=["wallonie"],
            eligible_user_types=["individual", "self_employed", "small_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.INSULATION, SubsidyKeyword.RENOVATION],
            max_amount=2000,
            percentage=35,
            conditions=isolation_conditions,
            required_documents=isolation_docs,
            application_process="Demande en ligne via le portail Energie de la Région Wallonne.",
            documentation_url="https://energie.wallonie.be/fr/prime-isolation-du-toit.html",
            application_url="https://monespace.wallonie.be",
            typical_processing_time_days=60,
            active=True
        )
        
        self.subsidies = {subsidy1.id: subsidy1}
        self.logger.info("Loaded default subsidy data")
    
    def save_to_file(self, file_path: str) -> bool:
        """Sauvegarde la base de données dans un fichier JSON"""
        try:
            data = {
                "providers": [provider.dict() for provider in self.providers.values()],
                "subsidies": [subsidy.dict() for subsidy in self.subsidies.values()]
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, default=str, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved subsidy database to {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving subsidy database to file: {e}")
            return False
    
    def get_all_subsidies(self, active_only: bool = True) -> List[Subsidy]:
        """Récupère toutes les subventions, optionnellement uniquement les actives"""
        if active_only:
            return [s for s in self.subsidies.values() if s.is_active()]
        return list(self.subsidies.values())
    
    def get_subsidy(self, subsidy_id: str) -> Optional[Subsidy]:
        """Récupère une subvention par son ID"""
        return self.subsidies.get(subsidy_id)
    
    def get_provider(self, provider_id: str) -> Optional[SubsidyProvider]:
        """Récupère un fournisseur par son ID"""
        return self.providers.get(provider_id)
    
    def get_subsidies_by_domain(self, domain: str, active_only: bool = True) -> List[Subsidy]:
        """Récupère les subventions par domaine"""
        if active_only:
            return [s for s in self.subsidies.values() if domain in s.domains and s.is_active()]
        return [s for s in self.subsidies.values() if domain in s.domains]
    
    def get_subsidies_by_region(self, region: str, active_only: bool = True) -> List[Subsidy]:
        """Récupère les subventions par région"""
        if active_only:
            return [s for s in self.subsidies.values() if region in s.regions and s.is_active()]
        return [s for s in self.subsidies.values() if region in s.regions]
    
    def get_subsidies_by_user_type(self, user_type: str, active_only: bool = True) -> List[Subsidy]:
        """Récupère les subventions par type d'utilisateur"""
        if active_only:
            return [s for s in self.subsidies.values() if user_type in s.eligible_user_types and s.is_active()]
        return [s for s in self.subsidies.values() if user_type in s.eligible_user_types]
    
    def find_applicable_subsidies(
        self,
        user_type: str,
        region: str,
        domains: Optional[List[str]] = None,
        recommendations: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Trouve les subventions applicables en fonction du profil utilisateur et des recommandations
        
        Args:
            user_type: Type d'utilisateur (individual, self_employed, etc.)
            region: Région (wallonie, flandre, bruxelles)
            domains: Liste optionnelle de domaines à inclure
            recommendations: Liste optionnelle de recommandations
        
        Returns:
            Liste de subventions applicables avec montants calculés
        """
        applicable_subsidies = []
        
        # Filtrer par domaine si spécifié
        subsidies = self.get_all_subsidies(active_only=True)
        if domains:
            subsidies = [s for s in subsidies if any(d in s.domains for d in domains)]
        
        # Filtrer par profil utilisateur
        subsidies = [s for s in subsidies if s.matches_user_profile(user_type, region)]
        
        # Si des recommandations sont fournies, associer les subventions appropriées
        if recommendations and len(recommendations) > 0:
            # Pour chaque recommandation, trouver les subventions qui s'appliquent
            for recommendation in recommendations:
                rec_subsidies = []
                for subsidy in subsidies:
                    if subsidy.matches_recommendation(recommendation):
                        # Calculer le montant de la subvention
                        cost = (recommendation.get("estimated_cost_min", 0) + recommendation.get("estimated_cost_max", 0)) / 2
                        if cost <= 0:
                            cost = recommendation.get("estimated_cost", 5000)  # Valeur par défaut
                        
                        subsidy_amount = subsidy.calculate_amount(cost)
                        
                        # Ajouter les détails de la recommandation
                        subsidy_amount["recommendation_id"] = recommendation.get("id")
                        subsidy_amount["recommendation_title"] = recommendation.get("title")
                        
                        rec_subsidies.append(subsidy_amount)
                
                applicable_subsidies.extend(rec_subsidies)
        else:
            # Sans recommandations, retourner toutes les subventions applicables
            for subsidy in subsidies:
                # Utiliser un coût moyen typique
                subsidy_amount = subsidy.calculate_amount(5000)
                applicable_subsidies.append(subsidy_amount)
        
        return applicable_subsidies
    
    def get_application_instructions(
        self,
        subsidy_id: str,
        recommendation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtient les instructions pour la demande d'une subvention
        
        Args:
            subsidy_id: ID de la subvention
            recommendation_id: ID optionnel de la recommandation associée
        
        Returns:
            Dictionnaire contenant les instructions et documents requis
        """
        subsidy = self.get_subsidy(subsidy_id)
        if not subsidy:
            return {"error": "Subsidy not found"}
        
        instructions = subsidy.get_application_instructions()
        
        # Ajouter des informations sur le fournisseur
        provider = self.get_provider(subsidy.provider_id)
        if provider:
            instructions["provider_name"] = provider.name
            instructions["provider_website"] = provider.website
            instructions["provider_contact_email"] = provider.contact_email
            instructions["provider_contact_phone"] = provider.contact_phone
        
        # Ajouter l'ID de recommandation si fourni
        if recommendation_id:
            instructions["recommendation_id"] = recommendation_id
        
        return instructions
    
    def add_subsidy(self, subsidy: Subsidy) -> bool:
        """Ajoute une nouvelle subvention à la base de données"""
        if subsidy.id in self.subsidies:
            return False
        self.subsidies[subsidy.id] = subsidy
        return True
    
    def update_subsidy(self, subsidy: Subsidy) -> bool:
        """Met à jour une subvention existante"""
        if subsidy.id not in self.subsidies:
            return False
        self.subsidies[subsidy.id] = subsidy
        return True
    
    def add_provider(self, provider: SubsidyProvider) -> bool:
        """Ajoute un nouveau fournisseur à la base de données"""
        if provider.id in self.providers:
            return False
        self.providers[provider.id] = provider
        return True


# Création d'une instance globale de la base de données
subsidy_db = SubsidyDatabase(load_from_file=False)

# Fonction pratique pour obtenir l'instance de la base de données
def get_subsidy_database() -> SubsidyDatabase:
    """Retourne l'instance globale de la base de données de subventions"""
    return subsidy_db
