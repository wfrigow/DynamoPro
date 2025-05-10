"""
Routes pour les applications de subventions
----------------------------------------
Endpoints pour la gestion des applications de subventions
"""

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Path, Query
from typing import List, Optional
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from ..auth import get_current_active_subsidy_user, UserInDB
from ..models.application_models import (
    ApplicationCreate, ApplicationDraftCreate, ApplicationResponse,
    ApplicationDraftResponse, ApplicationNoteCreate, DocumentUploadResponse
)
from ..data.subsidy_data_manager import subsidy_data_manager
from ..database.database import get_db
from ..database import crud

# Création du routeur
router = APIRouter(
    prefix="/applications",
    tags=["applications"],
    responses={401: {"description": "Non autorisé"}},
)


@router.post("/{subsidy_id}", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    subsidy_id: str = Path(..., description="ID de la subvention"),
    application: ApplicationCreate = None,
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle application de subvention.
    
    - **subsidy_id**: ID de la subvention
    - **application**: Données de l'application
    
    Retourne les détails de l'application créée.
    """
    # Vérifier que la subvention existe
    subsidy = subsidy_data_manager.get_subsidy_by_id(subsidy_id)
    if not subsidy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subvention avec ID {subsidy_id} non trouvée"
        )
    
    # Créer l'application dans la base de données
    subsidy_data = {
        "id": subsidy.id,
        "name": subsidy.name.get("fr"),
        "provider": subsidy.provider.get("fr"),
        "maxAmount": subsidy.max_amount,
        "percentage": subsidy.percentage,
        "calculatedAmount": None
    }
    
    db_application = crud.create_application(
        db=db,
        subsidy_id=subsidy_id,
        user_id=current_user.id,
        applicant_data=application.applicant.dict(),
        property_data=application.property.dict(),
        project_data=application.project.dict(),
        bank_details=application.bank_details.dict() if application.bank_details else None,
        subsidy_data=subsidy_data
    )
    
    # Préparer la réponse
    application_data = {
        "id": db_application.id,
        "subsidyId": db_application.subsidy_id,
        "status": db_application.status,
        "statusLabel": db_application.status_label,
        "submissionDate": db_application.submission_date,
        "lastUpdated": db_application.last_updated,
        "referenceNumber": db_application.reference_number,
        "applicant": db_application.applicant_data,
        "property": db_application.property_data,
        "project": db_application.project_data,
        "bankDetails": db_application.bank_details,
        "subsidy": db_application.subsidy_data,
        "documents": [],
        "notes": [],
        "history": crud.get_application_history(db, db_application.id),
        "nextSteps": db_application.next_steps
    }
    
    return ApplicationResponse(**application_data)


@router.post("/drafts/{subsidy_id}", response_model=ApplicationDraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    subsidy_id: str = Path(..., description="ID de la subvention"),
    draft: ApplicationDraftCreate = None,
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau brouillon d'application de subvention.
    
    - **subsidy_id**: ID de la subvention
    - **draft**: Données du brouillon
    
    Retourne les détails du brouillon créé.
    """
    # Vérifier que la subvention existe
    subsidy = subsidy_data_manager.get_subsidy_by_id(subsidy_id)
    if not subsidy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subvention avec ID {subsidy_id} non trouvée"
        )
    
    # Créer le brouillon dans la base de données
    db_draft = crud.create_draft(
        db=db,
        subsidy_id=subsidy_id,
        user_id=current_user.id,
        applicant_data=draft.applicant.dict() if draft.applicant else None,
        property_data=draft.property.dict() if draft.property else None,
        project_data=draft.project.dict() if draft.project else None,
        bank_details=draft.bank_details.dict() if draft.bank_details else None
    )
    
    # Préparer la réponse
    draft_data = {
        "id": db_draft.id,
        "subsidyId": db_draft.subsidy_id,
        "status": db_draft.status,
        "lastUpdated": db_draft.last_updated,
        "applicant": db_draft.applicant_data,
        "property": db_draft.property_data,
        "project": db_draft.project_data,
        "bankDetails": db_draft.bank_details
    }
    
    return ApplicationDraftResponse(**draft_data)


