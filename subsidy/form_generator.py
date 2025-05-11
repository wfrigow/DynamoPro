"""
Module de génération de formulaires de demande de subvention
--------------------------------------------------------
Ce module fournit des outils pour générer automatiquement des formulaires
de demande pour différentes subventions, basés sur les données utilisateur
et les recommandations.
"""

import os
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from pydantic import UUID4
from subsidy_db import Subsidy, SubsidyKeyword, RequiredDocument, SubsidyDocumentType


class FormGenerator:
    """Générateur de formulaires de demande de subvention"""
    
    def __init__(self):
        """Initialisation du générateur de formulaires"""
        self.templates_dir = os.path.join(os.path.dirname(__file__), "templates")
        os.makedirs(self.templates_dir, exist_ok=True)
    
    def generate_form_data(
        self,
        subsidy: Subsidy,
        user_profile: Dict[str, Any],
        property_data: Optional[Dict[str, Any]] = None,
        recommendation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Génère les données de formulaire pour une demande de subvention
        
        Args:
            subsidy: Données de la subvention
            user_profile: Profil de l'utilisateur
            property_data: Données de la propriété concernée
            recommendation: Recommandation liée à la demande
        
        Returns:
            Dictionnaire contenant les données du formulaire
        """
        # Données par défaut pour le formulaire
        property_data = property_data or {}
        
        # Déterminer la date d'achèvement estimée (3 à 6 mois dans le futur)
        completion_date = datetime.now() + timedelta(days=90 + uuid.uuid4().int % 90)
        
        # Assembler les données du formulaire
        form_data = {
            "applicant": {
                "name": user_profile.get("name", ""),
                "email": user_profile.get("email", ""),
                "phone": user_profile.get("phone", ""),
                "address": user_profile.get("address", ""),
                "user_type": user_profile.get("user_type", "individual")
            },
            "property": {
                "address": property_data.get("address", user_profile.get("address", "")),
                "type": property_data.get("type", "house"),
                "year_built": property_data.get("built_year", "Non spécifié")
            },
            "subsidy": {
                "id": subsidy.id,
                "name": subsidy.name,
                "provider_id": subsidy.provider_id
            },
            "project": {
                "description": recommendation["title"] if recommendation else f"Demande de {subsidy.name}",
                "estimated_cost": (recommendation["estimated_cost_min"] + recommendation["estimated_cost_max"]) / 2 if recommendation else None,
                "estimated_completion_date": completion_date.strftime("%Y-%m-%d")
            },
            "bank_details": {
                "account_holder": user_profile.get("name", ""),
                "iban": user_profile.get("iban", "")
            },
            "declaration": {
                "date_submitted": datetime.now().strftime("%Y-%m-%d"),
                "consent_rgpd": True,
                "consent_terms": True,
                "declaration_accuracy": True
            }
        }
        
        # Ajouter des champs spécifiques en fonction du type de subvention
        if subsidy.keywords:
            for keyword in subsidy.keywords:
                if keyword == SubsidyKeyword.INSULATION:
                    form_data["technical_details"] = {
                        "insulation_material": "",
                        "surface_area_m2": 0,
                        "r_value": 0,
                        "installer_certification": ""
                    }
                elif keyword == SubsidyKeyword.HEAT_PUMP:
                    form_data["technical_details"] = {
                        "heat_pump_type": "",
                        "cop_value": 0,
                        "manufacturer": "",
                        "model": "",
                        "installer_certification": ""
                    }
                elif keyword == SubsidyKeyword.SOLAR:
                    form_data["technical_details"] = {
                        "panel_count": 0,
                        "peak_power_kwp": 0,
                        "panel_efficiency": 0,
                        "installer_certification": "",
                        "orientation": ""
                    }
                elif keyword == SubsidyKeyword.RAINWATER:
                    form_data["technical_details"] = {
                        "tank_capacity_liters": 0,
                        "connection_points": "",
                        "filtering_system": ""
                    }
        
        return form_data
    
    def get_required_documents(self, subsidy: Subsidy) -> List[Dict[str, Any]]:
        """
        Obtient la liste des documents requis pour une subvention
        
        Args:
            subsidy: Données de la subvention
            
        Returns:
            Liste des documents requis avec leur statut
        """
        # Documents de base toujours requis
        base_documents = [
            {
                "name": "Preuve d'identité",
                "type": SubsidyDocumentType.IDENTITY.value,
                "description": "Copie de la carte d'identité du demandeur",
                "is_uploaded": False,
                "is_validated": False
            },
            {
                "name": "Preuve de propriété",
                "type": SubsidyDocumentType.OWNERSHIP.value,
                "description": "Document attestant que vous êtes propriétaire du bien concerné",
                "is_uploaded": False,
                "is_validated": False
            }
        ]
        
        # Documents spécifiques à la subvention
        specific_documents = []
        if subsidy.required_documents:
            for doc in subsidy.required_documents:
                specific_documents.append({
                    "name": doc.type.value,
                    "type": doc.type.value,
                    "description": doc.description,
                    "is_uploaded": False,
                    "is_validated": False
                })
        
        return base_documents + specific_documents
    
    def generate_application_checklist(self, subsidy: Subsidy) -> List[Dict[str, Any]]:
        """
        Génère une checklist pour suivre l'avancement de la demande
        
        Args:
            subsidy: Données de la subvention
            
        Returns:
            Checklist des étapes de la demande
        """
        checklist = [
            {
                "step": 1,
                "name": "Préparation du dossier",
                "description": "Rassembler tous les documents nécessaires",
                "is_completed": False,
                "deadline": (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
            },
            {
                "step": 2,
                "name": "Soumission de la demande",
                "description": f"Soumettre le formulaire de demande à {subsidy.provider_id}",
                "is_completed": False,
                "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            },
            {
                "step": 3,
                "name": "Suivi de la demande",
                "description": "Vérifier régulièrement l'état de la demande",
                "is_completed": False,
                "deadline": None
            },
            {
                "step": 4,
                "name": "Réception de la décision",
                "description": "Attendre la décision concernant votre demande",
                "is_completed": False,
                "deadline": (datetime.now() + timedelta(days=subsidy.typical_processing_time_days or 60)).strftime("%Y-%m-%d")
            }
        ]
        
        return checklist
    
    def save_application_template(
        self, 
        subsidy_id: str, 
        form_data: Dict[str, Any]
    ) -> str:
        """
        Sauvegarde un modèle de formulaire pour une subvention
        
        Args:
            subsidy_id: ID de la subvention
            form_data: Données du formulaire
            
        Returns:
            Chemin du fichier de template sauvegardé
        """
        template_path = os.path.join(self.templates_dir, f"{subsidy_id}_template.json")
        
        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(form_data, f, ensure_ascii=False, indent=2)
        
        return template_path
    
    def get_application_template(self, subsidy_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un modèle de formulaire pour une subvention
        
        Args:
            subsidy_id: ID de la subvention
            
        Returns:
            Données du formulaire ou None si non trouvé
        """
        template_path = os.path.join(self.templates_dir, f"{subsidy_id}_template.json")
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None


# Instance globale du générateur de formulaires
form_generator = FormGenerator()

def get_form_generator() -> FormGenerator:
    """
    Récupère l'instance globale du générateur de formulaires
    
    Returns:
        Instance du générateur de formulaires
    """
    return form_generator
