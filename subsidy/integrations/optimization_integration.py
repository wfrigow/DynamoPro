"""
Module d'intégration entre l'Agent de Subventions et le service d'Optimisation.
Permet de récupérer les projets d'optimisation et de suggérer des subventions adaptées.
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

# URL de base du service d'optimisation (à configurer selon l'environnement)
OPTIMIZATION_SERVICE_URL = "http://localhost:8003/api/optimization"

class OptimizationMeasure(BaseModel):
    """Modèle pour une mesure d'optimisation."""
    id: str
    name: str
    description: str
    domain: str
    estimated_cost: Optional[float] = None
    estimated_savings: Optional[float] = None
    estimated_roi: Optional[float] = None
    implementation_time: Optional[str] = None
    tags: List[str] = []

class OptimizationProject(BaseModel):
    """Modèle pour un projet d'optimisation."""
    id: str
    user_id: str
    property_id: str
    name: str
    description: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    measures: List[OptimizationMeasure]
    total_cost: Optional[float] = None
    total_savings: Optional[float] = None

class SubsidyOptimizationRecommendation(BaseModel):
    """Modèle pour une recommandation de subvention pour un projet d'optimisation."""
    subsidy_id: str
    name: str
    provider: str
    description: str
    max_amount: Optional[float] = None
    percentage: Optional[float] = None
    relevance_score: float  # Score de pertinence de 0 à 1
    project_id: str  # ID du projet d'optimisation associé
    project_name: str  # Nom du projet d'optimisation associé
    measure_id: Optional[str] = None  # ID de la mesure associée (si applicable)
    measure_name: Optional[str] = None  # Nom de la mesure associée (si applicable)
    match_reason: str  # Raison de la correspondance
    potential_savings: Optional[float] = None  # Économies potentielles avec cette subvention

