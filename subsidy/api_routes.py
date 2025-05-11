"""
Routes API pour l'agent de subvention
------------------------------------
Ce module définit les endpoints API pour l'agent de subvention, permettant
la recherche de subventions, la création et le suivi des demandes, ainsi
que la gestion des documents associés.
"""

import os
import uuid
from typing import Dict, List, Optional, Any, Union
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, UUID4, Field
import logging
from datetime import datetime

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.auth import get_current_active_user, UserInDB
from common.models import DomainType

# Importation circulaire, nous allons définir ces classes directement ici
from main import SubsidyResponse, ApplicationFormResponse, ApplicationStatusUpdate
from subsidy_db import get_subsidy_database, Subsidy, SubsidyDocumentType
from document_processor import get_document_processor, DocumentValidationStatus, DocumentMetadata
from application_tracker import (
    get_application_tracker, SubsidyApplication, ApplicationStatus, 
    DocumentStatus, ApplicationNote
)
from form_generator import get_form_generator

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création du routeur
router = APIRouter(prefix="/api/v1/subsidies", tags=["subsidies"])


# Modèles de données pour les requêtes et réponses
class SubsidyRequest(BaseModel):
    """Requête de recherche de subventions"""
    user_id: UUID4
    recommendation_ids: Optional[List[UUID4]] = None
    domains: List[DomainType] = [DomainType.ENERGY, DomainType.WATER]


class CreateApplicationRequest(BaseModel):
    """Requête de création d'une demande"""
    user_id: UUID4
    subsidy_id: UUID4
    recommendation_id: Optional[UUID4] = None
    form_data: Optional[Dict[str, Any]] = None


class UpdateApplicationRequest(BaseModel):
    """Requête de mise à jour d'une demande"""
    application_id: UUID4
    form_data: Optional[Dict[str, Any]] = None
    status: Optional[ApplicationStatus] = None
    comment: Optional[str] = None


class UploadDocumentRequest(BaseModel):
    """Requête de téléchargement de document (métadonnées)"""
    application_id: UUID4
    document_id: UUID4
    document_type: SubsidyDocumentType


class AddNoteRequest(BaseModel):
    """Requête d'ajout de note"""
    application_id: UUID4
    content: str
    is_internal: bool = False


class ApplicationSummary(BaseModel):
    """Résumé d'une demande de subvention"""
    id: str
    subsidy_id: str
    subsidy_name: str
    provider_name: str
    status: ApplicationStatus
    creation_date: datetime
    submission_date: Optional[datetime] = None
    amount_requested: Optional[float] = None
    amount_approved: Optional[float] = None
    documents_submitted: int
    documents_validated: int
    total_documents: int
    next_action: Optional[str] = None
    days_remaining: Optional[int] = None


