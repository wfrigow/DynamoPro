"""
Module de gestion des données d'applications de subventions.
Fournit des fonctions pour gérer les applications de subventions.
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

from backend.subsidy.models.application_models import (
    ApplicationResponse, ApplicationDraftResponse,
    Applicant, Property, Project, BankDetails
)
from backend.subsidy.data.subsidy_data_manager import subsidy_data_manager


# Base de données simulée pour les applications
applications_db: Dict[str, Dict[str, Any]] = {}
drafts_db: Dict[str, Dict[str, Any]] = {}


def create_application(
    subsidy_id: str,
    applicant: Applicant,
    property_data: Property,
    project: Project,
    bank_details: Optional[BankDetails] = None,
    user_id: str = None
) -> ApplicationResponse:
    """
    Crée une nouvelle application de subvention.
    
    Args:
        subsidy_id: ID de la subvention
        applicant: Informations sur le demandeur
        property_data: Informations sur la propriété
        project: Informations sur le projet
        bank_details: Informations bancaires
        user_id: ID de l'utilisateur
        
    Returns:
        Les détails de l'application créée
    """
    # Vérifier que la subvention existe
    subsidy = subsidy_data_manager.get_subsidy_by_id(subsidy_id)
    if not subsidy:
        return None
    
    # Générer un ID unique pour l'application
    application_id = f"APP-{uuid.uuid4().hex[:8].upper()}"
    
    # Générer un numéro de référence
    reference_number = f"PRE-{datetime.now().year}-{uuid.uuid4().hex[:5].upper()}"
    
    # Créer l'application
    now = datetime.now()
    application_data = {
        "id": application_id,
        "subsidy_id": subsidy_id,
        "user_id": user_id,
        "status": "submitted",
        "status_label": "Soumise",
        "submission_date": now,
        "last_updated": now,
        "reference_number": reference_number,
        "applicant": applicant.dict(),
        "property": property_data.dict(),
        "project": project.dict(),
        "bank_details": bank_details.dict() if bank_details else None,
        "subsidy": {
            "id": subsidy.id,
            "name": subsidy.name.get("fr"),
            "provider": subsidy.provider.get("fr"),
            "maxAmount": subsidy.max_amount,
            "percentage": subsidy.percentage,
            "calculatedAmount": None
        },
        "documents": [],
        "notes": [],
        "history": [
            {
                "id": f"hist-{uuid.uuid4().hex[:8]}",
                "date": now,
                "status": "submitted",
                "description": "Demande soumise"
            }
        ],
        "next_steps": [
            "Vérification des documents",
            "Évaluation technique",
            "Décision finale"
        ]
    }
    
    # Stocker l'application dans la base de données simulée
    applications_db[application_id] = application_data
    
    return ApplicationResponse(**application_data)


def create_draft(
    subsidy_id: str,
    applicant: Optional[Applicant] = None,
    property_data: Optional[Property] = None,
    project: Optional[Project] = None,
    bank_details: Optional[BankDetails] = None,
    user_id: str = None
) -> ApplicationDraftResponse:
    """
    Crée un nouveau brouillon d'application de subvention.
    
    Args:
        subsidy_id: ID de la subvention
        applicant: Informations sur le demandeur
        property_data: Informations sur la propriété
        project: Informations sur le projet
        bank_details: Informations bancaires
        user_id: ID de l'utilisateur
        
    Returns:
        Les détails du brouillon créé
    """
    # Vérifier que la subvention existe
    subsidy = subsidy_data_manager.get_subsidy_by_id(subsidy_id)
    if not subsidy:
        return None
    
    # Générer un ID unique pour le brouillon
    draft_id = f"DRAFT-{uuid.uuid4().hex[:8].upper()}"
    
    # Créer le brouillon
    now = datetime.now()
    draft_data = {
        "id": draft_id,
        "subsidy_id": subsidy_id,
        "user_id": user_id,
        "status": "draft",
        "last_updated": now,
        "applicant": applicant.dict() if applicant else None,
        "property": property_data.dict() if property_data else None,
        "project": project.dict() if project else None,
        "bank_details": bank_details.dict() if bank_details else None
    }
    
    # Stocker le brouillon dans la base de données simulée
    drafts_db[draft_id] = draft_data
    
    return ApplicationDraftResponse(**draft_data)


def update_draft(
    draft_id: str,
    applicant: Optional[Applicant] = None,
    property_data: Optional[Property] = None,
    project: Optional[Project] = None,
    bank_details: Optional[BankDetails] = None
) -> Optional[ApplicationDraftResponse]:
    """
    Met à jour un brouillon d'application de subvention existant.
    
    Args:
        draft_id: ID du brouillon
        applicant: Informations sur le demandeur
        property_data: Informations sur la propriété
        project: Informations sur le projet
        bank_details: Informations bancaires
        
    Returns:
        Les détails du brouillon mis à jour ou None si le brouillon n'existe pas
    """
    # Vérifier que le brouillon existe
    if draft_id not in drafts_db:
        return None
    
    # Récupérer le brouillon existant
    existing_draft = drafts_db[draft_id]
    
    # Mettre à jour le brouillon
    now = datetime.now()
    existing_draft["last_updated"] = now
    
    if applicant:
        existing_draft["applicant"] = applicant.dict()
    
    if property_data:
        existing_draft["property"] = property_data.dict()
    
    if project:
        existing_draft["project"] = project.dict()
    
    if bank_details:
        existing_draft["bank_details"] = bank_details.dict()
    
    return ApplicationDraftResponse(**existing_draft)


def get_application_by_id(application_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère les détails d'une application de subvention.
    
    Args:
        application_id: ID de l'application
        
    Returns:
        Les détails de l'application ou None si l'application n'existe pas
    """
    return applications_db.get(application_id)


