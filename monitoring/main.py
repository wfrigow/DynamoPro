"""
Monitoring Agent pour DynamoPro
-----------------------------
Ce module est responsable du suivi de l'avancement des actions et de la 
vérification des projets complétés.
"""

import logging
import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, UUID4, Field

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.auth import get_current_active_user, UserInDB
from common.config import settings
from common.models import (
    UserProfile, Recommendation, Project, GreenPassport,
    DomainType, UserType, BelgiumRegion
)
from common.ai_utils import LLMService, OCRService

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("monitoring")

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DynamoPro Monitoring Agent",
    description="Agent de suivi et vérification pour DynamoPro",
    version="0.1.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données spécifiques à l'agent
class ProjectProgressUpdate(BaseModel):
    """Mise à jour de l'avancement d'un projet"""
    project_id: UUID4
    user_id: UUID4
    status: str  # planning, in_progress, completed, cancelled
    progress_percentage: Optional[int] = None
    notes: Optional[str] = None
    actual_cost: Optional[float] = None
    completion_date: Optional[datetime] = None

class ProjectVerificationRequest(BaseModel):
    """Requête de vérification d'un projet"""
    project_id: UUID4
    user_id: UUID4
    verification_notes: Optional[str] = None

class ProjectVerificationResponse(BaseModel):
    """Réponse à une requête de vérification"""
    project_id: UUID4
    verification_status: str
    required_documents: List[str]
    next_steps: str

class DocumentVerificationResult(BaseModel):
    """Résultat de la vérification d'un document"""
    document_id: str
    project_id: UUID4
    validation_result: bool
    confidence_score: float
    issues: Optional[List[str]] = None

class GreenPassportRequest(BaseModel):
    """Requête de génération de Passeport Vert"""
    user_id: UUID4

class ProjectSummaryRequest(BaseModel):
    """Requête de résumé des projets d'un utilisateur"""
    user_id: UUID4
    status_filter: Optional[str] = None  # Filtrer par statut si spécifié

class ProjectSummaryResponse(BaseModel):
    """Réponse à une requête de résumé des projets"""
    user_id: UUID4
    projects_count: int
    completed_count: int
    in_progress_count: int
    planning_count: int
    cancelled_count: int
    total_investment: float
    estimated_annual_savings: float
    estimated_co2_reduction: float
    summary: str


# Base de données de projets (pour le MVP, à remplacer par une vraie DB)
PROJECTS_DATABASE = [
    {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "user_id": "user-1",
        "recommendation_id": "rec-1",
        "property_id": "property-1",
        "supplier_id": "supplier-1",
        "status": "completed",
        "start_date": "2025-03-15T00:00:00",
        "completion_date": "2025-04-10T00:00:00",
        "actual_cost": 12500,
        "notes": "Installation réussie de 12 panneaux solaires",
        "verification_status": "verified",
        "verification_date": "2025-04-15T00:00:00",
        "domain": "energy",
        "estimated_annual_savings": 1200,
        "estimated_co2_reduction": 2500
    },
    {
        "id": "c0a80121-9e7a-4b4a-9b96-4c6b5308c30c",
        "user_id": "user-1",
        "recommendation_id": "rec-2",
        "property_id": "property-1",
        "supplier_id": "supplier-2",
        "status": "in_progress",
        "start_date": "2025-05-01T00:00:00",
        "completion_date": None,
        "actual_cost": None,
        "notes": "Travaux d'isolation du toit en cours",
        "verification_status": "pending",
        "verification_date": None,
        "domain": "energy",
        "estimated_annual_savings": 800,
        "estimated_co2_reduction": 1500
    },
    {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "user_id": "user-1",
        "recommendation_id": "rec-3",
        "property_id": "property-1",
        "supplier_id": "supplier-3",
        "status": "planning",
        "start_date": None,
        "completion_date": None,
        "actual_cost": None,
        "notes": "Installation de récupération d'eau de pluie planifiée",
        "verification_status": "pending",
        "verification_date": None,
        "domain": "water",
        "estimated_annual_savings": 350,
        "estimated_co2_reduction": 800
    }
]


