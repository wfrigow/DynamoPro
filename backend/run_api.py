"""
Script pour démarrer l'API avec tous les endpoints nécessaires
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Ajouter le chemin du projet au path Python
sys.path.append(os.path.join(os.path.dirname(__file__), "subsidy"))

# Importer les modules nécessaires
from subsidy.api_routes import router as subsidy_router
from subsidy.common.auth import get_current_active_user, UserInDB
from subsidy.models.audit_models import AuditRequest, AuditResponse, AuditSummary
from subsidy.data.audit_data_manager import get_audit_data_manager
from subsidy.integrations.recommendation_engine import get_recommendation_engine

# Créer l'application FastAPI
app = FastAPI(title="DynamoPro API")

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes pour les subventions
app.include_router(subsidy_router)

# Initialiser le moteur de recommandation
recommendation_engine = get_recommendation_engine()

# Définir les routes pour les audits
@app.post("/api/v1/audits", response_model=AuditResponse)
async def create_audit(
    request: AuditRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Crée un nouvel audit vocal"""
    # Vérifier que l'utilisateur est autorisé à créer un audit
    if str(request.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à créer un audit pour un autre utilisateur"
        )
    
    # Récupérer le gestionnaire de données d'audit
    audit_manager = get_audit_data_manager()
    
    # Créer l'audit
    audit = audit_manager.create_audit(
        user_id=str(request.user_id),
        audit_data=request.audit_data.dict(by_alias=True)
    )
    
    return audit

@app.get("/api/v1/audits", response_model=list[AuditSummary])
async def get_audits(
    user_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Récupère les audits pour un utilisateur spécifique"""
    # Vérifier que l'utilisateur est autorisé à récupérer les audits
    if user_id != str(current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à récupérer les audits d'un autre utilisateur"
        )
    
    # Récupérer le gestionnaire de données d'audit
    audit_manager = get_audit_data_manager()
    
    # Récupérer les audits
    audits = audit_manager.get_audits_for_user(user_id)
    
    return audits

@app.post("/api/v1/detailed-recommendations")
async def generate_detailed_recommendations(
    audit_data: dict,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Génère des recommandations détaillées basées sur les données d'audit"""
    recommendations = await recommendation_engine.generate_recommendations(audit_data)
    return recommendations

if __name__ == "__main__":
    # Démarrer l'application
    uvicorn.run("run_api:app", host="0.0.0.0", port=8023, reload=True)
