"""
Routes API pour l'intégration de l'Agent de Subventions avec d'autres services.
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, Query, Path, HTTPException
from pydantic import BaseModel

from ..integrations.recommendation_integration import (
    recommendation_integration_service,
    SubsidyRecommendation
)
from ..integrations.optimization_integration import (
    optimization_integration_service,
    SubsidyOptimizationRecommendation
)
from ..integrations.green_passport_integration import (
    green_passport_integration_service,
    SubsidyPropertyRecommendation
)
from ..data.subsidies_extended import Language

router = APIRouter(prefix="/api/subsidy-integration", tags=["subsidy-integration"])

class SubsidyRecommendationResponse(BaseModel):
    """Modèle de réponse pour les recommandations de subventions."""
    recommendation_id: str
    subsidies: List[SubsidyRecommendation]

class RecommendationSetSubsidiesResponse(BaseModel):
    """Modèle de réponse pour les subventions d'un ensemble de recommandations."""
    recommendation_set_id: str
    recommendations: List[SubsidyRecommendationResponse]

class OptimizationMeasureSubsidiesResponse(BaseModel):
    """Modèle de réponse pour les subventions d'une mesure d'optimisation."""
    measure_id: str
    subsidies: List[SubsidyOptimizationRecommendation]

class OptimizationProjectSubsidiesResponse(BaseModel):
    """Modèle de réponse pour les subventions d'un projet d'optimisation."""
    project_id: str
    measures: List[OptimizationMeasureSubsidiesResponse]

class PropertySubsidiesResponse(BaseModel):
    """Modèle de réponse pour les subventions d'une propriété."""
    property_id: str
    property_address: str
    subsidies: List[SubsidyPropertyRecommendation]

@router.get("/recommendations/{recommendation_id}/subsidies", response_model=List[SubsidyRecommendation])
async def get_subsidies_for_recommendation(
    recommendation_id: str = Path(..., description="ID de la recommandation"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les subventions adaptées à une recommandation spécifique.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    recommendation_integration_service.language = lang
    
    # Récupérer les subventions
    subsidies = recommendation_integration_service.find_subsidies_for_recommendation(recommendation_id)
    
    if not subsidies:
        return []
    
    return subsidies

@router.get("/recommendation-sets/{recommendation_set_id}/subsidies", response_model=RecommendationSetSubsidiesResponse)
async def get_subsidies_for_recommendation_set(
    recommendation_set_id: str = Path(..., description="ID de l'ensemble de recommandations"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les subventions adaptées à un ensemble de recommandations.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    recommendation_integration_service.language = lang
    
    # Récupérer les subventions
    subsidies_by_recommendation = recommendation_integration_service.find_subsidies_for_recommendation_set(recommendation_set_id)
    
    if not subsidies_by_recommendation:
        raise HTTPException(status_code=404, detail=f"Ensemble de recommandations {recommendation_set_id} non trouvé ou aucune subvention applicable")
    
    # Formater la réponse
    recommendations = []
    for recommendation_id, subsidies in subsidies_by_recommendation.items():
        recommendations.append(
            SubsidyRecommendationResponse(
                recommendation_id=recommendation_id,
                subsidies=subsidies
            )
        )
    
    return RecommendationSetSubsidiesResponse(
        recommendation_set_id=recommendation_set_id,
        recommendations=recommendations
    )

@router.get("/recommendations/{recommendation_id}/best-subsidies", response_model=List[SubsidyRecommendation])
async def get_best_subsidies_for_recommendation(
    recommendation_id: str = Path(..., description="ID de la recommandation"),
    limit: int = Query(3, description="Nombre maximum de subventions à retourner"),
    min_score: float = Query(0.5, description="Score minimum de pertinence (0-1)"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les meilleures subventions adaptées à une recommandation spécifique.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    recommendation_integration_service.language = lang
    
    # Récupérer les subventions
    all_subsidies = recommendation_integration_service.find_subsidies_for_recommendation(recommendation_id)
    
    # Filtrer par score minimum et limiter le nombre
    filtered_subsidies = [s for s in all_subsidies if s.relevance_score >= min_score]
    limited_subsidies = filtered_subsidies[:limit]
    
    return limited_subsidies

# Routes pour l'intégration avec le service d'optimisation
@router.get("/optimization/measures/{measure_id}/subsidies", response_model=List[SubsidyOptimizationRecommendation])
async def get_subsidies_for_optimization_measure(
    measure_id: str = Path(..., description="ID de la mesure d'optimisation"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les subventions adaptées à une mesure d'optimisation spécifique.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    optimization_integration_service.language = lang
    
    # Récupérer les subventions
    subsidies = optimization_integration_service.find_subsidies_for_measure(measure_id)
    
    if not subsidies:
        return []
    
    return subsidies

@router.get("/optimization/projects/{project_id}/subsidies", response_model=OptimizationProjectSubsidiesResponse)
async def get_subsidies_for_optimization_project(
    project_id: str = Path(..., description="ID du projet d'optimisation"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les subventions adaptées à un projet d'optimisation.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    optimization_integration_service.language = lang
    
    # Récupérer les subventions
    subsidies_by_measure = optimization_integration_service.find_subsidies_for_project(project_id)
    
    if not subsidies_by_measure:
        raise HTTPException(status_code=404, detail=f"Projet d'optimisation {project_id} non trouvé ou aucune subvention applicable")
    
    # Formater la réponse
    measures = []
    for measure_id, subsidies in subsidies_by_measure.items():
        measures.append(
            OptimizationMeasureSubsidiesResponse(
                measure_id=measure_id,
                subsidies=subsidies
            )
        )
    
    return OptimizationProjectSubsidiesResponse(
        project_id=project_id,
        measures=measures
    )

@router.get("/optimization/measures/{measure_id}/best-subsidies", response_model=List[SubsidyOptimizationRecommendation])
async def get_best_subsidies_for_optimization_measure(
    measure_id: str = Path(..., description="ID de la mesure d'optimisation"),
    limit: int = Query(3, description="Nombre maximum de subventions à retourner"),
    min_score: float = Query(0.5, description="Score minimum de pertinence (0-1)"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les meilleures subventions adaptées à une mesure d'optimisation spécifique.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    optimization_integration_service.language = lang
    
    # Récupérer les subventions
    all_subsidies = optimization_integration_service.find_subsidies_for_measure(measure_id)
    
    # Filtrer par score minimum et limiter le nombre
    filtered_subsidies = [s for s in all_subsidies if s.relevance_score >= min_score]
    limited_subsidies = filtered_subsidies[:limit]
    
    return limited_subsidies
