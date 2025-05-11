"""
Module de suivi des demandes de subvention
-----------------------------------------
Ce module permet de suivre l'état d'avancement des demandes de subvention,
de gérer les notifications et d'enregistrer l'historique des changements.
"""

import os
import uuid
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field, UUID4

from subsidy_db import Subsidy, get_subsidy_database


class ApplicationStatus(str, Enum):
    """Statut d'une demande de subvention"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAYMENT_IN_PROGRESS = "payment_in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentStatus(BaseModel):
    """Statut d'un document pour une demande"""
    document_id: str
    name: str
    type: str
    submitted: bool = False
    validated: bool = False
    comments: Optional[str] = None
    submission_date: Optional[datetime] = None


class ApplicationNote(BaseModel):
    """Note sur une demande de subvention"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    application_id: str
    date: datetime = Field(default_factory=datetime.now)
    author: str
    content: str
    is_internal: bool = False


class ApplicationHistoryEntry(BaseModel):
    """Entrée dans l'historique d'une demande"""
    date: datetime = Field(default_factory=datetime.now)
    status: ApplicationStatus
    comment: Optional[str] = None
    notification_sent: bool = False


class SubsidyApplication(BaseModel):
    """Demande de subvention"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    subsidy_id: str
    recommendation_id: Optional[str] = None
    creation_date: datetime = Field(default_factory=datetime.now)
    submission_date: Optional[datetime] = None
    last_update_date: datetime = Field(default_factory=datetime.now)
    status: ApplicationStatus = ApplicationStatus.DRAFT
    form_data: Dict[str, Any] = Field(default_factory=dict)
    documents: List[DocumentStatus] = Field(default_factory=list)
    history: List[ApplicationHistoryEntry] = Field(default_factory=list)
    notes: List[ApplicationNote] = Field(default_factory=list)
    estimated_response_date: Optional[datetime] = None
    amount_requested: Optional[float] = None
    amount_approved: Optional[float] = None
    payment_date: Optional[datetime] = None


