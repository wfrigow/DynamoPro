"""
Opérations CRUD pour l'API de subventions
---------------------------------------
Fonctions pour créer, lire, mettre à jour et supprimer des données dans la base de données
"""

from datetime import datetime
import uuid
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

import sys
import os
# Ajouter le répertoire parent au sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .models import User, Application, ApplicationDraft, ApplicationDocument, ApplicationNote, ApplicationHistory
from ..auth import get_password_hash, verify_password


# Opérations CRUD pour les utilisateurs

def get_user(db: Session, user_id: str) -> Optional[User]:
    """Récupère un utilisateur par son ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Récupère un utilisateur par son email"""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Récupère une liste d'utilisateurs"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, email: str, password: str, first_name: Optional[str] = None, 
                last_name: Optional[str] = None, is_superuser: bool = False) -> User:
    """Crée un nouvel utilisateur"""
    hashed_password = get_password_hash(password)
    db_user = User(
        id=str(uuid.uuid4()),
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        is_superuser=is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: str, user_data: Dict[str, Any]) -> Optional[User]:
    """Met à jour un utilisateur existant"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Mise à jour des champs
    for key, value in user_data.items():
        if key == "password":
            setattr(db_user, "hashed_password", get_password_hash(value))
        elif hasattr(db_user, key):
            setattr(db_user, key, value)
    
    db_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authentifie un utilisateur par email et mot de passe"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Opérations CRUD pour les applications

def get_application(db: Session, application_id: str) -> Optional[Application]:
    """Récupère une application par son ID"""
    return db.query(Application).filter(Application.id == application_id).first()


def get_application_by_reference(db: Session, reference_number: str) -> Optional[Application]:
    """Récupère une application par son numéro de référence"""
    return db.query(Application).filter(Application.reference_number == reference_number).first()


def get_user_applications(db: Session, user_id: str, status: Optional[str] = None, 
                          skip: int = 0, limit: int = 100) -> List[Application]:
    """Récupère les applications d'un utilisateur"""
    query = db.query(Application).filter(Application.user_id == user_id)
    if status:
        query = query.filter(Application.status == status)
    return query.order_by(Application.last_updated.desc()).offset(skip).limit(limit).all()


def create_application(db: Session, subsidy_id: str, user_id: str, applicant_data: Dict[str, Any],
                      property_data: Dict[str, Any], project_data: Dict[str, Any],
                      bank_details: Optional[Dict[str, Any]] = None,
                      subsidy_data: Optional[Dict[str, Any]] = None,
                      next_steps: Optional[List[str]] = None) -> Application:
    """Crée une nouvelle application de subvention"""
    # Générer un numéro de référence unique
    reference_number = f"PRE-{datetime.now().year}-{uuid.uuid4().hex[:5].upper()}"
    
    # Créer l'application
    db_application = Application(
        id=str(uuid.uuid4()),
        reference_number=reference_number,
        subsidy_id=subsidy_id,
        user_id=user_id,
        status="submitted",
        status_label="Soumise",
        submission_date=datetime.utcnow(),
        applicant_data=applicant_data,
        property_data=property_data,
        project_data=project_data,
        bank_details=bank_details,
        subsidy_data=subsidy_data or {},
        next_steps=next_steps or ["Vérification des documents", "Évaluation technique", "Décision finale"]
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Ajouter une entrée dans l'historique
    create_application_history(db, db_application.id, "submitted", "Demande soumise")
    
    return db_application


def update_application_status(db: Session, application_id: str, status: str, 
                             status_label: str, description: str) -> Optional[Application]:
    """Met à jour le statut d'une application"""
    db_application = get_application(db, application_id)
    if not db_application:
        return None
    
    db_application.status = status
    db_application.status_label = status_label
    db_application.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_application)
    
    # Ajouter une entrée dans l'historique
    create_application_history(db, application_id, status, description)
    
    return db_application


# Opérations CRUD pour les brouillons d'applications

def get_draft(db: Session, draft_id: str) -> Optional[ApplicationDraft]:
    """Récupère un brouillon par son ID"""
    return db.query(ApplicationDraft).filter(ApplicationDraft.id == draft_id).first()