class MonitoringService:
    """Service principal de suivi et vérification"""
    
    def __init__(self):
        """Initialise le service de suivi et vérification"""
        self.llm_service = LLMService()
        self.ocr_service = OCRService()
    
    async def get_project(self, project_id: UUID4) -> Dict[str, Any]:
        """Récupère un projet par son ID (stub, à implémenter avec DB)"""
        project = next((p for p in PROJECTS_DATABASE if p["id"] == str(project_id)), None)
        if not project:
            raise HTTPException(status_code=404, detail="Projet non trouvé")
        return project
    
    async def get_user_projects(
        self, 
        user_id: UUID4,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Récupère tous les projets d'un utilisateur, avec filtre optionnel"""
        projects = [p for p in PROJECTS_DATABASE if p["user_id"] == str(user_id)]
        if status_filter:
            projects = [p for p in projects if p["status"] == status_filter]
        return projects
    
    async def update_project_progress(
        self,
        update: ProjectProgressUpdate
    ) -> Dict[str, Any]:
        """Met à jour l'avancement d'un projet"""
        # Récupérer le projet
        project = await self.get_project(update.project_id)
        
        # Vérifier que l'utilisateur est bien le propriétaire du projet
        if project["user_id"] != str(update.user_id):
            raise HTTPException(status_code=403, detail="Accès non autorisé à ce projet")
        
        # Mettre à jour les champs
        project["status"] = update.status
        
        if update.progress_percentage is not None:
            project["progress_percentage"] = update.progress_percentage
        
        if update.notes:
            project["notes"] = update.notes
        
        if update.actual_cost is not None:
            project["actual_cost"] = update.actual_cost
        
        if update.completion_date:
            project["completion_date"] = update.completion_date.isoformat()
        
        # Si le projet est marqué comme complété, mettre à jour les champs correspondants
        if update.status == "completed" and not project.get("completion_date"):
            project["completion_date"] = datetime.utcnow().isoformat()
            
            # Changer le statut de vérification si nécessaire
            if project["verification_status"] == "verified":
                # Si déjà vérifié, ne pas changer
                pass
            else:
                project["verification_status"] = "pending"
        
        # Note: dans une implémentation réelle, on sauvegarderait les modifications en base de données
        
        return project
    
    async def get_verification_requirements(
        self,
        project_id: UUID4,
        user_id: UUID4
    ) -> ProjectVerificationResponse:
        """Récupère les exigences de vérification pour un projet"""
        # Récupérer le projet
        project = await self.get_project(project_id)
        
        # Vérifier que l'utilisateur est bien le propriétaire du projet
        if project["user_id"] != str(user_id):
            raise HTTPException(status_code=403, detail="Accès non autorisé à ce projet")
        
        # Déterminer les documents requis en fonction du domaine et du type de projet
        required_documents = ["Facture du fournisseur", "Photos du projet terminé"]
        
        if project["domain"] == "energy":
            if "panneaux solaires" in project.get("notes", "").lower():
                required_documents.extend([
                    "Certificat d'installation des panneaux",
                    "Photo du compteur/onduleur",
                    "Déclaration de conformité électrique"
                ])
            elif "isolation" in project.get("notes", "").lower():
                required_documents.extend([
                    "Fiches techniques des matériaux utilisés",
                    "Photos avant/après des zones isolées"
                ])
            elif "pompe à chaleur" in project.get("notes", "").lower():
                required_documents.extend([
                    "Certificat d'installation de la pompe à chaleur",
                    "Manuel technique de l'équipement",
                    "Preuve de mise en service"
                ])
        
        if project["domain"] == "water":
            if "récupération d'eau" in project.get("notes", "").lower():
                required_documents.extend([
                    "Schéma d'installation du système",
                    "Photo de la citerne installée",
                    "Attestation de conformité sanitaire"
                ])
        
        # Générer les prochaines étapes avec le LLM
        next_steps = await self.generate_verification_steps(project, required_documents)
        
        return ProjectVerificationResponse(
            project_id=project_id,
            verification_status=project["verification_status"],
            required_documents=required_documents,
            next_steps=next_steps
        )
    
    async def generate_verification_steps(
        self,
        project: Dict[str, Any],
        required_documents: List[str]
    ) -> str:
        """Génère les prochaines étapes pour la vérification d'un projet"""
        # Créer le prompt
        prompt = f"""
        Génère une explication concise des étapes nécessaires pour faire vérifier ce projet:
        
        Informations clés:
        - Type de projet: {project.get("notes", "Non spécifié")}
        - Statut actuel: {project["status"]}
        - Statut de vérification: {project["verification_status"]}
        - Documents requis: {', '.join(required_documents)}
        
        Explique le processus étape par étape, de manière claire et pratique. Précise l'importance
        de la vérification pour valider les économies et l'impact écologique, ainsi que pour la
        génération du Passeport Vert.
        """
        
        # Générer les prochaines étapes
        system_message = "Tu es un expert en vérification de projets de durabilité et d'amélioration énergétique."
        next_steps = await self.llm_service.generate_response(prompt, system_message)
        
        return next_steps
    
    async def verify_document(
        self,
        project_id: UUID4,
        document_type: str,
        file: UploadFile
    ) -> DocumentVerificationResult:
        """Vérifie un document soumis pour un projet"""
        # Récupérer le projet
        project = await self.get_project(project_id)
        
        # Sauvegarde temporaire du fichier
        temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())
        
        # Initialiser les variables de résultat
        validation_result = False
        confidence_score = 0.0
        issues = []
        
        try:
            # Logique de vérification selon le type de document
            if document_type == "invoice":
                # Pour le MVP, on simule une vérification de facture
                # À implémenter: vérification réelle avec OCR et LLM
                validation_result = True
                confidence_score = 0.85
            
            elif document_type == "certificate":
                # Pour le MVP, on simule une vérification de certificat
                validation_result = True
                confidence_score = 0.9
            
            elif document_type == "photo":
                # Pour le MVP, on simule une analyse d'image
                # À implémenter: vérification réelle avec Computer Vision
                validation_result = True
                confidence_score = 0.75
                
                # Simulation d'un problème de qualité d'image
                if "test_fail" in file.filename:
                    validation_result = False
                    confidence_score = 0.4
                    issues = ["Image floue ou mal cadrée", "Impossible d'identifier clairement l'installation"]
            
            else:
                # Type de document non reconnu
                validation_result = False
                confidence_score = 0.0
                issues = ["Type de document non reconnu"]
        
        finally:
            # Suppression du fichier temporaire
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        # Création du résultat
        document_id = str(uuid.uuid4())
        
        # Note: dans une implémentation réelle, on sauvegarderait le document et le résultat en base de données
        
        return DocumentVerificationResult(
            document_id=document_id,
            project_id=project_id,
            validation_result=validation_result,
            confidence_score=confidence_score,
            issues=issues if issues else None
        )
    
    async def complete_verification(
        self,
        project_id: UUID4,
        user_id: UUID4,
        verification_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Finalise la vérification d'un projet après soumission des documents"""
        # Récupérer le projet
        project = await self.get_project(project_id)
        
        # Vérifier que l'utilisateur est bien le propriétaire du projet
        if project["user_id"] != str(user_id):
            raise HTTPException(status_code=403, detail="Accès non autorisé à ce projet")
        
        # Dans une implémentation réelle, on vérifierait que tous les documents requis ont été soumis
        # et validés. Pour le MVP, on simule une vérification réussie.
        
        # Mettre à jour le statut de vérification
        project["verification_status"] = "verified"
        project["verification_date"] = datetime.utcnow().isoformat()
        
        if verification_notes:
            if "notes" in project:
                project["notes"] += f"\n\nVérification: {verification_notes}"
            else:
                project["notes"] = f"Vérification: {verification_notes}"
        
        # Note: dans une implémentation réelle, on sauvegarderait les modifications en base de données
        
        return project
    
    async def generate_green_passport(
        self,
        user_id: UUID4
    ) -> GreenPassport:
        """Génère ou met à jour le Passeport Vert de l'utilisateur"""
        # Récupérer tous les projets vérifiés de l'utilisateur
        all_projects = await self.get_user_projects(user_id)
        verified_projects = [p for p in all_projects if p["verification_status"] == "verified"]
        
        if not verified_projects:
            raise HTTPException(
                status_code=400, 
                detail="Aucun projet vérifié trouvé. Au moins un projet vérifié est nécessaire pour le Passeport Vert."
            )
        
        # Calculer les économies et l'impact environnemental
        energy_savings_kwh = 0
        water_savings_m3 = 0
        cost_savings_total = 0
        co2_savings_kg = 0
        
        for project in verified_projects:
            # Estimer les économies sur la base des données du projet
            # Ces calculs seraient plus précis dans une implémentation réelle
            
            # Économies annuelles
            annual_savings = project.get("estimated_annual_savings", 0)
            cost_savings_total += annual_savings
            
            # Économies d'énergie
            if project["domain"] == "energy":
                # Conversion approximative euros -> kWh (à affiner)
                energy_savings_kwh += annual_savings * 5  # ~5 kWh par euro économisé
            
            # Économies d'eau
            if project["domain"] == "water":
                # Conversion approximative euros -> m³ (à affiner)
                water_savings_m3 += annual_savings * 3  # ~3 m³ par euro économisé
            
            # Réduction CO2
            co2_savings_kg += project.get("estimated_co2_reduction", 0)
        
        # Calculer le score total (simplifié pour le MVP)
        # Score basé sur les économies et l'impact, normalisé sur 100
        total_score = min(100, int(
            (cost_savings_total / 500) * 40 +  # 40% basé sur les économies (max 500€)
            (co2_savings_kg / 5000) * 60       # 60% basé sur la réduction CO2 (max 5000kg)
        ))
        
        # Déterminer le label
        label = "Bronze"
        if total_score >= 75:
            label = "Gold"
        elif total_score >= 50:
            label = "Silver"
        
        # Créer ou mettre à jour le Passeport Vert
        green_passport = GreenPassport(
            id=uuid.uuid4(),
            user_id=user_id,
            total_score=total_score,
            label=label,
            completed_projects=[UUID4(p["id"]) for p in verified_projects],
            energy_savings_kwh=energy_savings_kwh,
            water_savings_m3=water_savings_m3,
            cost_savings_total=cost_savings_total,
            co2_savings_kg=co2_savings_kg,
            issued_date=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(days=365)  # Valide pour un an
        )
        
        # Note: dans une implémentation réelle, on sauvegarderait le passeport en base de données
        
        return green_passport
    
    async def generate_projects_summary(
        self,
        user_id: UUID4,
        status_filter: Optional[str] = None
    ) -> ProjectSummaryResponse:
        """Génère un résumé des projets d'un utilisateur"""
        # Récupérer les projets de l'utilisateur
        projects = await self.get_user_projects(user_id, status_filter)
        
        if not projects:
            return ProjectSummaryResponse(
                user_id=user_id,
                projects_count=0,
                completed_count=0,
                in_progress_count=0,
                planning_count=0,
                cancelled_count=0,
                total_investment=0,
                estimated_annual_savings=0,
                estimated_co2_reduction=0,
                summary="Aucun projet trouvé pour cet utilisateur."
            )
        
        # Compter les projets par statut
        completed_count = sum(1 for p in projects if p["status"] == "completed")
        in_progress_count = sum(1 for p in projects if p["status"] == "in_progress")
        planning_count = sum(1 for p in projects if p["status"] == "planning")
        cancelled_count = sum(1 for p in projects if p["status"] == "cancelled")
        
        # Calculer les totaux
        total_investment = sum(p.get("actual_cost", 0) for p in projects if p.get("actual_cost") is not None)
        estimated_annual_savings = sum(p.get("estimated_annual_savings", 0) for p in projects)
        estimated_co2_reduction = sum(p.get("estimated_co2_reduction", 0) for p in projects)
        
        # Générer un résumé textuel avec le LLM
        summary = await self.generate_summary_text(
            projects, 
            completed_count,
            in_progress_count,
            planning_count,
            total_investment,
            estimated_annual_savings,
            estimated_co2_reduction
        )
        
        return ProjectSummaryResponse(
            user_id=user_id,
            projects_count=len(projects),
            completed_count=completed_count,
            in_progress_count=in_progress_count,
            planning_count=planning_count,
            cancelled_count=cancelled_count,
            total_investment=total_investment,
            estimated_annual_savings=estimated_annual_savings,
            estimated_co2_reduction=estimated_co2_reduction,
            summary=summary
        )
    
    async def generate_summary_text(
        self,
        projects: List[Dict[str, Any]],
        completed_count: int,
        in_progress_count: int,
        planning_count: int,
        total_investment: float,
        estimated_annual_savings: float,
        estimated_co2_reduction: float
    ) -> str:
        """Génère un texte de résumé des projets avec le LLM"""
        # Préparer le contexte pour le LLM
        roi_years = total_investment / estimated_annual_savings if estimated_annual_savings > 0 else 0
        
        # Créer le prompt
        prompt = f"""
        Génère un résumé concis (max 150 mots) des projets de durabilité d'un utilisateur.
        
        Informations clés:
        - Nombre total de projets: {len(projects)}
        - Projets complétés: {completed_count}
        - Projets en cours: {in_progress_count}
        - Projets en planification: {planning_count}
        - Investissement total: {total_investment}€
        - Économies annuelles estimées: {estimated_annual_savings}€
        - Réduction CO2 estimée: {estimated_co2_reduction}kg
        - Retour sur investissement: {roi_years:.1f} ans
        
        Le résumé doit être personnalisé, encourageant et mettre en avant les bénéfices
        financiers et environnementaux des actions entreprises. Si des projets sont en cours
        ou planifiés, mentionne les bénéfices additionnels attendus.
        """
        
        # Générer le résumé
        system_message = "Tu es un expert en durabilité et optimisation énergétique."
        summary = await self.llm_service.generate_response(prompt, system_message)
        
        return summary


# Initialisation du service
monitoring_service = MonitoringService()

# Routes API
@app.post("/api/v1/update-project", response_model=Dict[str, Any])
async def update_project(
    update: ProjectProgressUpdate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour la mise à jour de l'avancement d'un projet"""
    return await monitoring_service.update_project_progress(update)


@app.post("/api/v1/verification-requirements", response_model=ProjectVerificationResponse)
async def get_verification_requirements(
    request: ProjectVerificationRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour récupérer les exigences de vérification"""
    return await monitoring_service.get_verification_requirements(
        project_id=request.project_id,
        user_id=request.user_id
    )


@app.post("/api/v1/verify-document", response_model=DocumentVerificationResult)
async def verify_document(
    project_id: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour la vérification d'un document"""
    return await monitoring_service.verify_document(
        project_id=UUID4(project_id),
        document_type=document_type,
        file=file
    )


@app.post("/api/v1/complete-verification", response_model=Dict[str, Any])
async def complete_verification(
    request: ProjectVerificationRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour finaliser la vérification d'un projet"""
    return await monitoring_service.complete_verification(
        project_id=request.project_id,
        user_id=request.user_id,
        verification_notes=request.verification_notes
    )


@app.post("/api/v1/green-passport", response_model=GreenPassport)
async def generate_green_passport(
    request: GreenPassportRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour la génération du Passeport Vert"""
    return await monitoring_service.generate_green_passport(
        user_id=request.user_id
    )


@app.post("/api/v1/projects-summary", response_model=ProjectSummaryResponse)
async def generate_projects_summary(
    request: ProjectSummaryRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour la génération d'un résumé des projets"""
    return await monitoring_service.generate_projects_summary(
        user_id=request.user_id,
        status_filter=request.status_filter
    )


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Lancer le serveur en mode développement
    port = int(os.getenv("PORT", "8005"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
