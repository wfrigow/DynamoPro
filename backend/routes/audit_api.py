"""
Module pour gérer les endpoints d'audit (sans préfixe v1)
Ce module fournit des endpoints compatibles avec le frontend
"""

import os
import json
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

# Import des modèles et dépendances de la base de données
from backend.standalone_api import get_db, Audit, AuditSchema, AuditCreate

router = APIRouter(tags=["Audits"])

# Modèles Pydantic pour les réponses d'API attendues par le frontend
class AuditSummary(BaseModel):
    id: str
    createdAt: str  # Format ISO attendu par le frontend
    userType: str = "individual"
    region: str = "wallonie"
    propertyType: str = "apartment"

class BackendProfileData(BaseModel):
    userType: str = "individual"
    region: str = "wallonie"
    additionalInfo: Optional[Dict[str, Any]] = Field(default_factory=dict)

class BackendConsumptionData(BaseModel):
    electricityUsage: float = 3500.0
    gasUsage: bool = True
    gasConsumption: float = 15000.0
    additionalInfo: Optional[Dict[str, Any]] = Field(default_factory=dict)

class BackendPropertyData(BaseModel):
    propertyType: str = "apartment"
    area: float = 95.0
    constructionYear: int = 1998
    insulationStatus: str = "medium"
    additionalInfo: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UserAuditData(BaseModel):
    profile: BackendProfileData
    consumption: BackendConsumptionData
    property: BackendPropertyData

class FullAuditResponse(BaseModel):
    id: str
    userId: str
    createdAt: str  # Format ISO attendu par le frontend
    updatedAt: str  # Format ISO attendu par le frontend
    auditData: UserAuditData

# Données de démonstration pour simuler des audits quand la base de données est vide
DEMO_AUDIT_DATA = UserAuditData(
    profile=BackendProfileData(
        userType="individual",
        region="wallonie",
        additionalInfo={}
    ),
    consumption=BackendConsumptionData(
        electricityUsage=3500.0,
        gasUsage=True,
        gasConsumption=15000.0,
        additionalInfo={}
    ),
    property=BackendPropertyData(
        propertyType="apartment",
        area=95.0,
        constructionYear=1998,
        insulationStatus="medium",
        additionalInfo={}
    )
)

def get_or_create_demo_audit(db: Session, user_id: str) -> AuditSchema:
    """Récupère ou crée un audit de démonstration pour un utilisateur donné"""
    # Vérifier s'il existe déjà un audit pour cet utilisateur
    details = {
        "userId": user_id,
        "auditData": DEMO_AUDIT_DATA.model_dump()
    }
    
    # Convertir en JSON
    details_json = json.dumps(details)
    
    # Créer un nouvel audit de démonstration
    demo_audit = Audit(
        event_name=f"demo_audit_{user_id}",
        details=details_json
    )
    
    db.add(demo_audit)
    db.commit()
    db.refresh(demo_audit)
    
    return demo_audit

# Endpoint principal pour obtenir les audits d'un utilisateur spécifique (API v1)
@router.get("/api/v1/audits", response_model=List[AuditSummary])
async def get_user_audits_v1(
    user_id: str = Query(..., description="ID de l'utilisateur"),
    db: Session = Depends(get_db)
):
    """Endpoint API v1 pour récupérer la liste des audits d'un utilisateur"""
    return await _get_user_audits_impl(user_id, db)


# Version sans préfixe v1 pour compatibilité avec le frontend
@router.get("/api/audits", response_model=List[AuditSummary])
async def get_user_audits(
    user_id: str = Query(..., description="ID de l'utilisateur"),
    db: Session = Depends(get_db)
):
    """Version sans préfixe v1 pour la compatibilité avec le frontend"""
    return await _get_user_audits_impl(user_id, db)


