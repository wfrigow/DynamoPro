"""
Module de traitement des documents pour les demandes de subvention
------------------------------------------------------------------
Ce module fournit des outils pour extraire des informations pertinentes
des documents soumis par les utilisateurs et valider leur conformité
avec les exigences des subventions.
"""

import os
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.ai_utils import OCRService, LLMService
from subsidy_db import (
    Subsidy, SubsidyDocumentType, RequiredDocument, SubsidyConditionType
)


class DocumentValidationStatus(str, Enum):
    """Statut de validation d'un document"""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_MORE_INFO = "needs_more_info"


class DocumentMetadata(BaseModel):
    """Métadonnées d'un document extrait"""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_type: SubsidyDocumentType
    file_name: str
    upload_date: datetime = Field(default_factory=datetime.now)
    mime_type: str
    file_size: int
    validation_status: DocumentValidationStatus = DocumentValidationStatus.PENDING
    validation_message: Optional[str] = None
    extracted_data: Dict[str, Any] = Field(default_factory=dict)


class DocumentProcessor:
    """Processeur de documents pour les demandes de subvention"""
    
    def __init__(self):
        """Initialise le processeur de documents"""
        self.llm_service = LLMService()
        self.ocr_service = OCRService()
        self.documents_dir = os.path.join(os.path.dirname(__file__), "documents")
        os.makedirs(self.documents_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    async def process_document(
        self,
        file_path: str,
        document_type: SubsidyDocumentType,
        subsidy: Optional[Subsidy] = None
    ) -> DocumentMetadata:
        """
        Traite un document soumis et extrait les informations pertinentes
        
        Args:
            file_path: Chemin du fichier à traiter
            document_type: Type de document
            subsidy: Subvention associée au document (si applicable)
            
        Returns:
            Métadonnées du document avec les informations extraites
        """
        # Récupérer les informations de base du fichier
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        # Déterminer le type MIME (simplifié)
        extension = os.path.splitext(file_name)[1].lower()
        mime_type = self._get_mime_type(extension)
        
        # Initialiser les métadonnées
        metadata = DocumentMetadata(
            document_type=document_type,
            file_name=file_name,
            mime_type=mime_type,
            file_size=file_size
        )
        
        # Extraire le texte du document si c'est un type supporté
        if self._is_ocr_supported(mime_type):
            try:
                extracted_text = await self.ocr_service.extract_text(file_path)
                metadata.extracted_data["text"] = extracted_text
                
                # Extraire les données spécifiques selon le type de document
                extracted_data = await self._extract_specific_data(extracted_text, document_type)
                metadata.extracted_data.update(extracted_data)
                
                # Valider le document
                if subsidy:
                    validation_status, validation_message = await self._validate_document(
                        metadata, document_type, subsidy
                    )
                    metadata.validation_status = validation_status
                    metadata.validation_message = validation_message
            
            except Exception as e:
                self.logger.error(f"Erreur lors du traitement du document {file_name}: {str(e)}")
                metadata.validation_status = DocumentValidationStatus.INVALID
                metadata.validation_message = f"Erreur de traitement: {str(e)}"
        else:
            metadata.validation_status = DocumentValidationStatus.NEEDS_MORE_INFO
            metadata.validation_message = "Type de fichier non supporté pour l'extraction automatique"
        
        return metadata
    
    async def _extract_specific_data(
        self,
        text: str,
        document_type: SubsidyDocumentType
    ) -> Dict[str, Any]:
        """
        Extrait des données spécifiques en fonction du type de document
        
        Args:
            text: Texte extrait du document
            document_type: Type de document
            
        Returns:
            Dictionnaire des données extraites
        """
        extracted_data = {}
        
        # Créer un prompt pour l'extraction de données spécifiques
        prompt = f"""
        Extrait les informations pertinentes du document suivant de type {document_type.value}.
        Le texte du document est:
        
        {text[:1500]}...
        
        Réponds UNIQUEMENT avec un JSON valide contenant les champs extraits pertinents.
        """
        
        system_message = "Tu es un assistant spécialisé dans l'extraction de données à partir de documents administratifs belges."
        
        if document_type == SubsidyDocumentType.INVOICE:
            prompt += """
            Pour une facture, extrait les champs suivants:
            - date: Date de la facture (format YYYY-MM-DD)
            - company_name: Nom de l'entreprise
            - vat_number: Numéro de TVA
            - total_amount: Montant total TTC
            - vat_amount: Montant de la TVA
            - items: Liste des éléments facturés avec leur description et prix
            """
        
        elif document_type == SubsidyDocumentType.IDENTITY:
            prompt += """
            Pour une pièce d'identité, extrait les champs suivants:
            - full_name: Nom complet de la personne
            - id_number: Numéro d'identification
            - birth_date: Date de naissance (format YYYY-MM-DD)
            - issue_date: Date d'émission (format YYYY-MM-DD)
            - expiry_date: Date d'expiration (format YYYY-MM-DD)
            """
            
        elif document_type == SubsidyDocumentType.TECHNICAL_SPEC:
            prompt += """
            Pour une fiche technique, extrait les champs suivants:
            - product_name: Nom du produit
            - manufacturer: Fabricant
            - model: Modèle
            - performance_data: Données de performance (rendement, puissance, etc.)
            - certifications: Certifications mentionnées
            """
            
        elif document_type == SubsidyDocumentType.QUOTE:
            prompt += """
            Pour un devis, extrait les champs suivants:
            - date: Date du devis (format YYYY-MM-DD)
            - company_name: Nom de l'entreprise
            - vat_number: Numéro de TVA
            - total_amount: Montant total TTC
            - vat_amount: Montant de la TVA
            - validity_period: Période de validité du devis (en jours)
            - work_description: Description des travaux
            """
        
        try:
            response = await self.llm_service.generate_response(prompt, system_message)
            
            # Tenter de parser la réponse comme du JSON
            import json
            try:
                extracted_data = json.loads(response)
            except json.JSONDecodeError:
                self.logger.warning(f"Impossible de parser la réponse JSON pour le document de type {document_type}")
                # Extraction manuelle avec des déclencheurs de texte comme solution de repli
                extracted_data = self._fallback_extraction(text, document_type)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des données: {str(e)}")
            extracted_data = {}
        
        return extracted_data
    
    def _fallback_extraction(
        self,
        text: str,
        document_type: SubsidyDocumentType
    ) -> Dict[str, Any]:
        """
        Méthode de repli pour l'extraction de données en cas d'échec de l'IA
        
        Args:
            text: Texte du document
            document_type: Type de document
            
        Returns:
            Données extraites
        """
        extracted_data = {}
        text_lower = text.lower()
        
        # Extraction basique de montants (pour factures, devis)
        if document_type in [SubsidyDocumentType.INVOICE, SubsidyDocumentType.QUOTE]:
            # Recherche de montants (€)
            import re
            amount_matches = re.findall(r'(\d[\d\s,.]*)\s*(?:€|EUR)', text)
            if amount_matches:
                # Nettoyer et convertir le montant
                try:
                    amount_str = amount_matches[-1].replace(' ', '').replace('.', '').replace(',', '.')
                    extracted_data["total_amount"] = float(amount_str)
                except (ValueError, IndexError):
                    pass
        
        # Extraction de dates
        import re
        date_matches = re.findall(r'(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4})', text)
        if date_matches:
            extracted_data["date"] = date_matches[0]
        
        return extracted_data
    
    async def _validate_document(
        self,
        metadata: DocumentMetadata,
        document_type: SubsidyDocumentType,
        subsidy: Subsidy
    ) -> Tuple[DocumentValidationStatus, str]:
        """
        Valide un document par rapport aux exigences d'une subvention
        
        Args:
            metadata: Métadonnées du document
            document_type: Type de document
            subsidy: Subvention associée
            
        Returns:
            Statut de validation et message explicatif
        """
        # Vérifier si le document est requis pour cette subvention
        required_doc = next(
            (doc for doc in subsidy.required_documents if doc.type == document_type), 
            None
        )
        
        if not required_doc:
            return DocumentValidationStatus.VALID, "Document non explicitement requis mais accepté"
        
        # Validation spécifique par type de document
        if document_type == SubsidyDocumentType.TECHNICAL_SPEC:
            # Vérifier si les spécifications techniques répondent aux conditions de la subvention
            for condition in subsidy.conditions:
                if condition.type != SubsidyConditionType.TECHNICAL:
                    continue
                
                # Si la condition a un paramètre technique spécifique
                if condition.technical_parameter and condition.technical_value is not None:
                    param = condition.technical_parameter
                    expected_value = condition.technical_value
                    
                    # Vérifier si la valeur est présente dans les données extraites
                    extracted_performance = metadata.extracted_data.get("performance_data", {})
                    if isinstance(extracted_performance, dict) and param in extracted_performance:
                        actual_value = extracted_performance.get(param)
                        try:
                            actual_value = float(actual_value)
                            
                            # Comparer les valeurs
                            if actual_value < expected_value:
                                return (
                                    DocumentValidationStatus.INVALID,
                                    f"La valeur de {param} ({actual_value}) est inférieure à la valeur minimale requise ({expected_value})"
                                )
                        except (ValueError, TypeError):
                            return (
                                DocumentValidationStatus.NEEDS_MORE_INFO,
                                f"Impossible de valider la valeur de {param}"
                            )
        
        elif document_type == SubsidyDocumentType.INVOICE:
            # Vérifier si la facture contient les éléments nécessaires
            if not metadata.extracted_data.get("company_name"):
                return (
                    DocumentValidationStatus.NEEDS_MORE_INFO,
                    "Le nom de l'entreprise n'a pas pu être extrait de la facture"
                )
            
            if not metadata.extracted_data.get("total_amount"):
                return (
                    DocumentValidationStatus.NEEDS_MORE_INFO,
                    "Le montant total n'a pas pu être extrait de la facture"
                )
        
        # Par défaut, considérer le document comme valide
        return DocumentValidationStatus.VALID, "Document validé avec succès"
    
    def _get_mime_type(self, extension: str) -> str:
        """
        Détermine le type MIME à partir de l'extension du fichier
        
        Args:
            extension: Extension du fichier
            
        Returns:
            Type MIME
        """
        mime_types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        
        return mime_types.get(extension, 'application/octet-stream')
    
    def _is_ocr_supported(self, mime_type: str) -> bool:
        """
        Vérifie si le type MIME est supporté pour l'OCR
        
        Args:
            mime_type: Type MIME du document
            
        Returns:
            True si supporté, False sinon
        """
        supported_mime_types = [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/tiff'
        ]
        
        return mime_type in supported_mime_types


# Instance globale du processeur de documents
document_processor = DocumentProcessor()

def get_document_processor() -> DocumentProcessor:
    """
    Récupère l'instance globale du processeur de documents
    
    Returns:
        Instance du processeur de documents
    """
    return document_processor