@router.put("/drafts/{subsidy_id}/{draft_id}", response_model=ApplicationDraftResponse)
async def update_draft(
    subsidy_id: str = Path(..., description="ID de la subvention"),
    draft_id: str = Path(..., description="ID du brouillon"),
    draft: ApplicationDraftCreate = None,
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour un brouillon d'application de subvention existant.
    
    - **subsidy_id**: ID de la subvention
    - **draft_id**: ID du brouillon
    - **draft**: Données mises à jour du brouillon
    
    Retourne les détails du brouillon mis à jour.
    """
    # Récupérer le brouillon existant
    db_draft = crud.get_draft(db, draft_id)
    if not db_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brouillon avec ID {draft_id} non trouvé"
        )
    
    # Vérifier que le brouillon appartient à la subvention spécifiée
    if db_draft.subsidy_id != subsidy_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Le brouillon {draft_id} n'appartient pas à la subvention {subsidy_id}"
        )
    
    # Vérifier que le brouillon appartient à l'utilisateur courant
    if db_draft.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à modifier ce brouillon"
        )
    
    # Mettre à jour le brouillon
    updated_draft = crud.update_draft(
        db=db,
        draft_id=draft_id,
        applicant_data=draft.applicant.dict() if draft.applicant else None,
        property_data=draft.property.dict() if draft.property else None,
        project_data=draft.project.dict() if draft.project else None,
        bank_details=draft.bank_details.dict() if draft.bank_details else None
    )
    
    if not updated_draft:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour du brouillon"
        )
    
    # Préparer la réponse
    draft_data = {
        "id": updated_draft.id,
        "subsidyId": updated_draft.subsidy_id,
        "status": updated_draft.status,
        "lastUpdated": updated_draft.last_updated,
        "applicant": updated_draft.applicant_data,
        "property": updated_draft.property_data,
        "project": updated_draft.project_data,
        "bankDetails": updated_draft.bank_details
    }
    
    return ApplicationDraftResponse(**draft_data)


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str = Path(..., description="ID de l'application"),
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'une application de subvention.
    
    - **application_id**: ID de l'application
    
    Retourne les détails de l'application.
    """
    # Récupérer l'application depuis la base de données
    db_application = crud.get_application(db, application_id)
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application avec ID {application_id} non trouvée"
        )
    
    # Vérifier que l'utilisateur est autorisé à accéder à cette application
    if db_application.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à cette application"
        )
    
    # Récupérer les documents, notes et historique de l'application
    documents = crud.get_application_documents(db, application_id)
    notes = crud.get_application_notes(db, application_id)
    history = crud.get_application_history(db, application_id)
    
    # Préparer la réponse
    application_data = {
        "id": db_application.id,
        "subsidyId": db_application.subsidy_id,
        "status": db_application.status,
        "statusLabel": db_application.status_label,
        "submissionDate": db_application.submission_date,
        "lastUpdated": db_application.last_updated,
        "referenceNumber": db_application.reference_number,
        "applicant": db_application.applicant_data,
        "property": db_application.property_data,
        "project": db_application.project_data,
        "bankDetails": db_application.bank_details,
        "subsidy": db_application.subsidy_data,
        "documents": [
            {
                "id": doc.id,
                "name": doc.name,
                "status": doc.status,
                "uploadDate": doc.upload_date,
                "validationDate": doc.validation_date,
                "comments": doc.comments,
                "size": doc.size
            } for doc in documents
        ],
        "notes": [
            {
                "id": note.id,
                "date": note.date,
                "author": note.author,
                "authorType": note.author_type,
                "content": note.content
            } for note in notes
        ],
        "history": [
            {
                "id": hist.id,
                "date": hist.date,
                "status": hist.status,
                "description": hist.description
            } for hist in history
        ],
        "nextSteps": db_application.next_steps
    }
    
    return ApplicationResponse(**application_data)