class OptimizationIntegrationService:
    """Service d'intégration avec le service d'optimisation."""
    
    def __init__(self, language: Language = Language.FR):
        """Initialise le service d'intégration."""
        self.language = language
    
    def get_optimization_project(self, project_id: str) -> Optional[OptimizationProject]:
        """
        Récupère un projet d'optimisation depuis le service d'optimisation.
        
        Args:
            project_id: ID du projet d'optimisation
            
        Returns:
            Projet d'optimisation ou None si non trouvé
        """
        try:
            response = requests.get(f"{OPTIMIZATION_SERVICE_URL}/projects/{project_id}")
            response.raise_for_status()
            return OptimizationProject(**response.json())
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération du projet d'optimisation: {e}")
            return None
    
    def get_optimization_measure(self, measure_id: str) -> Optional[OptimizationMeasure]:
        """
        Récupère une mesure d'optimisation spécifique depuis le service d'optimisation.
        
        Args:
            measure_id: ID de la mesure d'optimisation
            
        Returns:
            Mesure d'optimisation ou None si non trouvée
        """
        try:
            response = requests.get(f"{OPTIMIZATION_SERVICE_URL}/measures/{measure_id}")
            response.raise_for_status()
            return OptimizationMeasure(**response.json())
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération de la mesure d'optimisation: {e}")
            return None
    
    def _map_domain_to_subsidy_domain(self, optimization_domain: str) -> Optional[Domain]:
        """
        Mappe le domaine d'optimisation au domaine de subvention.
        
        Args:
            optimization_domain: Domaine de l'optimisation
            
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
        return domain_mapping.get(optimization_domain.lower())
    
    def _calculate_relevance_score(self, subsidy, measure: OptimizationMeasure) -> float:
        """
        Calcule un score de pertinence entre une subvention et une mesure d'optimisation.
        
        Args:
            subsidy: Subvention à évaluer
            measure: Mesure d'optimisation à comparer
            
        Returns:
            Score de pertinence entre 0 et 1
        """
        score = 0.0
        
        # Vérifier la correspondance de domaine (facteur important)
        subsidy_domains = [d.value for d in subsidy.domains]
        if measure.domain.lower() in subsidy_domains:
            score += 0.5
        
        # Vérifier les correspondances de mots-clés
        measure_tags = [tag.lower() for tag in measure.tags]
        subsidy_keywords = [keyword.get(self.language).lower() for keyword in subsidy.keywords]
        
        matching_keywords = set(measure_tags).intersection(set(subsidy_keywords))
        if matching_keywords:
            score += 0.3 * (len(matching_keywords) / max(len(measure_tags), 1))
        
        # Ajuster en fonction du coût estimé et du montant de la subvention
        if measure.estimated_cost and subsidy.max_amount:
            if subsidy.max_amount >= measure.estimated_cost * 0.2:  # Couvre au moins 20% du coût
                score += 0.2
        
        return min(score, 1.0)  # Plafonner à 1.0
    
    def _calculate_potential_savings(self, subsidy, measure: OptimizationMeasure) -> Optional[float]:
        """
        Calcule les économies potentielles en appliquant une subvention à une mesure d'optimisation.
        
        Args:
            subsidy: Subvention à appliquer
            measure: Mesure d'optimisation
            
        Returns:
            Économies potentielles en euros
        """
        if not measure.estimated_cost:
            return None
        
        if subsidy.max_amount:
            # Si la subvention a un montant maximum
            return min(subsidy.max_amount, measure.estimated_cost)
        elif subsidy.percentage:
            # Si la subvention est un pourcentage
            return measure.estimated_cost * (subsidy.percentage / 100)
        
        return None
    
    def _generate_match_reason(self, subsidy, measure: OptimizationMeasure, score: float) -> str:
        """
        Génère une explication de la correspondance entre une subvention et une mesure d'optimisation.
        
        Args:
            subsidy: Subvention à expliquer
            measure: Mesure d'optimisation associée
            score: Score de pertinence
            
        Returns:
            Explication textuelle de la correspondance
        """
        reasons = []
        
        # Vérifier la correspondance de domaine
        subsidy_domains = [d.value for d in subsidy.domains]
        if measure.domain.lower() in subsidy_domains:
            if self.language == Language.FR:
                reasons.append(f"Cette subvention concerne le domaine '{measure.domain}' de votre mesure d'optimisation")
            else:
                reasons.append(f"Deze subsidie heeft betrekking op het '{measure.domain}' domein van uw optimalisatiemaatregel")
        
        # Vérifier les correspondances de mots-clés
        measure_tags = [tag.lower() for tag in measure.tags]
        subsidy_keywords = [keyword.get(self.language).lower() for keyword in subsidy.keywords]
        
        matching_keywords = set(measure_tags).intersection(set(subsidy_keywords))
        if matching_keywords:
            keywords_str = ", ".join(matching_keywords)
            if self.language == Language.FR:
                reasons.append(f"Mots-clés correspondants: {keywords_str}")
            else:
                reasons.append(f"Overeenkomende trefwoorden: {keywords_str}")
        
        # Mentionner le montant de la subvention et les économies potentielles
        potential_savings = self._calculate_potential_savings(subsidy, measure)
        if potential_savings and measure.estimated_cost:
            percentage = (potential_savings / measure.estimated_cost) * 100
            if self.language == Language.FR:
                reasons.append(f"Peut couvrir environ {percentage:.1f}% du coût estimé ({potential_savings:.2f}€)")
            else:
                reasons.append(f"Kan ongeveer {percentage:.1f}% van de geschatte kosten dekken ({potential_savings:.2f}€)")
        
        # Assembler les raisons
        if self.language == Language.FR:
            return " | ".join(reasons) if reasons else "Subvention potentiellement pertinente pour cette mesure d'optimisation"
        else:
            return " | ".join(reasons) if reasons else "Potentieel relevante subsidie voor deze optimalisatiemaatregel"
    
    def find_subsidies_for_measure(self, measure_id: str) -> List[SubsidyOptimizationRecommendation]:
        """
        Trouve les subventions adaptées à une mesure d'optimisation spécifique.
        
        Args:
            measure_id: ID de la mesure d'optimisation
            
        Returns:
            Liste des subventions recommandées avec scores de pertinence
        """
        measure = self.get_optimization_measure(measure_id)
        if not measure:
            logger.error(f"Mesure d'optimisation {measure_id} non trouvée")
            return []
        
        # Convertir le domaine d'optimisation en domaine de subvention
        subsidy_domain = self._map_domain_to_subsidy_domain(measure.domain)
        
        # Rechercher les subventions dans ce domaine
        subsidies = []
        if subsidy_domain:
            subsidies = subsidy_data_manager.get_subsidies_by_domain(subsidy_domain)
        
        # Calculer les scores de pertinence et filtrer les subventions pertinentes
        subsidy_recommendations = []
        for subsidy in subsidies:
            score = self._calculate_relevance_score(subsidy, measure)
            if score >= 0.3:  # Seuil minimum de pertinence
                match_reason = self._generate_match_reason(subsidy, measure, score)
                potential_savings = self._calculate_potential_savings(subsidy, measure)
                
                subsidy_dict = subsidy_data_manager.get_subsidy_details_dict(subsidy.id, self.language)
                subsidy_recommendations.append(
                    SubsidyOptimizationRecommendation(
                        subsidy_id=subsidy.id,
                        name=subsidy_dict["name"],
                        provider=subsidy_dict["provider"],
                        description=subsidy_dict["description"],
                        max_amount=subsidy_dict["max_amount"],
                        percentage=subsidy_dict["percentage"],
                        relevance_score=score,
                        project_id="",  # Sera rempli lors de l'appel depuis un projet
                        project_name="",  # Sera rempli lors de l'appel depuis un projet
                        measure_id=measure.id,
                        measure_name=measure.name,
                        match_reason=match_reason,
                        potential_savings=potential_savings
                    )
                )
        
        # Trier par score de pertinence décroissant
        subsidy_recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        return subsidy_recommendations
    
    def find_subsidies_for_project(self, project_id: str) -> Dict[str, List[SubsidyOptimizationRecommendation]]:
        """
        Trouve les subventions adaptées à un projet d'optimisation.
        
        Args:
            project_id: ID du projet d'optimisation
            
        Returns:
            Dictionnaire avec les IDs de mesure comme clés et les listes de subventions comme valeurs
        """
        project = self.get_optimization_project(project_id)
        if not project:
            logger.error(f"Projet d'optimisation {project_id} non trouvé")
            return {}
        
        result = {}
        for measure in project.measures:
            subsidies = self.find_subsidies_for_measure(measure.id)
            
            # Mettre à jour les informations du projet
            for subsidy in subsidies:
                subsidy.project_id = project.id
                subsidy.project_name = project.name
            
            result[measure.id] = subsidies
        
        return result

# Instance singleton du service d'intégration
optimization_integration_service = OptimizationIntegrationService()
