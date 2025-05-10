"""
Modèles de données pour les applications de subventions
----------------------------------------------------
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4, EmailStr


class Applicant(BaseModel):
    """Modèle pour les informations du demandeur"""
    name: str
    email: EmailStr
    phone: str
    address: str
    user_type: str = Field(..., alias="userType")
    additional_info: Optional[Dict[str, Any]] = Field(None, alias="additionalInfo")


class Property(BaseModel):
    """Modèle pour les informations sur la propriété"""
    address: str
    type: str
    year_built: Optional[str] = Field(None, alias="yearBuilt")
    additional_info: Optional[Dict[str, Any]] = Field(None, alias="additionalInfo")


class Project(BaseModel):
    """Modèle pour les informations sur le projet"""
    description: str
    estimated_cost: float = Field(..., alias="estimatedCost")
    estimated_completion_date: Optional[str] = Field(None, alias="estimatedCompletionDate")
    work_started: Optional[str] = Field(None, alias="workStarted")
    contractor_selected: Optional[str] = Field(None, alias="contractorSelected")
    contractor_name: Optional[str] = Field(None, alias="contractorName")
    additional_info: Optional[Dict[str, Any]] = Field(None, alias="additionalInfo")


class BankDetails(BaseModel):
    """Modèle pour les informations bancaires"""
    account_holder: str = Field(..., alias="accountHolder")
    iban: str
    additional_info: Optional[Dict[str, Any]] = Field(None, alias="additionalInfo")


class ApplicationDocument(BaseModel):
    """Modèle pour les documents d'une application"""
    id: str
    name: str
    status: str  # pending, validated, rejected, requested
    upload_date: Optional[datetime] = Field(None, alias="uploadDate")
    validation_date: Optional[datetime] = Field(None, alias="validationDate")
    comments: Optional[str] = None
    size: Optional[int] = None


class ApplicationNote(BaseModel):
    """Modèle pour les notes d'une application"""
    id: str
    date: datetime
    author: str
    author_type: str = Field(..., alias="authorType")  # admin, user
    content: str


class ApplicationHistory(BaseModel):
    """Modèle pour l'historique d'une application"""
    id: str
    date: datetime
    status: str
    description: str


class ApplicationCreate(BaseModel):
    """Modèle pour la création d'une application"""
    applicant: Applicant
    property: Property
    project: Project
    bank_details: BankDetails = Field(..., alias="bankDetails")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "applicant": {
                    "name": "Jean Dupont",
                    "email": "jean.dupont@example.com",
                    "phone": "+32 470 12 34 56",
                    "address": "Rue de la Science 123, 1040 Bruxelles",
                    "userType": "individual"
                },
                "property": {
                    "address": "Rue de la Science 123, 1040 Bruxelles",
                    "type": "house",
                    "yearBuilt": "1975"
                },
                "project": {
                    "description": "Isolation de la toiture avec des matériaux écologiques",
                    "estimatedCost": 5000,
                    "estimatedCompletionDate": "2025-09-15",
                    "workStarted": "no",
                    "contractorSelected": "yes",
                    "contractorName": "Iso-Pro SPRL"
                },
                "bankDetails": {
                    "accountHolder": "Jean Dupont",
                    "iban": "BE68 5390 0754 7034"
                }
            }
        }


class ApplicationDraftCreate(BaseModel):
    """Modèle pour la création d'un brouillon d'application"""
    applicant: Optional[Applicant] = None
    property: Optional[Property] = None
    project: Optional[Project] = None
    bank_details: Optional[BankDetails] = Field(None, alias="bankDetails")
    
    class Config:
        populate_by_name = True


class ApplicationNoteCreate(BaseModel):
    """Modèle pour la création d'une note d'application"""
    content: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "J'ai besoin d'informations supplémentaires concernant les matériaux utilisés."
            }
        }


class ApplicationResponse(BaseModel):
    """Modèle pour la réponse d'une application"""
    id: str
    subsidy_id: str = Field(..., alias="subsidyId")
    status: str
    status_label: str = Field(..., alias="statusLabel")
    submission_date: Optional[datetime] = Field(None, alias="submissionDate")
    last_updated: datetime = Field(..., alias="lastUpdated")
    reference_number: Optional[str] = Field(None, alias="referenceNumber")
    applicant: Applicant
    property: Property
    project: Project
    bank_details: Optional[BankDetails] = Field(None, alias="bankDetails")
    subsidy: Dict[str, Any]
    documents: List[ApplicationDocument]
    notes: List[ApplicationNote]
    history: List[ApplicationHistory]
    next_steps: Optional[List[str]] = Field(None, alias="nextSteps")
    
    class Config:
        populate_by_name = True


class ApplicationDraftResponse(BaseModel):
    """Modèle pour la réponse d'un brouillon d'application"""
    id: str
    subsidy_id: str = Field(..., alias="subsidyId")
    status: str
    last_updated: datetime = Field(..., alias="lastUpdated")
    applicant: Optional[Applicant] = None
    property: Optional[Property] = None
    project: Optional[Project] = None
    bank_details: Optional[BankDetails] = Field(None, alias="bankDetails")
    
    class Config:
        populate_by_name = True


class DocumentUploadResponse(BaseModel):
    """Modèle pour la réponse d'un téléchargement de document"""
    id: str
    name: str
    status: str
    upload_date: datetime = Field(..., alias="uploadDate")
    size: int
    
    class Config:
        populate_by_name = True
