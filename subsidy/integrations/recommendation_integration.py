"""
Module d'intégration entre l'Agent de Subventions et le service de Recommandations.
Permet de récupérer les recommandations et de suggérer des subventions adaptées.
"""

import requests
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..data.subsidies_extended import Domain, Region, UserType, Language
from ..data.subsidy_data_manager import subsidy_data_manager

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL de base du service de recommandations (à configurer selon l'environnement)
RECOMMENDATION_SERVICE_URL = "http://localhost:8002/api/recommendations"

class RecommendationItem(BaseModel):
    """Modèle pour un élément de recommandation."""
    id: str
    title: str
    description: str
    domain: str
    priority: int
    estimated_cost: Optional[float] = None
    estimated_savings: Optional[float] = None
    implementation_difficulty: Optional[str] = None
    tags: List[str] = []

class RecommendationSet(BaseModel):
    """Modèle pour un ensemble de recommandations."""
    id: str
    user_id: str
    property_id: str
    created_at: str
    recommendations: List[RecommendationItem]

class SubsidyRecommendation(BaseModel):
    """Modèle pour une recommandation de subvention."""
    subsidy_id: str
    name: str
    provider: str
    description: str
    max_amount: Optional[float] = None
    percentage: Optional[float] = None
    relevance_score: float  # Score de pertinence de 0 à 1
    recommendation_id: str  # ID de la recommandation associée
    recommendation_title: str  # Titre de la recommandation associée
    match_reason: str  # Raison de la correspondance

class RecommendationIntegrationService:
    """Service d'intégration avec le service de recommandations."""
    
    def __init__(self, language: Language = Language.FR):
        """Initialise le service d'intégration."""
        self.language = language
    
    def get_recommendation_set(self, recommendation_set_id: str) -> Optional[RecommendationSet]:
        """
        Récupère un ensemble de recommandations depuis le service de recommandations.
        
        Args:
            recommendation_set_id: ID de l'ensemble de recommandations
            
        Returns:
            Ensemble de recommandations ou None si non trouvé
        """
        try:
            response = requests.get(f"{RECOMMENDATION_SERVICE_URL}/sets/{recommendation_set_id}")
            response.raise_for_status()
            return RecommendationSet(**response.json())
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération des recommandations: {e}")
            return None
    
    def get_recommendation_by_id(self, recommendation_id: str) -> Optional[RecommendationItem]:
        """
        Récupère une recommandation spécifique depuis le service de recommandations.
        
        Args:
            recommendation_id: ID de la recommandation
            
        Returns:
            Recommandation ou None si non trouvée
        """
        try:
            response = requests.get(f"{RECOMMENDATION_SERVICE_URL}/{recommendation_id}")
            response.raise_for_status()
            return RecommendationItem(**response.json())
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération de la recommandation: {e}")
            return None
    
    def _map_domain_to_subsidy_domain(self, recommendation_domain: str) -> Optional[Domain]:
        """
        Mappe le domaine de recommandation au domaine de subvention.
        
        Args:
            recommendation_domain: Domaine de la recommandation
            
        Returns:
            Domaine de subvention correspondant
        """
        domain_mapping = {
            "energy": Domain.ENERGY,
            "water": Domain.WATER,
            "waste": Domain.WASTE,
            "biodiversity": Domain.BIODIVERSITY,
            "renovation": Domain.RENOVATION,
            "mobility": Domain.MOBILITY,
            "circular_economy": Domain.CIRCULAR_ECONOMY
        }
        return domain_mapping.get(recommendation_domain.lower())
    
    def _calculate_relevance_score(self, subsidy, recommendation: RecommendationItem) -> float:
        """
        Calcule un score de pertinence entre une subvention et une recommandation.
        
        Args:
            subsidy: Subvention à évaluer
            recommendation: Recommandation à comparer
            
        Returns:
            Score de pertinence entre 0 et 1
        """
        score = 0.0
        
        # Vérifier la correspondance de domaine (facteur important)
        subsidy_domains = [d.value for d in subsidy.domains]
        if recommendation.domain.lower() in subsidy_domains:
            score += 0.5
        
        # Vérifier les correspondances de mots-clés
        recommendation_tags = [tag.lower() for tag in recommendation.tags]
        subsidy_keywords = [keyword.get(self.language).lower() for keyword in subsidy.keywords]
        
        matching_keywords = set(recommendation_tags).intersection(set(subsidy_keywords))
        if matching_keywords:
            score += 0.3 * (len(matching_keywords) / max(len(recommendation_tags), 1))
        
        # Ajuster en fonction du coût estimé et du montant de la subvention
        if recommendation.estimated_cost and subsidy.max_amount:
            if subsidy.max_amount >= recommendation.estimated_cost * 0.2:  # Couvre au moins 20% du coût
                score += 0.2
        
        return min(score, 1.0)  # Plafonner à 1.0
    
    def _generate_match_reason(self, subsidy, recommendation: RecommendationItem, score: float) -> str:
        """
        Génère une explication de la correspondance entre une subvention et une recommandation.
        
        Args:
            subsidy: Subvention à expliquer
            recommendation: Recommandation associée
            score: Score de pertinence
            
        Returns:
            Explication textuelle de la correspondance
        """
        reasons = []
        
        # Vérifier la correspondance de domaine
        subsidy_domains = [d.value for d in subsidy.domains]
        if recommendation.domain.lower() in subsidy_domains:
            if self.language == Language.FR:
                reasons.append(f"Cette subvention concerne le domaine '{recommendation.domain}' de votre recommandation")
            else:
                reasons.append(f"Deze subsidie heeft betrekking op het '{recommendation.domain}' domein van uw aanbeveling")
        
        # Vérifier les correspondances de mots-clés
        recommendation_tags = [tag.lower() for tag in recommendation.tags]
        subsidy_keywords = [keyword.get(self.language).lower() for keyword in subsidy.keywords]
        
        matching_keywords = set(recommendation_tags).intersection(set(subsidy_keywords))
        if matching_keywords:
            keywords_str = ", ".join(matching_keywords)
            if self.language == Language.FR:
                reasons.append(f"Mots-clés correspondants: {keywords_str}")
            else:
                reasons.append(f"Overeenkomende trefwoorden: {keywords_str}")
        
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
            return " | ".join(reasons) if reasons else "Subvention potentiellement pertinente pour cette recommandation"
        else:
            return " | ".join(reasons) if reasons else "Potentieel relevante subsidie voor deze aanbeveling"
    
    def find_subsidies_for_recommendation(self, recommendation_id: str) -> List[SubsidyRecommendation]:
        """
        Trouve les subventions adaptées à une recommandation spécifique.
        
        Args:
            recommendation_id: ID de la recommandation
            
        Returns:
            Liste des subventions recommandées avec scores de pertinence
        """
        recommendation = self.get_recommendation_by_id(recommendation_id)
        if not recommendation:
            logger.error(f"Recommandation {recommendation_id} non trouvée")
            return []
        
        # Convertir le domaine de recommandation en domaine de subvention
        subsidy_domain = self._map_domain_to_subsidy_domain(recommendation.domain)
        
        # Rechercher les subventions dans ce domaine
        subsidies = []
        if subsidy_domain:
            subsidies = subsidy_data_manager.get_subsidies_by_domain(subsidy_domain)
        
        # Calculer les scores de pertinence et filtrer les subventions pertinentes
        subsidy_recommendations = []
        for subsidy in subsidies:
            score = self._calculate_relevance_score(subsidy, recommendation)
            if score >= 0.3:  # Seuil minimum de pertinence
                match_reason = self._generate_match_reason(subsidy, recommendation, score)
                
                subsidy_dict = subsidy_data_manager.get_subsidy_details_dict(subsidy.id, self.language)
                subsidy_recommendations.append(
                    SubsidyRecommendation(
                        subsidy_id=subsidy.id,
                        name=subsidy_dict["name"],
                        provider=subsidy_dict["provider"],
                        description=subsidy_dict["description"],
                        max_amount=subsidy_dict["max_amount"],
                        percentage=subsidy_dict["percentage"],
                        relevance_score=score,
                        recommendation_id=recommendation.id,
                        recommendation_title=recommendation.title,
                        match_reason=match_reason
                    )
                )
        
        # Trier par score de pertinence décroissant
        subsidy_recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return subsidy_recommendations
    
    def find_subsidies_for_recommendation_set(self, recommendation_set_id: str) -> Dict[str, List[SubsidyRecommendation]]:
        """
        Trouve les subventions adaptées à un ensemble de recommandations.
        
        Args:
            recommendation_set_id: ID de l'ensemble de recommandations
            
        Returns:
            Dictionnaire avec les IDs de recommandation comme clés et les listes de subventions comme valeurs
        """
        recommendation_set = self.get_recommendation_set(recommendation_set_id)
        if not recommendation_set:
            logger.error(f"Ensemble de recommandations {recommendation_set_id} non trouvé")
            return {}
        
        result = {}
        for recommendation in recommendation_set.recommendations:
            subsidies = self.find_subsidies_for_recommendation(recommendation.id)
            result[recommendation.id] = subsidies
        
        return result

# Instance singleton du service d'intégration
recommendation_integration_service = RecommendationIntegrationService()