def get_user_drafts(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[ApplicationDraft]:
    """Récupère les brouillons d'un utilisateur"""
    return db.query(ApplicationDraft).filter(ApplicationDraft.user_id == user_id)\
        .order_by(ApplicationDraft.last_updated.desc()).offset(skip).limit(limit).all()


def create_draft(db: Session, subsidy_id: str, user_id: str, 
                applicant_data: Optional[Dict[str, Any]] = None,
                property_data: Optional[Dict[str, Any]] = None,
                project_data: Optional[Dict[str, Any]] = None,
                bank_details: Optional[Dict[str, Any]] = None) -> ApplicationDraft:
    """Crée un nouveau brouillon d'application"""
    db_draft = ApplicationDraft(
        id=str(uuid.uuid4()),
        subsidy_id=subsidy_id,
        user_id=user_id,
        applicant_data=applicant_data,
        property_data=property_data,
        project_data=project_data,
        bank_details=bank_details
    )
    db.add(db_draft)
    db.commit()
    db.refresh(db_draft)
    return db_draft


def update_draft(db: Session, draft_id: str, 
                applicant_data: Optional[Dict[str, Any]] = None,
                property_data: Optional[Dict[str, Any]] = None,
                project_data: Optional[Dict[str, Any]] = None,
                bank_details: Optional[Dict[str, Any]] = None) -> Optional[ApplicationDraft]:
    """Met à jour un brouillon existant"""
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    if applicant_data is not None:
        db_draft.applicant_data = applicant_data
    
    if property_data is not None:
        db_draft.property_data = property_data
    
    if project_data is not None:
        db_draft.project_data = project_data
    
    if bank_details is not None:
        db_draft.bank_details = bank_details
    
    db_draft.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(db_draft)
    return db_draft


def convert_draft_to_application(db: Session, draft_id: str, subsidy_data: Dict[str, Any]) -> Optional[Application]:
    """Convertit un brouillon en application soumise"""
    db_draft = get_draft(db, draft_id)
    if not db_draft:
        return None
    
    # Vérifier que toutes les données nécessaires sont présentes
    if not db_draft.applicant_data or not db_draft.property_data or not db_draft.project_data:
        return None
    
    # Créer l'application à partir du brouillon
    db_application = create_application(
        db=db,
        subsidy_id=db_draft.subsidy_id,
        user_id=db_draft.user_id,
        applicant_data=db_draft.applicant_data,
        property_data=db_draft.property_data,
        project_data=db_draft.project_data,
        bank_details=db_draft.bank_details,
        subsidy_data=subsidy_data
    )
    
    # Supprimer le brouillon
    db.delete(db_draft)
    db.commit()
    
    return db_application


# Opérations CRUD pour les documents

def get_document(db: Session, document_id: str) -> Optional[ApplicationDocument]:
    """Récupère un document par son ID"""
    return db.query(ApplicationDocument).filter(ApplicationDocument.id == document_id).first()


def get_application_documents(db: Session, application_id: str) -> List[ApplicationDocument]:
    """Récupère tous les documents d'une application"""
    return db.query(ApplicationDocument).filter(ApplicationDocument.application_id == application_id).all()


def create_document(db: Session, application_id: str, name: str, size: int, 
                   file_path: Optional[str] = None, content_type: Optional[str] = None) -> ApplicationDocument:
    """Crée un nouveau document pour une application"""
    db_document = ApplicationDocument(
        id=str(uuid.uuid4()),
        application_id=application_id,
        name=name,
        status="pending",
        size=size,
        file_path=file_path,
        content_type=content_type
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    # Mettre à jour la date de dernière mise à jour de l'application
    update_application_last_updated(db, application_id)
    
    # Ajouter une entrée dans l'historique
    create_application_history(db, application_id, "document_uploaded", f"Document '{name}' téléchargé")
    
    return db_document


def update_document_status(db: Session, document_id: str, status: str, 
                          comments: Optional[str] = None) -> Optional[ApplicationDocument]:
    """Met à jour le statut d'un document"""
    db_document = get_document(db, document_id)
    if not db_document:
        return None
    
    db_document.status = status
    if status in ["validated", "rejected"]:
        db_document.validation_date = datetime.utcnow()
    if comments:
        db_document.comments = comments
    
    db.commit()
    db.refresh(db_document)
    
    # Mettre à jour la date de dernière mise à jour de l'application
    update_application_last_updated(db, db_document.application_id)
    
    # Ajouter une entrée dans l'historique
    status_description = {
        "validated": "validé",
        "rejected": "rejeté",
        "requested": "demandé"
    }.get(status, status)
    create_application_history(
        db, 
        db_document.application_id, 
        f"document_{status}", 
        f"Document '{db_document.name}' {status_description}"
    )
    
    return db_document


# Opérations CRUD pour les notes

def get_note(db: Session, note_id: str) -> Optional[ApplicationNote]:
    """Récupère une note par son ID"""
    return db.query(ApplicationNote).filter(ApplicationNote.id == note_id).first()


def get_application_notes(db: Session, application_id: str) -> List[ApplicationNote]:
    """Récupère toutes les notes d'une application"""
    return db.query(ApplicationNote).filter(ApplicationNote.application_id == application_id)\
        .order_by(ApplicationNote.date.desc()).all()


def create_note(db: Session, application_id: str, content: str, author: str, 
               author_type: str) -> ApplicationNote:
    """Crée une nouvelle note pour une application"""
    db_note = ApplicationNote(
        id=str(uuid.uuid4()),
        application_id=application_id,
        content=content,
        author=author,
        author_type=author_type
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Mettre à jour la date de dernière mise à jour de l'application
    update_application_last_updated(db, application_id)
    
    return db_note


# Opérations CRUD pour l'historique

def get_application_history(db: Session, application_id: str) -> List[ApplicationHistory]:
    """Récupère tout l'historique d'une application"""
    return db.query(ApplicationHistory).filter(ApplicationHistory.application_id == application_id)\
        .order_by(ApplicationHistory.date.desc()).all()


def create_application_history(db: Session, application_id: str, status: str, 
                              description: str) -> ApplicationHistory:
    """Crée une nouvelle entrée dans l'historique d'une application"""
    db_history = ApplicationHistory(
        id=str(uuid.uuid4()),
        application_id=application_id,
        status=status,
        description=description
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


# Fonctions utilitaires

def update_application_last_updated(db: Session, application_id: str) -> None:
    """Met à jour la date de dernière mise à jour d'une application"""
    db_application = get_application(db, application_id)
    if db_application:
        db_application.last_updated = datetime.utcnow()
        db.commit()


def search_applications(db: Session, query: str, user_id: Optional[str] = None, 
                       skip: int = 0, limit: int = 100) -> List[Application]:
    """Recherche des applications par texte"""
    search_query = f"%{query}%"
    base_query = db.query(Application)
    
    if user_id:
        base_query = base_query.filter(Application.user_id == user_id)
    
    return base_query.filter(
        or_(
            Application.reference_number.ilike(search_query),
            Application.status_label.ilike(search_query)
        )
    ).order_by(Application.last_updated.desc()).offset(skip).limit(limit).all()