@router.get("/drafts/{draft_id}", response_model=ApplicationDraftResponse)
async def get_draft(
    draft_id: str = Path(..., description="ID du brouillon"),
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'un brouillon d'application de subvention.
    
    - **draft_id**: ID du brouillon
    
    Retourne les détails du brouillon.
    """
    # Récupérer le brouillon depuis la base de données
    db_draft = crud.get_draft(db, draft_id)
    if not db_draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brouillon avec ID {draft_id} non trouvé"
        )
    
    # Vérifier que l'utilisateur est autorisé à accéder à ce brouillon
    if db_draft.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder à ce brouillon"
        )
    
    # Préparer la réponse
    draft_data = {
        "id": db_draft.id,
        "subsidyId": db_draft.subsidy_id,
        "status": db_draft.status,
        "lastUpdated": db_draft.last_updated,
        "applicant": db_draft.applicant_data,
        "property": db_draft.property_data,
        "project": db_draft.project_data,
        "bankDetails": db_draft.bank_details
    }
    
    return ApplicationDraftResponse(**draft_data)


@router.post("/{application_id}/notes", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_note(
    application_id: str = Path(..., description="ID de l'application"),
    note: ApplicationNoteCreate = None,
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Ajoute une note à une application de subvention.
    
    - **application_id**: ID de l'application
    - **note**: Contenu de la note
    
    Retourne les détails de la note ajoutée.
    """
    # Vérifier que l'application existe
    db_application = crud.get_application(db, application_id)
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application avec ID {application_id} non trouvée"
        )
    
    # Vérifier que l'utilisateur est autorisé à ajouter une note à cette application
    if db_application.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à ajouter une note à cette application"
        )
    
    # Créer la note dans la base de données
    author_type = "admin" if current_user.is_superuser else "user"
    db_note = crud.create_note(
        db=db,
        application_id=application_id,
        content=note.content,
        author=current_user.email,
        author_type=author_type
    )
    
    # Préparer la réponse
    return {
        "id": db_note.id,
        "date": db_note.date.isoformat(),
        "author": db_note.author,
        "authorType": db_note.author_type,
        "content": db_note.content
    }


