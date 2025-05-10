"""
Modèles de données pour les audits vocaux
-----------------------------------------
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, UUID4


class ProfileData(BaseModel):
    """Modèle pour les données de profil collectées lors de l'audit"""
    user_type: str = Field(default="", alias="userType")
    region: str = Field(default="")
    additional_info: Optional[Dict[str, Any]] = Field(default=None, alias="additionalInfo")


class ConsumptionData(BaseModel):
    """Modèle pour les données de consommation collectées lors de l'audit"""
    electricity_usage: float = Field(default=0, alias="electricityUsage")
    gas_usage: bool = Field(default=False, alias="gasUsage")
    gas_consumption: float = Field(default=0, alias="gasConsumption")
    additional_info: Optional[Dict[str, Any]] = Field(default=None, alias="additionalInfo")


class PropertyData(BaseModel):
    """Modèle pour les données de propriété collectées lors de l'audit"""
    property_type: str = Field(default="", alias="propertyType")
    area: float = Field(default=0)
    construction_year: int = Field(default=0, alias="constructionYear")
    insulation_status: str = Field(default="", alias="insulationStatus")
    additional_info: Optional[Dict[str, Any]] = Field(default=None, alias="additionalInfo")


class AuditData(BaseModel):
    """Modèle pour l'ensemble des données d'audit"""
    profile: ProfileData
    consumption: ConsumptionData
    property: PropertyData


class AuditRequest(BaseModel):
    """Modèle pour la requête de sauvegarde d'un audit"""
    user_id: UUID4 = Field(..., alias="userId")
    audit_data: AuditData = Field(..., alias="auditData")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "userId": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "auditData": {
                    "profile": {
                        "userType": "individual",
                        "region": "wallonie"
                    },
                    "consumption": {
                        "electricityUsage": 3500,
                        "gasUsage": True,
                        "gasConsumption": 15000
                    },
                    "property": {
                        "propertyType": "house",
                        "area": 150,
                        "constructionYear": 1985,
                        "insulationStatus": "partial"
                    }
                }
            }
        }


class AuditResponse(BaseModel):
    """Modèle pour la réponse à une requête d'audit"""
    id: str
    user_id: str = Field(..., alias="userId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")
    audit_data: AuditData = Field(..., alias="auditData")
    
    class Config:
        populate_by_name = True


class AuditSummary(BaseModel):
    """Modèle pour le résumé d'un audit"""
    id: str
    created_at: datetime = Field(..., alias="createdAt")
    user_type: str = Field(..., alias="userType")
    region: str
    property_type: str = Field(..., alias="propertyType")
    
    class Config:
        populate_by_name = True