# Routes pour les subventions
@router.post("/find", response_model=SubsidyResponse)
async def find_subsidies(
    request: SubsidyRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour la recherche de subventions applicables"""
    # Cette fonction est déjà implémentée dans main.py
    # On va appeler la fonction existante
    from main import subsidy_service
    return await subsidy_service.find_applicable_subsidies(
        user_id=request.user_id,
        recommendation_ids=request.recommendation_ids,
        domains=request.domains
    )


@router.post("/generate-form", response_model=ApplicationFormResponse)
async def generate_application_form(
    request: SubsidyRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour la génération d'un formulaire de demande"""
    # Cette fonction est déjà implémentée dans main.py
    # On va appeler la fonction existante
    from main import subsidy_service
    return await subsidy_service.generate_application_form(
        user_id=request.user_id,
        subsidy_id=request.subsidy_id,
        recommendation_id=request.recommendation_id
    )


# Routes pour les demandes
@router.post("/applications", response_model=SubsidyApplication)
async def create_application(
    request: CreateApplicationRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour la création d'une nouvelle demande"""
    try:
        # Vérifier que la subvention existe
        subsidy_db = get_subsidy_database()
        subsidy = subsidy_db.get_subsidy_by_id(str(request.subsidy_id))
        if not subsidy:
            raise HTTPException(status_code=404, detail="Subvention non trouvée")
        
        # Si form_data n'est pas fourni, on génère un formulaire par défaut
        form_data = request.form_data
        if not form_data:
            # Récupérer les données utilisateur
            from main import subsidy_service
            user_data = await subsidy_service.get_user_data(request.user_id)
            
            # Récupérer la recommandation si spécifiée
            recommendation = None
            if request.recommendation_id:
                recommendations = await subsidy_service.get_recommendations([request.recommendation_id])
                if recommendations:
                    recommendation = recommendations[0]
            
            # Générer le formulaire
            form_generator = get_form_generator()
            form_data = form_generator.generate_form_data(
                subsidy=subsidy,
                user_profile=user_data.get("profile", {}),
                property_data=user_data.get("properties", [{}])[0] if user_data.get("properties") else None,
                recommendation=recommendation
            )
        
        # Créer la demande
        tracker = get_application_tracker()
        application = tracker.create_application(
            user_id=str(request.user_id),
            subsidy_id=str(request.subsidy_id),
            recommendation_id=str(request.recommendation_id) if request.recommendation_id else None,
            form_data=form_data
        )
        
        return application
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la création de la demande: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de serveur")


@router.get("/applications/{application_id}", response_model=SubsidyApplication)
async def get_application(
    application_id: UUID4,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour récupérer une demande"""
    tracker = get_application_tracker()
    application = tracker.get_application(str(application_id))
    
    if not application:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Vérifier que l'utilisateur a accès à cette demande
    if str(current_user.id) != application.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    return application


@router.put("/applications/{application_id}", response_model=SubsidyApplication)
async def update_application(
    application_id: UUID4,
    request: UpdateApplicationRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour mettre à jour une demande"""
    tracker = get_application_tracker()
    
    # Vérifier que la demande existe
    application = tracker.get_application(str(application_id))
    if not application:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Vérifier que l'utilisateur a accès à cette demande
    if str(current_user.id) != application.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    try:
        # Mettre à jour la demande
        updated_application = tracker.update_application(
            application_id=str(application_id),
            form_data=request.form_data,
            status=request.status,
            comment=request.comment
        )
        
        return updated_application
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de la demande {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de serveur")


@router.get("/applications/user/{user_id}", response_model=List[ApplicationSummary])
async def get_user_applications(
    user_id: UUID4,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour récupérer toutes les demandes d'un utilisateur"""
    # Vérifier que l'utilisateur a accès à ces demandes
    if str(current_user.id) != str(user_id) and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    tracker = get_application_tracker()
    applications = tracker.get_user_applications(str(user_id))
    
    subsidy_db = get_subsidy_database()
    
    # Convertir en résumés
    summaries = []
    for app in applications:
        # Récupérer les informations de la subvention
        subsidy = subsidy_db.get_subsidy_by_id(app.subsidy_id)
        provider = subsidy_db.get_provider(subsidy.provider_id) if subsidy else None
        
        # Récupérer les échéances
        deadlines = tracker.get_application_deadlines(app.id)
        
        # Calculer les statistiques de documents
        total_docs = len(app.documents)
        submitted_docs = sum(1 for doc in app.documents if doc.submitted)
        validated_docs = sum(1 for doc in app.documents if doc.validated)
        
        # Créer le résumé
        summary = ApplicationSummary(
            id=app.id,
            subsidy_id=app.subsidy_id,
            subsidy_name=subsidy.name if subsidy else "Subvention inconnue",
            provider_name=provider.name if provider else "Fournisseur inconnu",
            status=app.status,
            creation_date=app.creation_date,
            submission_date=app.submission_date,
            amount_requested=app.amount_requested,
            amount_approved=app.amount_approved,
            documents_submitted=submitted_docs,
            documents_validated=validated_docs,
            total_documents=total_docs,
            next_action=deadlines.get("next_action"),
            days_remaining=deadlines.get("days_remaining")
        )
        
        summaries.append(summary)
    
    return summaries


@router.put("/applications/{application_id}/submit", response_model=SubsidyApplication)
async def submit_application(
    application_id: UUID4,
    background_tasks: BackgroundTasks,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour soumettre une demande"""
    tracker = get_application_tracker()
    
    # Vérifier que la demande existe
    application = tracker.get_application(str(application_id))
    if not application:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Vérifier que l'utilisateur a accès à cette demande
    if str(current_user.id) != application.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifier que la demande est à l'état DRAFT
    if application.status != ApplicationStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Seules les demandes en brouillon peuvent être soumises")
    
    try:
        # Mettre à jour le statut de la demande
        updated_application = tracker.update_application(
            application_id=str(application_id),
            status=ApplicationStatus.SUBMITTED,
            comment="Demande soumise par l'utilisateur"
        )
        
        # Traitement en arrière-plan (à implémenter)
        # Par exemple, envoi d'un email de confirmation
        background_tasks.add_task(
            _send_application_submitted_notification,
            application_id=str(application_id),
            user_id=str(current_user.id)
        )
        
        return updated_application
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la soumission de la demande {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de serveur")


# Routes pour les documents
@router.post("/documents/upload", response_model=DocumentMetadata)
async def upload_document(
    file: UploadFile = File(...),
    application_id: str = Form(...),
    document_id: str = Form(...),
    document_type: str = Form(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour télécharger un document"""
    tracker = get_application_tracker()
    processor = get_document_processor()
    
    # Vérifier que la demande existe
    application = tracker.get_application(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Vérifier que l'utilisateur a accès à cette demande
    if str(current_user.id) != application.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Vérifier que le document est associé à la demande
    document = next((doc for doc in application.documents if doc.document_id == document_id), None)
    if not document:
        raise HTTPException(status_code=404, detail="Document non trouvé dans la demande")
    
    try:
        # Convertir le type de document en enum
        doc_type = SubsidyDocumentType(document_type)
        
        # Créer un fichier temporaire
        temp_dir = os.path.join(os.path.dirname(__file__), "temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_file_path = os.path.join(temp_dir, file.filename)
        
        # Sauvegarder le fichier
        with open(temp_file_path, "wb") as buffer:
            contents = await file.read()
            buffer.write(contents)
        
        # Récupérer la subvention
        subsidy_db = get_subsidy_database()
        subsidy = subsidy_db.get_subsidy_by_id(application.subsidy_id)
        
        # Traiter le document
        metadata = await processor.process_document(
            file_path=temp_file_path,
            document_type=doc_type,
            subsidy=subsidy
        )
        
        # Mettre à jour le statut du document dans la demande
        tracker.update_document_status(
            application_id=application_id,
            document_id=document_id,
            submitted=True,
            validated=metadata.validation_status == DocumentValidationStatus.VALID,
            comments=metadata.validation_message
        )
        
        # Nettoyage
        os.remove(temp_file_path)
        
        return metadata
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors du téléchargement du document: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de serveur")


@router.put("/documents/{document_id}/validate", response_model=DocumentStatus)
async def validate_document(
    application_id: UUID4,
    document_id: UUID4,
    is_valid: bool = True,
    comments: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour valider manuellement un document (admin uniquement)"""
    # Vérifier que l'utilisateur est admin
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Seuls les administrateurs peuvent valider les documents")
    
    tracker = get_application_tracker()
    
    try:
        # Mettre à jour le statut du document
        application = tracker.update_document_status(
            application_id=str(application_id),
            document_id=str(document_id),
            validated=is_valid,
            comments=comments
        )
        
        # Récupérer le document mis à jour
        document = next(
            (doc for doc in application.documents if doc.document_id == str(document_id)),
            None
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document non trouvé après mise à jour")
        
        return document
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de la validation du document: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de serveur")


# Routes pour les notes
@router.post("/applications/{application_id}/notes", response_model=ApplicationNote)
async def add_note(
    application_id: UUID4,
    request: AddNoteRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Endpoint pour ajouter une note à une demande"""
    tracker = get_application_tracker()
    
    # Vérifier que la demande existe
    application = tracker.get_application(str(application_id))
    if not application:
        raise HTTPException(status_code=404, detail="Demande non trouvée")
    
    # Vérifier que l'utilisateur a accès à cette demande
    if str(current_user.id) != application.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Si c'est une note interne, vérifier que l'utilisateur est admin
    if request.is_internal and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Seuls les administrateurs peuvent ajouter des notes internes")
    
    try:
        # Ajouter la note
        note = tracker.add_note(
            application_id=str(application_id),
            author=f"{current_user.first_name} {current_user.last_name}",
            content=request.content,
            is_internal=request.is_internal
        )
        
        return note
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de la note: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur de serveur")


# Fonctions d'aide
async def _send_application_submitted_notification(application_id: str, user_id: str) -> None:
    """
    Envoie une notification à l'utilisateur lorsqu'une demande est soumise
    
    Args:
        application_id: ID de la demande
        user_id: ID de l'utilisateur
    """
    # À implémenter: envoi d'email ou notification push
    logger.info(f"Notification envoyée pour la demande {application_id} à l'utilisateur {user_id}")