@router.post("/{application_id}/documents/{document_id}", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    application_id: str = Path(..., description="ID de l'application"),
    document_id: str = Path(..., description="ID du document"),
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Télécharge un document pour une application de subvention.
    
    - **application_id**: ID de l'application
    - **document_id**: ID du document
    - **file**: Fichier à télécharger
    
    Retourne les détails du document téléchargé.
    """
    # Vérifier que l'application existe
    db_application = crud.get_application(db, application_id)
    if not db_application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application avec ID {application_id} non trouvée"
        )
    
    # Vérifier que l'utilisateur est autorisé à télécharger un document pour cette application
    if db_application.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à télécharger un document pour cette application"
        )
    
    # Lire le contenu du fichier
    contents = await file.read()
    file_size = len(contents)
    
    # Dans une implémentation réelle, nous sauvegarderions le fichier sur disque ou dans un stockage cloud
    # Pour l'instant, nous simulons le stockage
    file_path = f"/tmp/{document_id}_{file.filename}"  # Chemin fictif
    
    # Créer ou mettre à jour le document dans la base de données
    db_document = crud.create_document(
        db=db,
        application_id=application_id,
        name=file.filename,
        size=file_size,
        file_path=file_path,
        content_type=file.content_type
    )
    
    # Préparer la réponse
    return DocumentUploadResponse(
        id=db_document.id,
        name=db_document.name,
        status=db_document.status,
        uploadDate=db_document.upload_date,
        size=db_document.size
    )


@router.get("/user/{user_id}", response_model=List[ApplicationResponse])
async def get_user_applications(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    status: Optional[str] = Query(None, description="Filtre par statut"),
    skip: int = Query(0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, description="Nombre maximum d'éléments à retourner"),
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les applications de subvention d'un utilisateur.
    
    - **user_id**: ID de l'utilisateur
    - **status**: Filtre par statut (optionnel)
    - **skip**: Nombre d'éléments à sauter (pagination)
    - **limit**: Nombre maximum d'éléments à retourner (pagination)
    
    Retourne la liste des applications de l'utilisateur.
    """
    # Vérifier que l'utilisateur est autorisé à accéder aux applications
    if user_id != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder aux applications de cet utilisateur"
        )
    
    # Récupérer les applications de l'utilisateur depuis la base de données
    db_applications = crud.get_user_applications(db, user_id, status, skip, limit)
    
    # Préparer la réponse
    result = []
    for app in db_applications:
        # Récupérer les documents, notes et historique de l'application
        documents = crud.get_application_documents(db, app.id)
        notes = crud.get_application_notes(db, app.id)
        history = crud.get_application_history(db, app.id)
        
        application_data = {
            "id": app.id,
            "subsidyId": app.subsidy_id,
            "status": app.status,
            "statusLabel": app.status_label,
            "submissionDate": app.submission_date,
            "lastUpdated": app.last_updated,
            "referenceNumber": app.reference_number,
            "applicant": app.applicant_data,
            "property": app.property_data,
            "project": app.project_data,
            "bankDetails": app.bank_details,
            "subsidy": app.subsidy_data,
            "documents": [
                {
                    "id": doc.id,
                    "name": doc.name,
                    "status": doc.status,
                    "uploadDate": doc.upload_date,
                    "validationDate": doc.validation_date,
                    "comments": doc.comments,
                    "size": doc.size
                } for doc in documents
            ],
            "notes": [
                {
                    "id": note.id,
                    "date": note.date,
                    "author": note.author,
                    "authorType": note.author_type,
                    "content": note.content
                } for note in notes
            ],
            "history": [
                {
                    "id": hist.id,
                    "date": hist.date,
                    "status": hist.status,
                    "description": hist.description
                } for hist in history
            ],
            "nextSteps": app.next_steps
        }
        
        result.append(ApplicationResponse(**application_data))
    
    return result


@router.get("/user/{user_id}/drafts", response_model=List[ApplicationDraftResponse])
async def get_user_drafts(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    skip: int = Query(0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, description="Nombre maximum d'éléments à retourner"),
    current_user: UserInDB = Depends(get_current_active_subsidy_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les brouillons d'applications de subvention d'un utilisateur.
    
    - **user_id**: ID de l'utilisateur
    - **skip**: Nombre d'éléments à sauter (pagination)
    - **limit**: Nombre maximum d'éléments à retourner (pagination)
    
    Retourne la liste des brouillons de l'utilisateur.
    """
    # Vérifier que l'utilisateur est autorisé à accéder aux brouillons
    if user_id != str(current_user.id) and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accéder aux brouillons de cet utilisateur"
        )
    
    # Récupérer les brouillons de l'utilisateur depuis la base de données
    db_drafts = crud.get_user_drafts(db, user_id)
    
    # Limiter les résultats pour la pagination
    db_drafts = db_drafts[skip:skip+limit]
    
    # Préparer la réponse
    result = []
    for draft in db_drafts:
        draft_data = {
            "id": draft.id,
            "subsidyId": draft.subsidy_id,
            "status": draft.status,
            "lastUpdated": draft.last_updated,
            "applicant": draft.applicant_data,
            "property": draft.property_data,
            "project": draft.project_data,
            "bankDetails": draft.bank_details
        }
        
        result.append(ApplicationDraftResponse(**draft_data))
    
    return result
