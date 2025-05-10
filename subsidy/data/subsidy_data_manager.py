"""
Module de gestion des données de subventions enrichies.
Fournit des fonctions pour charger, filtrer et accéder aux données de subventions.
"""

from typing import List, Dict, Any, Optional, Union, Set
from .subsidies_extended import (
    EnrichedSubsidy, 
    TranslatedText, 
    Region, 
    Domain, 
    UserType, 
    Language,
    ENRICHED_SUBSIDIES
)
from .subsidies_extended_part2 import MORE_ENRICHED_SUBSIDIES

class SubsidyDataManager:
    """Gestionnaire des données de subventions enrichies."""
    
    def __init__(self):
        """Initialise le gestionnaire avec les données de subventions."""
        self.subsidies = ENRICHED_SUBSIDIES + MORE_ENRICHED_SUBSIDIES
        self._index_by_id = {subsidy.id: subsidy for subsidy in self.subsidies}
        self._index_by_region = self._build_region_index()
        self._index_by_domain = self._build_domain_index()
        self._index_by_user_type = self._build_user_type_index()
        self._index_by_keyword = self._build_keyword_index()
    
    def _build_region_index(self) -> Dict[Region, List[EnrichedSubsidy]]:
        """Construit un index des subventions par région."""
        index = {region: [] for region in Region}
        for subsidy in self.subsidies:
            for region in subsidy.regions:
                index[region].append(subsidy)
        return index
    
    def _build_domain_index(self) -> Dict[Domain, List[EnrichedSubsidy]]:
        """Construit un index des subventions par domaine."""
        index = {domain: [] for domain in Domain}
        for subsidy in self.subsidies:
            for domain in subsidy.domains:
                index[domain].append(subsidy)
        return index
    
    def _build_user_type_index(self) -> Dict[UserType, List[EnrichedSubsidy]]:
        """Construit un index des subventions par type d'utilisateur."""
        index = {user_type: [] for user_type in UserType}
        for subsidy in self.subsidies:
            for user_type in subsidy.user_types:
                index[user_type].append(subsidy)
        return index
    
    def _build_keyword_index(self) -> Dict[str, List[EnrichedSubsidy]]:
        """Construit un index des subventions par mot-clé."""
        index = {}
        for subsidy in self.subsidies:
            for keyword in subsidy.keywords:
                # Indexer par mot-clé en français et en néerlandais
                for lang in [Language.FR, Language.NL]:
                    key = keyword.get(lang).lower()
                    if key not in index:
                        index[key] = []
                    index[key].append(subsidy)
        return index
    
    def get_all_subsidies(self) -> List[EnrichedSubsidy]:
        """Récupère toutes les subventions."""
        return self.subsidies
    
    def get_subsidy_by_id(self, subsidy_id: str) -> Optional[EnrichedSubsidy]:
        """Récupère une subvention par son ID."""
        return self._index_by_id.get(subsidy_id)
    
    def get_subsidies_by_region(self, region: Region) -> List[EnrichedSubsidy]:
        """Récupère les subventions disponibles dans une région."""
        return self._index_by_region.get(region, [])
    
    def get_subsidies_by_domain(self, domain: Domain) -> List[EnrichedSubsidy]:
        """Récupère les subventions dans un domaine spécifique."""
        return self._index_by_domain.get(domain, [])
    
    def get_subsidies_by_user_type(self, user_type: UserType) -> List[EnrichedSubsidy]:
        """Récupère les subventions disponibles pour un type d'utilisateur."""
        return self._index_by_user_type.get(user_type, [])
    
    def get_subsidies_by_keyword(self, keyword: str, language: Language = Language.FR) -> List[EnrichedSubsidy]:
        """Récupère les subventions correspondant à un mot-clé."""
        return self._index_by_keyword.get(keyword.lower(), [])
    
    def search_subsidies(self, 
                         query: str = None,
                         regions: List[Region] = None,
                         domains: List[Domain] = None,
                         user_types: List[UserType] = None,
                         min_amount: float = None,
                         max_amount: float = None,
                         year_built: int = None,
                         language: Language = Language.FR) -> List[EnrichedSubsidy]:
        """
        Recherche des subventions selon plusieurs critères.
        
        Args:
            query: Texte à rechercher dans le nom, la description ou les mots-clés
            regions: Liste des régions à filtrer
            domains: Liste des domaines à filtrer
            user_types: Liste des types d'utilisateurs à filtrer
            min_amount: Montant minimum de la subvention
            max_amount: Montant maximum de la subvention
            year_built: Année de construction du bâtiment
            language: Langue pour la recherche textuelle
            
        Returns:
            Liste des subventions correspondant aux critères
        """
        results = set(self.subsidies)
        
        # Filtrer par région
        if regions:
            region_results = set()
            for region in regions:
                region_results.update(self._index_by_region.get(region, []))
            results = results.intersection(region_results)
        
        # Filtrer par domaine
        if domains:
            domain_results = set()
            for domain in domains:
                domain_results.update(self._index_by_domain.get(domain, []))
            results = results.intersection(domain_results)
        
        # Filtrer par type d'utilisateur
        if user_types:
            user_type_results = set()
            for user_type in user_types:
                user_type_results.update(self._index_by_user_type.get(user_type, []))
            results = results.intersection(user_type_results)
        
        # Filtrer par montant
        if min_amount is not None or max_amount is not None:
            amount_results = set()
            for subsidy in self.subsidies:
                if subsidy.max_amount is not None:
                    if min_amount is not None and subsidy.max_amount < min_amount:
                        continue
                    if max_amount is not None and subsidy.max_amount > max_amount:
                        continue
                    amount_results.add(subsidy)
            results = results.intersection(amount_results) if amount_results else results
        
        # Filtrer par année de construction
        if year_built is not None:
            year_results = set()
            for subsidy in self.subsidies:
                if (subsidy.min_year_built is None or year_built >= subsidy.min_year_built) and \
                   (subsidy.max_year_built is None or year_built <= subsidy.max_year_built):
                    year_results.add(subsidy)
            results = results.intersection(year_results)
        
        # Filtrer par texte de recherche
        if query:
            query = query.lower()
            text_results = set()
            
            # Rechercher dans les mots-clés
            for keyword, subsidies in self._index_by_keyword.items():
                if language == Language.FR and query in keyword.lower():
                    text_results.update(subsidies)
            
            # Rechercher dans le nom et la description
            for subsidy in self.subsidies:
                if query in subsidy.name.get(language).lower() or \
                   query in subsidy.description.get(language).lower():
                    text_results.add(subsidy)
            
            results = results.intersection(text_results) if text_results else results
        
        return list(results)
    
    def get_subsidy_details_dict(self, subsidy_id: str, language: Language = Language.FR) -> Dict[str, Any]:
        """
        Récupère les détails d'une subvention dans un format adapté à l'API.
        
        Args:
            subsidy_id: ID de la subvention
            language: Langue des textes
            
        Returns:
            Dictionnaire contenant les détails de la subvention
        """
        subsidy = self.get_subsidy_by_id(subsidy_id)
        if not subsidy:
            return None
        
        return {
            "id": subsidy.id,
            "name": subsidy.name.get(language),
            "provider": subsidy.provider.get(language),
            "description": subsidy.description.get(language),
            "regions": [r.value for r in subsidy.regions],
            "domains": [d.value for d in subsidy.domains],
            "max_amount": subsidy.max_amount,
            "percentage": subsidy.percentage,
            "conditions": subsidy.conditions.get(language) if subsidy.conditions else None,
            "eligibility": [e.get(language) for e in subsidy.eligibility],
            "user_types": [ut.value for ut in subsidy.user_types],
            "required_documents": [
                {
                    "id": doc.id,
                    "name": doc.name.get(language),
                    "description": doc.description.get(language),
                    "type": doc.type.value,
                    "required": doc.required,
                    "format": doc.format
                }
                for doc in subsidy.required_documents
            ],
            "application_process": subsidy.application_process.get(language) if subsidy.application_process else None,
            "documentation_url": subsidy.documentation_url.get(language, None),
            "status": subsidy.status.value,
            "keywords": [k.get(language) for k in subsidy.keywords],
            "min_year_built": subsidy.min_year_built,
            "max_year_built": subsidy.max_year_built,
            "additional_info": subsidy.additional_info.get(language) if subsidy.additional_info else None
        }
    
    def get_subsidies_list_dict(self, subsidies: List[EnrichedSubsidy], language: Language = Language.FR) -> List[Dict[str, Any]]:
        """
        Convertit une liste de subventions en format adapté à l'API.
        Version simplifiée pour les listes.
        
        Args:
            subsidies: Liste des subventions
            language: Langue des textes
            
        Returns:
            Liste de dictionnaires contenant les détails simplifiés des subventions
        """
        return [
            {
                "id": subsidy.id,
                "name": subsidy.name.get(language),
                "provider": subsidy.provider.get(language),
                "description": subsidy.description.get(language),
                "regions": [r.value for r in subsidy.regions],
                "domains": [d.value for d in subsidy.domains],
                "max_amount": subsidy.max_amount,
                "percentage": subsidy.percentage,
                "keywords": [k.get(language) for k in subsidy.keywords],
                "status": subsidy.status.value
            }
            for subsidy in subsidies
        ]


# Instance singleton du gestionnaire de données
subsidy_data_manager = SubsidyDataManager()
