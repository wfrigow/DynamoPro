"""
Data Collector Agent pour DynamoPro
----------------------------------
Ce module est responsable de la collecte des données utilisateur à travers
des conversations et l'analyse de documents.
"""

import logging
import os
import uuid
import base64
from typing import Dict, List, Optional, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, UUID4, Field

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.ai_utils import ConversationalAgent, LLMService, OCRService
from common.auth import get_current_active_user, UserInDB
from common.config import settings
from common.models import (
    UserProfile, ConsumptionData, Property, DomainType, UserType, BelgiumRegion, Language
)

# Import des nouveaux modules
from speech_processor import SpeechProcessor
from data_extractor import DataExtractor
from llm_service import LLMService, ChatMessage as LLMChatMessage

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("data-collector")

# Initialisation de l'application FastAPI
app = FastAPI(
    title="DynamoPro Data Collector Agent",
    description="Agent de collecte de données pour DynamoPro",
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
class ChatMessage(BaseModel):
    """Message de chat pour conversation avec l'agent"""
    content: str
    user_id: str
    session_id: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 encoded audio
    conversation_history: Optional[List[Dict[str, str]]] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Réponse à un message de chat"""
    message: str
    extracted_data: Optional[Dict[str, Any]] = None
    next_questions: Optional[List[str]] = None
    audio_data: Optional[str] = None  # Base64 encoded audio for voice response

class VoiceMessage(BaseModel):
    """Message vocal pour conversation avec l'agent"""
    audio_data: str = Field(..., description="Base64 encoded audio data")
    user_id: UUID4
    context: Optional[Dict[str, Any]] = None
    language: str = "fr-FR"

class DocumentUploadResponse(BaseModel):
    """Réponse à un téléchargement de document"""
    document_id: str
    extracted_data: Dict[str, Any]
    status: str

# Création de l'agent conversationnel pour le profilage
profile_agent_prompt = """
Tu es l'Agent de Collecte de Données de DynamoPro, une plateforme d'optimisation de la durabilité en Belgique.
Ton rôle est de recueillir les informations nécessaires pour créer un profil complet de l'utilisateur.
Sois toujours poli, concis et précis dans tes questions. Adapte ton langage au type d'utilisateur.

Tu dois collecter progressivement les informations suivantes:
1. Type d'utilisateur (particulier, indépendant, TPE, PME, grande entreprise)
2. Nom et coordonnées (email, téléphone)
3. Adresse complète et code postal
4. Région belge (Wallonie, Flandre, Bruxelles)
5. Pour les entreprises: nom, taille (nombre d'employés), numéro TVA

Procède par étapes, sans submerger l'utilisateur avec trop de questions à la fois.
Commence toujours par le type d'utilisateur car cela détermine les questions suivantes.

IMPORTANT: Après avoir recueilli les informations de base (type d'utilisateur et région), propose de passer
à l'étape suivante pour collecter les informations sur la consommation énergétique.
"""

consumption_agent_prompt = """
Tu es l'Agent de Collecte de Données de DynamoPro, spécialisé dans l'analyse de la consommation énergétique et d'eau.
Ton rôle est de recueillir des informations précises sur la consommation de l'utilisateur.

Tu dois collecter progressivement les informations suivantes:
1. Type de consommation (électricité, gaz, eau)
2. Période de consommation (dates de début et de fin)
3. Quantité consommée (kWh pour l'électricité et le gaz, m³ pour l'eau)
4. Montant payé (en euros)
5. Fournisseur
6. Type de contrat si connu

Tu peux également suggérer à l'utilisateur d'uploader ses factures pour une extraction automatique
des données plutôt que de les saisir manuellement.

IMPORTANT: Après avoir recueilli les informations de base sur la consommation, propose de passer
à l'étape suivante pour collecter les informations sur la propriété.
"""

property_agent_prompt = """
Tu es l'Agent de Collecte de Données de DynamoPro, spécialisé dans l'analyse des propriétés.
Ton rôle est de recueillir des informations sur les bâtiments et logements de l'utilisateur.

Tu dois collecter progressivement les informations suivantes:
1. Type de propriété (appartement, maison, bureau, etc.)
2. Superficie en m²
3. Année de construction
4. Année de dernière rénovation significative (si applicable)
5. Classe énergétique (si connue)
6. Type de chauffage
7. Nombre d'occupants
8. Adresse complète (si différente de l'adresse principale)

IMPORTANT: Après avoir recueilli suffisamment d'informations, explique à l'utilisateur que
ces données permettront de générer des recommandations personnalisées pour améliorer
l'efficacité énergétique et réduire son empreinte environnementale.
"""

# Initialisation des agents
profile_agent = ConversationalAgent(system_message=profile_agent_prompt)
consumption_agent = ConversationalAgent(system_message=consumption_agent_prompt)
property_agent = ConversationalAgent(system_message=property_agent_prompt)

# Initialisation des services auxiliaires
speech_processor = SpeechProcessor()
data_extractor = DataExtractor()
llm_service = LLMService()


class DataCollectorService:
    """Service principal de collecte de données"""
    
    @staticmethod
    async def process_chat_message(chat_message: ChatMessage, agent_type: str) -> ChatResponse:
        """Traite un message de chat avec l'agent approprié"""
        try:
            # Si des données audio sont fournies, les convertir en texte
            if chat_message.audio_data:
                speech_result = await speech_processor.speech_to_text(chat_message.audio_data)
                message_text = speech_result.get("text", "")
                logging.info(f"Converted speech to text: {message_text}")
            else:
                message_text = chat_message.content
            
            # Utiliser le service LLM pour traiter le message
            try:
                # Utiliser l'historique de conversation s'il est fourni
                conversation_history = chat_message.conversation_history or []
                
                # Appeler le service LLM
                llm_response = await llm_service.process_message(
                    user_message=message_text,
                    agent_type=agent_type,
                    conversation_history=conversation_history
                )
                
                # Extraire la réponse et les données
                response = llm_response.message
                extracted_data = llm_response.extracted_data or {}
                
                logging.info(f"LLM response: {response}")
                logging.info(f"Extracted data: {extracted_data}")
                
                # Générer des questions de suivi basées sur les données extraites
                next_questions = []
                
                # Déterminer les questions de suivi en fonction du type d'agent et des données extraites
                if agent_type == "profile":
                    if not extracted_data.get("userType"):
                        next_questions.append("Êtes-vous un particulier, un indépendant ou une entreprise ?")
                    if not extracted_data.get("region"):
                        next_questions.append("Dans quelle région de Belgique êtes-vous situé(e) ?")
                elif agent_type == "consumption":
                    if not extracted_data.get("electricityUsage"):
                        next_questions.append("Quelle est votre consommation annuelle d'électricité en kWh ?")
                    if not extracted_data.get("gasUsage"):
                        next_questions.append("Utilisez-vous du gaz ? Si oui, quelle est votre consommation ?")
                elif agent_type == "property":
                    if not extracted_data.get("propertyType"):
                        next_questions.append("S'agit-il d'une maison, d'un appartement ou d'un autre type de bâtiment ?")
                    if not extracted_data.get("propertySize"):
                        next_questions.append("Quelle est la superficie en m² ?")
                    if not extracted_data.get("yearBuilt"):
                        next_questions.append("Quelle est l'année de construction ?")
                
                return ChatResponse(
                    message=response,
                    extracted_data=extracted_data,
                    next_questions=next_questions
                )
                
            except Exception as llm_error:
                logging.error(f"Error with LLM service: {str(llm_error)}")
                
                # Fallback: utiliser l'extracteur de données classique si le LLM échoue
                extracted_data = data_extractor.extract_data(message_text, agent_type)
                logging.info(f"Fallback - Extracted data: {extracted_data}")
                
                # Générer une réponse basique
                if agent_type == "profile":
                    response = "Pourriez-vous me dire si vous êtes un particulier, un indépendant ou une entreprise ? Et dans quelle région de Belgique êtes-vous situé(e) ?"
                elif agent_type == "consumption":
                    response = "Pourriez-vous me donner des informations sur votre consommation annuelle d'électricité en kWh et/ou de gaz ?"
                elif agent_type == "property":
                    response = "Pourriez-vous me décrire votre propriété ? J'ai besoin de savoir s'il s'agit d'une maison, d'un appartement, etc."
                else:
                    response = "Je n'ai pas bien compris. Pourriez-vous reformuler votre message ?"
                
                return ChatResponse(
                    message=response,
                    extracted_data=extracted_data,
                    next_questions=[]
                )
                
        except Exception as e:
            logging.error(f"Error processing chat message: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @staticmethod
    async def process_voice_message(voice_message: VoiceMessage, agent_type: str) -> ChatResponse:
        """Traite un message vocal avec l'agent approprié"""
        try:
            # Convertir l'audio en texte
            speech_result = await speech_processor.speech_to_text(
                voice_message.audio_data,
                voice_message.language
            )
            
            # Créer un message texte à partir du résultat de la reconnaissance vocale
            text_message = ChatMessage(
                content=speech_result["text"],
                user_id=voice_message.user_id,
                context=voice_message.context
            )
            
            # Traiter le message texte
            text_response = await DataCollectorService.process_chat_message(text_message, agent_type)
            
            # Convertir la réponse texte en audio
            audio_result = await speech_processor.text_to_speech(
                text_response.message,
                voice_message.language
            )
            
            # Ajouter les données audio à la réponse
            text_response.audio_data = audio_result["audio_data"]
            
            return text_response
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message vocal: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors du traitement du message vocal: {str(e)}"
            )
    
    @staticmethod
    async def process_document(
        file: UploadFile,
        document_type: str,
        user_id: UUID4
    ) -> DocumentUploadResponse:
        """Traite un document téléchargé (facture, etc.)"""
        # Sauvegarde temporaire du fichier
        temp_file_path = f"/tmp/{uuid.uuid4()}_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())
        
        # Détermination du schéma en fonction du type de document
        schema = {}
        
        if document_type == "energy_bill":
            schema = {
                "provider": "string",
                "start_date": "date",
                "end_date": "date",
                "consumption_kwh": "number",
                "amount_eur": "number",
                "contract_type": "string"
            }
        elif document_type == "water_bill":
            schema = {
                "provider": "string",
                "start_date": "date",
                "end_date": "date",
                "consumption_m3": "number",
                "amount_eur": "number"
            }
        elif document_type == "property_document":
            schema = {
                "property_type": "string",
                "address": "string",
                "size_m2": "number",
                "year_built": "number",
                "energy_class": "string"
            }
        
        # Extraction des données du document
        ocr_service = OCRService()
        extracted_data = await ocr_service.extract_structured_data_from_image(
            temp_file_path,
            schema
        )
        
        # Suppression du fichier temporaire
        os.remove(temp_file_path)
        
        return DocumentUploadResponse(
            document_id=str(uuid.uuid4()),
            extracted_data=extracted_data,
            status="processed"
        )
        
    @staticmethod
    async def generate_recommendations(audit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Génère des recommandations personnalisées basées sur les données d'audit
        
        Args:
            audit_data: Données collectées lors de l'audit
        
        Returns:
            Liste de recommandations personnalisées
        """
        # Dans une implémentation réelle, nous utiliserions un modèle d'IA ou des règles métier
        # pour générer des recommandations personnalisées
        
        recommendations = []
        
        # Exemple de logique de recommandation basée sur les données de propriété
        property_data = audit_data.get("property", {})
        if property_data.get("yearBuilt", 2020) < 2000:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "title": "Isolation des murs",
                "description": "L'isolation des murs peut réduire votre consommation énergétique de 25%.",
                "savings": 850,
                "roi": 4,
                "domain": "energy",
                "priority": "high"
            })
        
        # Recommandations basées sur la consommation
        consumption_data = audit_data.get("consumption", {})
        if consumption_data.get("electricityUsage", 0) > 4000:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "title": "Installation de panneaux solaires",
                "description": "Avec votre consommation élevée, les panneaux solaires seraient rentabilisés en 5 ans.",
                "savings": 1200,
                "roi": 5,
                "domain": "energy",
                "priority": "medium"
            })
        
        if consumption_data.get("waterUsage", 0) > 100:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "title": "Système de récupération d'eau de pluie",
                "description": "Réduisez votre consommation d'eau potable avec un système de récupération d'eau de pluie.",
                "savings": 350,
                "roi": 3,
                "domain": "water",
                "priority": "medium"
            })
        
        # Ajouter des recommandations par défaut si nécessaire
        if len(recommendations) < 2:
            recommendations.append({
                "id": str(uuid.uuid4()),
                "title": "Remplacement des ampoules par des LED",
                "description": "Remplacer toutes vos ampoules par des LED peut réduire votre consommation d'électricité liée à l'éclairage de 80%.",
                "savings": 120,
                "roi": 1,
                "domain": "energy",
                "priority": "low"
            })
        
        return recommendations


# Routes API
@app.post("/api/v1/chat/{agent_type}", response_model=ChatResponse)
async def chat_with_agent(
    agent_type: str,
    chat_message: ChatMessage,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour les conversations textuelles avec l'agent"""
    if agent_type not in ["profile", "consumption", "property"]:
        raise HTTPException(status_code=400, detail="Type d'agent non supporté")
    
    return await DataCollectorService.process_chat_message(chat_message, agent_type)


@app.post("/api/v1/voice/{agent_type}", response_model=ChatResponse)
async def voice_chat_with_agent(
    agent_type: str,
    voice_message: VoiceMessage,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour les conversations vocales avec l'agent"""
    if agent_type not in ["profile", "consumption", "property"]:
        raise HTTPException(status_code=400, detail="Type d'agent non supporté")
    
    return await DataCollectorService.process_voice_message(voice_message, agent_type)


@app.post("/api/v1/documents", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    user_id: str = Form(...),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Point d'entrée pour l'upload et l'analyse de documents"""
    if document_type not in ["energy_bill", "water_bill", "property_document"]:
        raise HTTPException(status_code=400, detail="Type de document non supporté")
    
    try:
        user_uuid = UUID4(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID utilisateur invalide")
    
    return await DataCollectorService.process_document(file, document_type, user_uuid)


@app.post("/api/v1/recommendations")
async def generate_recommendations(
    audit_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Génère des recommandations basées sur les données d'audit"""
    return await DataCollectorService.generate_recommendations(audit_data)


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy"}


if __name__ == "__main__":
    # Lancer le serveur en mode développement
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