def get_draft_by_id(draft_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère les détails d'un brouillon d'application de subvention.
    
    Args:
        draft_id: ID du brouillon
        
    Returns:
        Les détails du brouillon ou None si le brouillon n'existe pas
    """
    return drafts_db.get(draft_id)


def add_note_to_application(
    application_id: str,
    content: str,
    author: str,
    author_type: str
) -> Optional[Dict[str, Any]]:
    """
    Ajoute une note à une application de subvention.
    
    Args:
        application_id: ID de l'application
        content: Contenu de la note
        author: Auteur de la note
        author_type: Type d'auteur (admin, user)
        
    Returns:
        Les détails de la note ajoutée ou None si l'application n'existe pas
    """
    # Vérifier que l'application existe
    if application_id not in applications_db:
        return None
    
    # Créer la note
    now = datetime.now()
    note_id = f"note-{uuid.uuid4().hex[:8]}"
    note_data = {
        "id": note_id,
        "date": now,
        "author": author,
        "author_type": author_type,
        "content": content
    }
    
    # Ajouter la note à l'application
    applications_db[application_id]["notes"].append(note_data)
    
    # Mettre à jour la date de dernière mise à jour de l'application
    applications_db[application_id]["last_updated"] = now
    
    return {
        "id": note_id,
        "date": now,
        "author": author,
        "authorType": author_type,
        "content": content
    }


def add_document_to_application(
    application_id: str,
    document_id: str,
    file_name: str,
    file_size: int
) -> Optional[Dict[str, Any]]:
    """
    Ajoute un document à une application de subvention.
    
    Args:
        application_id: ID de l'application
        document_id: ID du document
        file_name: Nom du fichier
        file_size: Taille du fichier en octets
        
    Returns:
        Les détails du document ajouté ou None si l'application n'existe pas
    """
    # Vérifier que l'application existe
    if application_id not in applications_db:
        return None
    
    # Créer le document
    now = datetime.now()
    document_data = {
        "id": document_id,
        "name": file_name,
        "status": "pending",
        "upload_date": now,
        "size": file_size
    }
    
    # Vérifier si le document existe déjà
    existing_document = None
    for doc in applications_db[application_id]["documents"]:
        if doc["id"] == document_id:
            existing_document = doc
            break
    
    if existing_document:
        # Mettre à jour le document existant
        existing_document.update(document_data)
    else:
        # Ajouter le nouveau document à l'application
        applications_db[application_id]["documents"].append(document_data)
    
    # Mettre à jour la date de dernière mise à jour de l'application
    applications_db[application_id]["last_updated"] = now
    
    # Ajouter une entrée dans l'historique
    history_entry = {
        "id": f"hist-{uuid.uuid4().hex[:8]}",
        "date": now,
        "status": "document_uploaded",
        "description": f"Document '{file_name}' téléchargé"
    }
    applications_db[application_id]["history"].append(history_entry)
    
    return {
        "id": document_id,
        "name": file_name,
        "status": "pending",
        "uploadDate": now,
        "size": file_size
    }


def get_user_applications(
    user_id: str,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Récupère les applications de subvention d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        status: Filtre par statut (optionnel)
        
    Returns:
        Liste des applications de l'utilisateur
    """
    # Filtrer les applications par utilisateur
    user_applications = []
    for app_id, app_data in applications_db.items():
        if app_data.get("user_id") == user_id:
            # Filtrer par statut si spécifié
            if status is None or app_data["status"] == status:
                user_applications.append(app_data)
    
    return user_applications


def get_user_drafts(
    user_id: str
) -> List[Dict[str, Any]]:
    """
    Récupère les brouillons d'application de subvention d'un utilisateur.
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        Liste des brouillons de l'utilisateur
    """
    # Filtrer les brouillons par utilisateur
    user_drafts = []
    for draft_id, draft_data in drafts_db.items():
        if draft_data.get("user_id") == user_id:
            user_drafts.append(draft_data)
    
    return user_drafts
