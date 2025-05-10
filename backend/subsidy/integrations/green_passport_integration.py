"""
Module d'intégration entre l'Agent de Subventions et le service de Passeport Vert.
Permet de récupérer les informations sur les propriétés des utilisateurs et de suggérer des subventions adaptées.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ..data.subsidies_extended import Domain, Region, UserType, Language
from ..data.subsidy_data_manager import subsidy_data_manager

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL de base du service de passeport vert (à configurer selon l'environnement)
GREEN_PASSPORT_SERVICE_URL = "http://localhost:8004/api/green-passport"

class PropertyInfo(BaseModel):
    """Modèle pour les informations d'une propriété."""
    id: str
    user_id: str
    address: str
    postal_code: str
    city: str
    region: str
    property_type: str
    year_built: Optional[int] = None
    living_area: Optional[float] = None
    energy_performance: Optional[str] = None
    heating_system: Optional[str] = None
    insulation_level: Optional[str] = None
    renewable_energy_sources: List[str] = []
    water_management_systems: List[str] = []
    waste_management_systems: List[str] = []
    mobility_options: List[str] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserProfile(BaseModel):
    """Modèle pour le profil d'un utilisateur."""
    id: str
    email: str
    first_name: str
    last_name: str
    user_type: str
    language_preference: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class SubsidyPropertyRecommendation(BaseModel):
    """Modèle pour une recommandation de subvention basée sur une propriété."""
    subsidy_id: str
    name: str
    provider: str
    description: str
    max_amount: Optional[float] = None
    percentage: Optional[float] = None
    relevance_score: float  # Score de pertinence de 0 à 1
    property_id: str  # ID de la propriété associée
    property_address: str  # Adresse de la propriété associée
    match_reason: str  # Raison de la correspondance