# Implémentation commune pour éviter la duplication de code
async def _get_user_audits_impl(
    user_id: str,
    db: Session
):
    """Récupère la liste des audits pour un utilisateur spécifique"""
    try:
        # Rechercher les audits avec l'ID utilisateur dans les détails
        audits = db.query(Audit).filter(Audit.details.contains(f'"userId":"{user_id}"')).all()
        
        # Si aucun audit trouvé, créer un audit de démonstration
        if not audits:
            demo_audit = get_or_create_demo_audit(db, user_id)
            audits = [demo_audit]
        
        # Convertir les audits au format attendu par le frontend
        result = []
        for audit in audits:
            # Extraire l'ID et la date de création
            audit_id = str(audit.id)
            created_at = audit.timestamp.isoformat()
            
            # Extraire les détails s'ils sont disponibles
            user_type = "individual"
            region = "wallonie"
            property_type = "apartment"
            
            if audit.details and isinstance(audit.details, str):
                try:
                    details_dict = json.loads(audit.details)
                    if "auditData" in details_dict:
                        audit_data = details_dict["auditData"]
                        if "profile" in audit_data:
                            user_type = audit_data["profile"].get("userType", user_type)
                            region = audit_data["profile"].get("region", region)
                        if "property" in audit_data:
                            property_type = audit_data["property"].get("propertyType", property_type)
                except Exception as e:
                    print(f"Erreur lors du décodage des détails de l'audit {audit_id}: {str(e)}")
            
            # Créer un résumé d'audit
            summary = AuditSummary(
                id=audit_id,
                createdAt=created_at,
                userType=user_type,
                region=region,
                propertyType=property_type
            )
            result.append(summary)
        
        return result
    
    except Exception as e:
        print(f"Erreur lors de la récupération des audits pour l'utilisateur {user_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des audits: {str(e)}"
        )

# Endpoint principal pour obtenir un audit spécifique par son ID (API v1)
@router.get("/api/v1/audits/{audit_id}", response_model=FullAuditResponse)
async def get_audit_by_id_v1(audit_id: str, db: Session = Depends(get_db)):
    """Endpoint API v1 pour récupérer les détails d'un audit spécifique"""
    return await _get_audit_by_id_impl(audit_id, db)


# Version sans préfixe v1 pour compatibilité avec le frontend
@router.get("/api/audits/{audit_id}", response_model=FullAuditResponse)
async def get_audit_by_id(audit_id: str, db: Session = Depends(get_db)):
    """Version sans préfixe v1 pour la compatibilité avec le frontend"""
    return await _get_audit_by_id_impl(audit_id, db)


# Implémentation commune pour éviter la duplication de code
async def _get_audit_by_id_impl(
    audit_id: str,
    db: Session
):
    """Récupère les détails complets d'un audit spécifique"""
    try:
        # Convertir l'ID en entier si possible
        try:
            numeric_id = int(audit_id)
            audit = db.query(Audit).filter(Audit.id == numeric_id).first()
        except ValueError:
            # Si l'ID n'est pas un nombre, utiliser une valeur par défaut
            print(f"ID d'audit non numérique: {audit_id}, utilisant l'audit 1")
            audit = db.query(Audit).filter(Audit.id == 1).first()
        
        # Si aucun audit trouvé, créer une réponse de démonstration
        if not audit:
            print(f"Aucun audit trouvé avec l'ID {audit_id}, retournant des données de démonstration")
            return FullAuditResponse(
                id=audit_id,
                userId="user-1",
                createdAt=datetime.now().isoformat(),
                updatedAt=datetime.now().isoformat(),
                auditData=DEMO_AUDIT_DATA
            )
        
        # Extraire les détails de l'audit
        details_dict = {}
        user_id = "user-1"
        audit_data = DEMO_AUDIT_DATA
        
        if audit.details and isinstance(audit.details, str):
            try:
                details_dict = json.loads(audit.details)
                if "userId" in details_dict:
                    user_id = details_dict["userId"]
                if "auditData" in details_dict:
                    try:
                        # Tenter de convertir les données d'audit au format attendu
                        audit_data = UserAuditData(**details_dict["auditData"])
                    except Exception as e:
                        print(f"Erreur lors de la conversion des données d'audit: {str(e)}")
                        # Conserver les données de démonstration
            except Exception as e:
                print(f"Erreur lors du décodage des détails de l'audit {audit_id}: {str(e)}")
        
        # Créer la réponse complète
        response = FullAuditResponse(
            id=str(audit.id),
            userId=user_id,
            createdAt=audit.timestamp.isoformat(),
            updatedAt=audit.timestamp.isoformat(),  # Utiliser la même date pour updated si non disponible
            auditData=audit_data
        )
        
        return response
    
    except Exception as e:
        print(f"Erreur lors de la récupération de l'audit {audit_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération de l'audit: {str(e)}"
        )
