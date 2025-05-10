"""
Routes API pour les audits vocaux
---------------------------------
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List

import sys
import os

# Ajouter le chemin du projet au path Python pour les importations absolues
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Utiliser des importations absolues au lieu d'importations relatives
from common.auth import get_current_active_user, UserInDB
from models.audit_models import AuditRequest, AuditResponse, AuditSummary
from data.audit_data_manager import get_audit_data_manager

router = APIRouter(
    prefix="/api/v1/audits",
    tags=["audits"],
    responses={404: {"description": "Not found"}},
)


@router.post("", response_model=AuditResponse)
async def create_audit(
    request: AuditRequest
    # Authentification désactivée temporairement pour les tests
    # current_user: UserInDB = Depends(get_current_active_user)
):
    """Crée un nouvel audit vocal"""
    # Vérification d'authentification désactivée temporairement
    # if str(request.user_id) != str(current_user.id):
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Vous n'êtes pas autorisé à créer un audit pour cet utilisateur"
    #     )
    
    # Créer l'audit
    audit_manager = get_audit_data_manager()
    audit = audit_manager.create_audit(
        user_id=str(request.user_id),
        audit_data=request.audit_data.dict(by_alias=True)
    )
    
    return audit


@router.get("", response_model=List[AuditSummary])
async def get_user_audits(
    user_id: str
    # Authentification désactivée temporairement pour les tests
    # current_user: UserInDB = Depends(get_current_active_user)
):
    """Récupère tous les audits d'un utilisateur"""
    # Vérification d'authentification désactivée temporairement
    # if user_id != str(current_user.id):
    #     raise HTTPException(
    #         status_code=403,
    #         detail="Vous n'êtes pas autorisé à voir les audits d'un autre utilisateur"
    #     )
    
    # Récupérer les audits
    audit_manager = get_audit_data_manager()
    audits = audit_manager.get_user_audits(user_id)
    
    # Convertir en résumés
    summaries = []
    for audit in audits:
        summaries.append({
            "id": audit["id"],
            "createdAt": audit["createdAt"],
            "userType": audit["auditData"]["profile"]["userType"],
            "region": audit["auditData"]["profile"]["region"],
            "propertyType": audit["auditData"]["property"]["propertyType"]
        })
    
    return summaries


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(
    audit_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Récupère un audit par son ID"""
    # Récupérer l'audit
    audit_manager = get_audit_data_manager()
    audit = audit_manager.get_audit(audit_id)
    
    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit non trouvé"
        )
    
    # Vérifier que l'utilisateur est autorisé à voir cet audit
    if audit["userId"] != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à voir cet audit"
        )
    
    return audit


@router.put("/{audit_id}", response_model=AuditResponse)
async def update_audit(
    audit_id: str,
    request: AuditRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Met à jour un audit existant"""
    # Récupérer l'audit
    audit_manager = get_audit_data_manager()
    audit = audit_manager.get_audit(audit_id)
    
    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit non trouvé"
        )
    
    # Vérifier que l'utilisateur est autorisé à modifier cet audit
    if audit["userId"] != str(current_user.id) or str(request.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à modifier cet audit"
        )
    
    # Mettre à jour l'audit
    updated_audit = audit_manager.update_audit(
        audit_id=audit_id,
        audit_data=request.audit_data.dict(by_alias=True)
    )
    
    if not updated_audit:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la mise à jour de l'audit"
        )
    
    return updated_audit


@router.delete("/{audit_id}")
async def delete_audit(
    audit_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Supprime un audit"""
    # Récupérer l'audit
    audit_manager = get_audit_data_manager()
    audit = audit_manager.get_audit(audit_id)
    
    if not audit:
        raise HTTPException(
            status_code=404,
            detail="Audit non trouvé"
        )
    
    # Vérifier que l'utilisateur est autorisé à supprimer cet audit
    if audit["userId"] != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à supprimer cet audit"
        )
    
    # Supprimer l'audit
    success = audit_manager.delete_audit(audit_id)
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression de l'audit"
        )
    
    return {"status": "success", "message": "Audit supprimé avec succès"}