class GreenPassportIntegrationService:
    """Service d'intégration avec le service de passeport vert."""
    
    def __init__(self, language: Language = Language.FR):
        """Initialise le service d'intégration."""
        self.language = language
    
    def get_property_info(self, property_id: str) -> Optional[PropertyInfo]:
        """
        Récupère les informations d'une propriété depuis le service de passeport vert.
        
        Args:
            property_id: ID de la propriété
            
        Returns:
            Informations de la propriété ou None si non trouvée
        """
        try:
            response = requests.get(f"{GREEN_PASSPORT_SERVICE_URL}/properties/{property_id}")
            response.raise_for_status()
            return PropertyInfo(**response.json())
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération des informations de la propriété: {e}")
            return None
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """
        Récupère le profil d'un utilisateur depuis le service de passeport vert.
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Profil de l'utilisateur ou None si non trouvé
        """
        try:
            response = requests.get(f"{GREEN_PASSPORT_SERVICE_URL}/users/{user_id}")
            response.raise_for_status()
            return UserProfile(**response.json())
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération du profil utilisateur: {e}")
            return None
    
    def _map_region_string_to_enum(self, region_str: str) -> Optional[Region]:
        """
        Mappe une chaîne de région à l'énumération Region.
        
        Args:
            region_str: Chaîne représentant la région
            
        Returns:
            Énumération Region correspondante
        """
        region_mapping = {
            "wallonie": Region.WALLONIE,
            "bruxelles": Region.BRUXELLES,
            "flandre": Region.FLANDRE,
            "federal": Region.FEDERAL
        }
        return region_mapping.get(region_str.lower())
    
    def _map_user_type_string_to_enum(self, user_type_str: str) -> Optional[UserType]:
        """
        Mappe une chaîne de type d'utilisateur à l'énumération UserType.
        
        Args:
            user_type_str: Chaîne représentant le type d'utilisateur
            
        Returns:
            Énumération UserType correspondante
        """
        user_type_mapping = {
            "individual": UserType.INDIVIDUAL,
            "self_employed": UserType.SELF_EMPLOYED,
            "small_business": UserType.SMALL_BUSINESS,
            "medium_business": UserType.MEDIUM_BUSINESS,
            "large_business": UserType.LARGE_BUSINESS,
            "public_entity": UserType.PUBLIC_ENTITY,
            "non_profit": UserType.NON_PROFIT
        }
        return user_type_mapping.get(user_type_str.lower())
    
    def _map_property_type_to_domains(self, property_type: str) -> List[Domain]:
        """
        Mappe un type de propriété à des domaines de subvention potentiels.
        
        Args:
            property_type: Type de propriété
            
        Returns:
            Liste des domaines de subvention potentiels
        """
        # Par défaut, tous les types de propriété peuvent bénéficier de subventions dans ces domaines
        domains = [Domain.ENERGY, Domain.WATER, Domain.WASTE]
        
        # Ajouter des domaines spécifiques selon le type de propriété
        if property_type.lower() in ["house", "apartment", "building"]:
            domains.append(Domain.RENOVATION)
        
        if property_type.lower() in ["house", "land"]:
            domains.append(Domain.BIODIVERSITY)
        
        if property_type.lower() in ["office", "commercial", "industrial"]:
            domains.append(Domain.CIRCULAR_ECONOMY)
            domains.append(Domain.MOBILITY)
        
        return domains
    
    def _calculate_relevance_score(self, subsidy, property_info: PropertyInfo, user_profile: Optional[UserProfile] = None) -> float:
        """
        Calcule un score de pertinence entre une subvention et une propriété/utilisateur.
        
        Args:
            subsidy: Subvention à évaluer
            property_info: Informations sur la propriété
            user_profile: Profil de l'utilisateur (optionnel)
            
        Returns:
            Score de pertinence entre 0 et 1
        """
        score = 0.0
        
        # Vérifier la correspondance de région (facteur très important)
        property_region = self._map_region_string_to_enum(property_info.region)
        if property_region and property_region in subsidy.regions:
            score += 0.4
        
        # Vérifier la correspondance de type d'utilisateur
        if user_profile:
            user_type = self._map_user_type_string_to_enum(user_profile.user_type)
            if user_type and user_type in subsidy.user_types:
                score += 0.2
        
        # Vérifier la correspondance d'année de construction
        if property_info.year_built and subsidy.min_year_built and subsidy.max_year_built:
            if subsidy.min_year_built <= property_info.year_built <= subsidy.max_year_built:
                score += 0.2
        
        # Vérifier la correspondance de domaine
        property_domains = self._map_property_type_to_domains(property_info.property_type)
        matching_domains = set(property_domains).intersection(set(subsidy.domains))
        if matching_domains:
            score += 0.2 * (len(matching_domains) / len(subsidy.domains))
        
        return min(score, 1.0)  # Plafonner à 1.0
    
    def _generate_match_reason(self, subsidy, property_info: PropertyInfo, user_profile: Optional[UserProfile] = None) -> str:
        """
        Génère une explication de la correspondance entre une subvention et une propriété/utilisateur.
        
        Args:
            subsidy: Subvention à expliquer
            property_info: Informations sur la propriété
            user_profile: Profil de l'utilisateur (optionnel)
            
        Returns:
            Explication textuelle de la correspondance
        """
        reasons = []
        
        # Vérifier la correspondance de région
        property_region = self._map_region_string_to_enum(property_info.region)
        if property_region and property_region in subsidy.regions:
            if self.language == Language.FR:
                reasons.append(f"Cette subvention est disponible dans votre région ({property_info.region})")
            else:
                reasons.append(f"Deze subsidie is beschikbaar in uw regio ({property_info.region})")
        
        # Vérifier la correspondance de type d'utilisateur
        if user_profile:
            user_type = self._map_user_type_string_to_enum(user_profile.user_type)
            if user_type and user_type in subsidy.user_types:
                if self.language == Language.FR:
                    reasons.append(f"Vous êtes éligible en tant que {user_profile.user_type}")
                else:
                    reasons.append(f"U komt in aanmerking als {user_profile.user_type}")
        
        # Vérifier la correspondance d'année de construction
        if property_info.year_built and subsidy.min_year_built and subsidy.max_year_built:
            if subsidy.min_year_built <= property_info.year_built <= subsidy.max_year_built:
                if self.language == Language.FR:
                    reasons.append(f"L'année de construction de votre propriété ({property_info.year_built}) est dans la plage éligible")
                else:
                    reasons.append(f"Het bouwjaar van uw eigendom ({property_info.year_built}) valt binnen het in aanmerking komende bereik")
        
        # Mentionner le montant de la subvention
        if subsidy.max_amount:
            if self.language == Language.FR:
                reasons.append(f"Montant maximum de la subvention: {subsidy.max_amount}€")
            else:
                reasons.append(f"Maximaal subsidiebedrag: {subsidy.max_amount}€")
        elif subsidy.percentage:
            if self.language == Language.FR:
                reasons.append(f"Pourcentage de couverture: {subsidy.percentage}%")
            else:
                reasons.append(f"Dekkingspercentage: {subsidy.percentage}%")
        
        # Assembler les raisons
        if self.language == Language.FR:
            return " | ".join(reasons) if reasons else "Subvention potentiellement pertinente pour votre propriété"
        else:
            return " | ".join(reasons) if reasons else "Potentieel relevante subsidie voor uw eigendom"
    
    def find_subsidies_for_property(self, property_id: str, user_id: Optional[str] = None) -> List[SubsidyPropertyRecommendation]:
        """
        Trouve les subventions adaptées à une propriété spécifique.
        
        Args:
            property_id: ID de la propriété
            user_id: ID de l'utilisateur (optionnel)
            
        Returns:
            Liste des subventions recommandées avec scores de pertinence
        """
        property_info = self.get_property_info(property_id)
        if not property_info:
            logger.error(f"Propriété {property_id} non trouvée")
            return []
        
        user_profile = None
        if user_id:
            user_profile = self.get_user_profile(user_id)
        
        # Déterminer la région de la propriété
        property_region = self._map_region_string_to_enum(property_info.region)
        
        # Rechercher les subventions dans cette région
        subsidies = []
        if property_region:
            subsidies = subsidy_data_manager.get_subsidies_by_region(property_region)
        
        # Calculer les scores de pertinence et filtrer les subventions pertinentes
        subsidy_recommendations = []
        for subsidy in subsidies:
            score = self._calculate_relevance_score(subsidy, property_info, user_profile)
            if score >= 0.3:  # Seuil minimum de pertinence
                match_reason = self._generate_match_reason(subsidy, property_info, user_profile)
                
                subsidy_dict = subsidy_data_manager.get_subsidy_details_dict(subsidy.id, self.language)
                subsidy_recommendations.append(
                    SubsidyPropertyRecommendation(
                        subsidy_id=subsidy.id,
                        name=subsidy_dict["name"],
                        provider=subsidy_dict["provider"],
                        description=subsidy_dict["description"],
                        max_amount=subsidy_dict["max_amount"],
                        percentage=subsidy_dict["percentage"],
                        relevance_score=score,
                        property_id=property_info.id,
                        property_address=property_info.address,
                        match_reason=match_reason
                    )
                )
        
        # Trier par score de pertinence décroissant
        subsidy_recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return subsidy_recommendations

# Instance singleton du service d'intégration
green_passport_integration_service = GreenPassportIntegrationService()
