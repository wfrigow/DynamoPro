"""
Routes API pour accéder aux subventions enrichies.
Fournit des endpoints pour rechercher, filtrer et récupérer des subventions.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, Path, HTTPException
from pydantic import BaseModel, Field
from enum import Enum

from ..data.subsidies_extended import Region, Domain, UserType, Language
from ..data.subsidy_data_manager import subsidy_data_manager

router = APIRouter(tags=["subsidies"])

# Modèles Pydantic pour l'API
class LanguageEnum(str, Enum):
    FR = "fr"
    NL = "nl"

class RegionEnum(str, Enum):
    WALLONIE = "wallonie"
    BRUXELLES = "bruxelles"
    FLANDRE = "flandre"
    FEDERAL = "federal"

class DomainEnum(str, Enum):
    ENERGY = "energy"
    WATER = "water"
    WASTE = "waste"
    BIODIVERSITY = "biodiversity"
    RENOVATION = "renovation"
    MOBILITY = "mobility"
    CIRCULAR_ECONOMY = "circular_economy"

class UserTypeEnum(str, Enum):
    INDIVIDUAL = "individual"
    SELF_EMPLOYED = "self_employed"
    SMALL_BUSINESS = "small_business"
    MEDIUM_BUSINESS = "medium_business"
    LARGE_BUSINESS = "large_business"
    PUBLIC_ENTITY = "public_entity"
    NON_PROFIT = "non_profit"

class DocumentFormatModel(BaseModel):
    id: str
    name: str
    description: str
    type: str
    required: bool
    format: List[str]

class SubsidyListItemModel(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    regions: List[str]
    domains: List[str]
    max_amount: Optional[float] = None
    percentage: Optional[float] = None
    keywords: List[str]
    status: str

class SubsidyDetailModel(SubsidyListItemModel):
    conditions: Optional[str] = None
    eligibility: List[str]
    user_types: List[str]
    required_documents: List[DocumentFormatModel]
    application_process: Optional[str] = None
    documentation_url: Optional[str] = None
    min_year_built: Optional[int] = None
    max_year_built: Optional[int] = None
    additional_info: Optional[str] = None

class SubsidySearchResponseModel(BaseModel):
    count: int
    results: List[SubsidyListItemModel]

@router.get("/", response_model=SubsidySearchResponseModel)
async def search_subsidies(
    query: Optional[str] = Query(None, description="Texte à rechercher dans le nom, la description ou les mots-clés"),
    regions: Optional[List[RegionEnum]] = Query(None, description="Régions à filtrer"),
    domains: Optional[List[DomainEnum]] = Query(None, description="Domaines à filtrer"),
    user_types: Optional[List[UserTypeEnum]] = Query(None, description="Types d'utilisateurs à filtrer"),
    min_amount: Optional[float] = Query(None, description="Montant minimum de la subvention"),
    max_amount: Optional[float] = Query(None, description="Montant maximum de la subvention"),
    year_built: Optional[int] = Query(None, description="Année de construction du bâtiment"),
    language: LanguageEnum = Query(LanguageEnum.FR, description="Langue des résultats")
):
    """
    Recherche des subventions selon plusieurs critères.
    """
    # Convertir les enums en objets internes
    regions_internal = [Region(r.value) for r in regions] if regions else None
    domains_internal = [Domain(d.value) for d in domains] if domains else None
    user_types_internal = [UserType(ut.value) for ut in user_types] if user_types else None
    language_internal = Language(language.value)
    
    # Effectuer la recherche
    results = subsidy_data_manager.search_subsidies(
        query=query,
        regions=regions_internal,
        domains=domains_internal,
        user_types=user_types_internal,
        min_amount=min_amount,
        max_amount=max_amount,
        year_built=year_built,
        language=language_internal
    )
    
    # Convertir les résultats en format API
    subsidies_list = subsidy_data_manager.get_subsidies_list_dict(results, language_internal)
    
    return {
        "count": len(subsidies_list),
        "results": subsidies_list
    }

@router.get("/{subsidy_id}", response_model=SubsidyDetailModel)
async def get_subsidy_details(
    subsidy_id: str = Path(..., description="ID de la subvention"),
    language: LanguageEnum = Query(LanguageEnum.FR, description="Langue des résultats")
):
    """
    Récupère les détails d'une subvention spécifique.
    """
    language_internal = Language(language.value)
    subsidy_details = subsidy_data_manager.get_subsidy_details_dict(subsidy_id, language_internal)
    
    if not subsidy_details:
        raise HTTPException(status_code=404, detail=f"Subvention avec ID {subsidy_id} non trouvée")
    
    return subsidy_details

@router.get("/regions/{region}", response_model=SubsidySearchResponseModel)
async def get_subsidies_by_region(
    region: RegionEnum = Path(..., description="Région à filtrer"),
    language: LanguageEnum = Query(LanguageEnum.FR, description="Langue des résultats")
):
    """
    Récupère les subventions disponibles dans une région spécifique.
    """
    region_internal = Region(region.value)
    language_internal = Language(language.value)
    
    results = subsidy_data_manager.get_subsidies_by_region(region_internal)
    subsidies_list = subsidy_data_manager.get_subsidies_list_dict(results, language_internal)
    
    return {
        "count": len(subsidies_list),
        "results": subsidies_list
    }

@router.get("/domains/{domain}", response_model=SubsidySearchResponseModel)
async def get_subsidies_by_domain(
    domain: DomainEnum = Path(..., description="Domaine à filtrer"),
    language: LanguageEnum = Query(LanguageEnum.FR, description="Langue des résultats")
):
    """
    Récupère les subventions disponibles dans un domaine spécifique.
    """
    domain_internal = Domain(domain.value)
    language_internal = Language(language.value)
    
    results = subsidy_data_manager.get_subsidies_by_domain(domain_internal)
    subsidies_list = subsidy_data_manager.get_subsidies_list_dict(results, language_internal)
    
    return {
        "count": len(subsidies_list),
        "results": subsidies_list
    }

@router.get("/user-types/{user_type}", response_model=SubsidySearchResponseModel)
async def get_subsidies_by_user_type(
    user_type: UserTypeEnum = Path(..., description="Type d'utilisateur à filtrer"),
    language: LanguageEnum = Query(LanguageEnum.FR, description="Langue des résultats")
):
    """
    Récupère les subventions disponibles pour un type d'utilisateur spécifique.
    """
    user_type_internal = UserType(user_type.value)
    language_internal = Language(language.value)
    
    results = subsidy_data_manager.get_subsidies_by_user_type(user_type_internal)
    subsidies_list = subsidy_data_manager.get_subsidies_list_dict(results, language_internal)
    
    return {
        "count": len(subsidies_list),
        "results": subsidies_list
    }

@router.get("/keywords/{keyword}", response_model=SubsidySearchResponseModel)
async def get_subsidies_by_keyword(
    keyword: str = Path(..., description="Mot-clé à rechercher"),
    language: LanguageEnum = Query(LanguageEnum.FR, description="Langue des résultats")
):
    """
    Récupère les subventions correspondant à un mot-clé spécifique.
    """
    language_internal = Language(language.value)
    
    results = subsidy_data_manager.get_subsidies_by_keyword(keyword, language_internal)
    subsidies_list = subsidy_data_manager.get_subsidies_list_dict(results, language_internal)
    
    return {
        "count": len(subsidies_list),
        "results": subsidies_list
    }