class ApplicationTracker:
    """Gestionnaire de suivi des demandes de subvention"""
    
    def __init__(self):
        """Initialisation du gestionnaire de suivi"""
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.applications_dir = os.path.join(self.data_dir, "applications")
        os.makedirs(self.applications_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        self.subsidy_db = get_subsidy_database()
    
    def create_application(
        self,
        user_id: str,
        subsidy_id: str,
        recommendation_id: Optional[str] = None,
        form_data: Optional[Dict[str, Any]] = None
    ) -> SubsidyApplication:
        """
        Crée une nouvelle demande de subvention
        
        Args:
            user_id: ID de l'utilisateur
            subsidy_id: ID de la subvention
            recommendation_id: ID de la recommandation (optionnel)
            form_data: Données du formulaire (optionnel)
            
        Returns:
            Nouvelle demande de subvention
        """
        # Récupérer la subvention
        subsidy = self.subsidy_db.get_subsidy_by_id(subsidy_id)
        if not subsidy:
            raise ValueError(f"Subvention avec ID {subsidy_id} non trouvée")
        
        # Créer une nouvelle demande
        application = SubsidyApplication(
            user_id=user_id,
            subsidy_id=subsidy_id,
            recommendation_id=recommendation_id,
            form_data=form_data or {}
        )
        
        # Ajouter l'entrée initiale dans l'historique
        application.history.append(
            ApplicationHistoryEntry(
                status=ApplicationStatus.DRAFT,
                comment="Création de la demande"
            )
        )
        
        # Ajouter les documents requis
        if subsidy.required_documents:
            for doc in subsidy.required_documents:
                application.documents.append(
                    DocumentStatus(
                        document_id=str(uuid.uuid4()),
                        name=doc.description,
                        type=doc.type.value,
                        submitted=False,
                        validated=False
                    )
                )
        
        # Calculer le montant demandé si possible
        if "project" in application.form_data and "estimated_cost" in application.form_data["project"]:
            estimated_cost = application.form_data["project"]["estimated_cost"]
            if isinstance(estimated_cost, (int, float)) and estimated_cost > 0:
                if subsidy.percentage:
                    application.amount_requested = min(
                        estimated_cost * (subsidy.percentage / 100),
                        subsidy.max_amount or float('inf')
                    )
                else:
                    application.amount_requested = subsidy.max_amount
        
        # Sauvegarder la demande
        self._save_application(application)
        
        return application
    
    def update_application(
        self,
        application_id: str,
        form_data: Optional[Dict[str, Any]] = None,
        status: Optional[ApplicationStatus] = None,
        comment: Optional[str] = None
    ) -> SubsidyApplication:
        """
        Met à jour une demande existante
        
        Args:
            application_id: ID de la demande
            form_data: Nouvelles données de formulaire (optionnel)
            status: Nouveau statut (optionnel)
            comment: Commentaire sur la mise à jour (optionnel)
            
        Returns:
            Demande mise à jour
        """
        # Récupérer la demande existante
        application = self.get_application(application_id)
        if not application:
            raise ValueError(f"Demande avec ID {application_id} non trouvée")
        
        # Mettre à jour les données du formulaire si fournies
        if form_data:
            application.form_data.update(form_data)
        
        # Mettre à jour le statut si fourni
        old_status = application.status
        if status and status != old_status:
            application.status = status
            
            # Ajouter une entrée dans l'historique
            application.history.append(
                ApplicationHistoryEntry(
                    status=status,
                    comment=comment or f"Changement de statut: {old_status} → {status}"
                )
            )
            
            # Mettre à jour les dates spécifiques au statut
            if status == ApplicationStatus.SUBMITTED and not application.submission_date:
                application.submission_date = datetime.now()
                
                # Estimer la date de réponse
                subsidy = self.subsidy_db.get_subsidy_by_id(application.subsidy_id)
                if subsidy and subsidy.typical_processing_time_days:
                    application.estimated_response_date = (
                        datetime.now() + timedelta(days=subsidy.typical_processing_time_days)
                    )
        
        # Mettre à jour la date de dernière modification
        application.last_update_date = datetime.now()
        
        # Sauvegarder les changements
        self._save_application(application)
        
        return application
    
    def update_document_status(
        self,
        application_id: str,
        document_id: str,
        submitted: Optional[bool] = None,
        validated: Optional[bool] = None,
        comments: Optional[str] = None
    ) -> SubsidyApplication:
        """
        Met à jour le statut d'un document
        
        Args:
            application_id: ID de la demande
            document_id: ID du document
            submitted: Indique si le document a été soumis
            validated: Indique si le document a été validé
            comments: Commentaires sur le document
            
        Returns:
            Demande mise à jour
        """
        # Récupérer la demande
        application = self.get_application(application_id)
        if not application:
            raise ValueError(f"Demande avec ID {application_id} non trouvée")
        
        # Trouver le document
        document = next((doc for doc in application.documents if doc.document_id == document_id), None)
        if not document:
            raise ValueError(f"Document avec ID {document_id} non trouvé dans la demande {application_id}")
        
        # Mettre à jour les champs
        if submitted is not None:
            document.submitted = submitted
            if submitted and not document.submission_date:
                document.submission_date = datetime.now()
        
        if validated is not None:
            document.validated = validated
        
        if comments is not None:
            document.comments = comments
        
        # Mettre à jour la date de dernière modification
        application.last_update_date = datetime.now()
        
        # Sauvegarder les changements
        self._save_application(application)
        
        return application
    
    def add_note(
        self,
        application_id: str,
        author: str,
        content: str,
        is_internal: bool = False
    ) -> ApplicationNote:
        """
        Ajoute une note à une demande
        
        Args:
            application_id: ID de la demande
            author: Auteur de la note
            content: Contenu de la note
            is_internal: Indique si la note est interne (non visible par l'utilisateur)
            
        Returns:
            Note ajoutée
        """
        # Récupérer la demande
        application = self.get_application(application_id)
        if not application:
            raise ValueError(f"Demande avec ID {application_id} non trouvée")
        
        # Créer la note
        note = ApplicationNote(
            application_id=application_id,
            author=author,
            content=content,
            is_internal=is_internal
        )
        
        # Ajouter la note à la demande
        application.notes.append(note)
        
        # Mettre à jour la date de dernière modification
        application.last_update_date = datetime.now()
        
        # Sauvegarder les changements
        self._save_application(application)
        
        return note
    
    def get_application(self, application_id: str) -> Optional[SubsidyApplication]:
        """
        Récupère une demande par son ID
        
        Args:
            application_id: ID de la demande
            
        Returns:
            Demande de subvention ou None si non trouvée
        """
        try:
            file_path = os.path.join(self.applications_dir, f"{application_id}.json")
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return SubsidyApplication(**data)
            
            return None
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération de la demande {application_id}: {str(e)}")
            return None
    
    def get_user_applications(self, user_id: str) -> List[SubsidyApplication]:
        """
        Récupère toutes les demandes d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des demandes de l'utilisateur
        """
        applications = []
        
        try:
            for filename in os.listdir(self.applications_dir):
                if not filename.endswith('.json'):
                    continue
                
                file_path = os.path.join(self.applications_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('user_id') == user_id:
                    applications.append(SubsidyApplication(**data))
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des demandes de l'utilisateur {user_id}: {str(e)}")
        
        return applications
    
    def get_application_deadlines(self, application_id: str) -> Dict[str, Any]:
        """
        Récupère les échéances importantes pour une demande
        
        Args:
            application_id: ID de la demande
            
        Returns:
            Dictionnaire des échéances importantes
        """
        # Récupérer la demande
        application = self.get_application(application_id)
        if not application:
            raise ValueError(f"Demande avec ID {application_id} non trouvée")
        
        # Récupérer la subvention
        subsidy = self.subsidy_db.get_subsidy_by_id(application.subsidy_id)
        
        # Initialiser les échéances
        deadlines = {
            "submission_deadline": None,
            "estimated_response_date": application.estimated_response_date,
            "document_deadlines": {},
            "next_action": None,
            "days_remaining": None
        }
        
        # Déterminer la prochaine action en fonction du statut
        if application.status == ApplicationStatus.DRAFT:
            deadlines["next_action"] = "Soumettre la demande"
            
            # Vérifier les documents manquants
            missing_docs = [doc.name for doc in application.documents if not doc.submitted]
            if missing_docs:
                deadlines["next_action"] = f"Soumettre les documents manquants : {', '.join(missing_docs)}"
        
        elif application.status == ApplicationStatus.ADDITIONAL_INFO_REQUIRED:
            deadlines["next_action"] = "Fournir les informations supplémentaires demandées"
        
        elif application.status == ApplicationStatus.UNDER_REVIEW:
            deadlines["next_action"] = "Attendre la réponse de l'administration"
            
            if application.estimated_response_date:
                delta = application.estimated_response_date - datetime.now()
                deadlines["days_remaining"] = max(0, delta.days)
        
        # Inclure les dates spécifiques de la subvention si disponibles
        if subsidy and hasattr(subsidy, "deadline_date") and subsidy.deadline_date:
            deadline_date = subsidy.deadline_date
            deadlines["submission_deadline"] = deadline_date
            
            if application.status == ApplicationStatus.DRAFT:
                delta = deadline_date - datetime.now()
                deadlines["days_remaining"] = max(0, delta.days)
        
        return deadlines
    
    def _save_application(self, application: SubsidyApplication) -> None:
        """
        Sauvegarde une demande dans un fichier
        
        Args:
            application: Demande à sauvegarder
        """
        try:
            file_path = os.path.join(self.applications_dir, f"{application.id}.json")
            
            # Convertir la demande en dictionnaire
            data = application.dict()
            
            # Convertir les dates en chaînes
            self._convert_dates_to_strings(data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la demande {application.id}: {str(e)}")
    
    def _convert_dates_to_strings(self, data: Dict[str, Any]) -> None:
        """
        Convertit toutes les dates d'un dictionnaire en chaînes
        
        Args:
            data: Dictionnaire à convertir
        """
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                self._convert_dates_to_strings(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._convert_dates_to_strings(item)


# Instance globale du gestionnaire de suivi
application_tracker = ApplicationTracker()

def get_application_tracker() -> ApplicationTracker:
    """
    Récupère l'instance globale du gestionnaire de suivi
    
    Returns:
        Instance du gestionnaire de suivi
    """
    return application_tracker
