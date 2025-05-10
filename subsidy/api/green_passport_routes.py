"""
Routes API pour l'intégration de l'Agent de Subventions avec le service de Passeport Vert.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException
from pydantic import BaseModel

from ..integrations.green_passport_integration import (
    green_passport_integration_service,
    SubsidyPropertyRecommendation
)
from ..data.subsidies_extended import Language

router = APIRouter(prefix="/api/subsidy-green-passport", tags=["subsidy-green-passport"])

class PropertySubsidiesResponse(BaseModel):
    """Modèle de réponse pour les subventions d'une propriété."""
    property_id: str
    property_address: str
    subsidies: List[SubsidyPropertyRecommendation]

@router.get("/properties/{property_id}/subsidies", response_model=PropertySubsidiesResponse)
async def get_subsidies_for_property(
    property_id: str = Path(..., description="ID de la propriété"),
    user_id: Optional[str] = Query(None, description="ID de l'utilisateur (optionnel)"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les subventions adaptées à une propriété spécifique.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    green_passport_integration_service.language = lang
    
    # Récupérer les subventions
    subsidies = green_passport_integration_service.find_subsidies_for_property(property_id, user_id)
    
    if not subsidies:
        # Si aucune subvention n'est trouvée, retourner une réponse vide plutôt qu'une erreur
        property_info = green_passport_integration_service.get_property_info(property_id)
        if not property_info:
            raise HTTPException(status_code=404, detail=f"Propriété {property_id} non trouvée")
        
        return PropertySubsidiesResponse(
            property_id=property_id,
            property_address=property_info.address,
            subsidies=[]
        )
    
    # Récupérer l'adresse de la propriété depuis la première subvention
    property_address = subsidies[0].property_address
    
    return PropertySubsidiesResponse(
        property_id=property_id,
        property_address=property_address,
        subsidies=subsidies
    )

@router.get("/properties/{property_id}/best-subsidies", response_model=List[SubsidyPropertyRecommendation])
async def get_best_subsidies_for_property(
    property_id: str = Path(..., description="ID de la propriété"),
    user_id: Optional[str] = Query(None, description="ID de l'utilisateur (optionnel)"),
    limit: int = Query(5, description="Nombre maximum de subventions à retourner"),
    min_score: float = Query(0.4, description="Score minimum de pertinence (0-1)"),
    language: str = Query("fr", description="Langue (fr ou nl)")
):
    """
    Récupère les meilleures subventions adaptées à une propriété spécifique.
    """
    # Définir la langue
    lang = Language.FR if language.lower() == "fr" else Language.NL
    green_passport_integration_service.language = lang
    
    # Récupérer les subventions
    all_subsidies = green_passport_integration_service.find_subsidies_for_property(property_id, user_id)
    
    # Filtrer par score minimum et limiter le nombre
    filtered_subsidies = [s for s in all_subsidies if s.relevance_score >= min_score]
    limited_subsidies = filtered_subsidies[:limit]
    
    return limited_subsidies
