"""
Service LLM pour le Data Collector Agent
---------------------------------------
Ce module gère les interactions avec les modèles de langage avancés.
"""

import os
import logging
import json
import asyncio
import re
from typing import Dict, List, Any, Optional

import aiohttp
from pydantic import BaseModel

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm-service")

class ChatMessage(BaseModel):
    """Message pour une conversation avec un LLM"""
    role: str  # 'system', 'user', 'assistant'
    content: str

class ChatCompletionRequest(BaseModel):
    """Requête pour une complétion de chat"""
    model: str
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 500
    
class ChatCompletionResponse(BaseModel):
    """Réponse d'une complétion de chat"""
    message: str
    extracted_data: Optional[Dict[str, Any]] = None

class LLMService:
    """Service pour interagir avec des modèles de langage avancés"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialise le service LLM"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("Aucune clé API OpenAI trouvée. Le service fonctionnera en mode simulation.")
        
        # Instructions système pour chaque type d'agent
        self.system_instructions = {
            "profile": """
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

À la fin de chaque réponse, tu dois extraire les données pertinentes du message de l'utilisateur dans un format JSON.
Exemple: {"userType": "individual", "region": "wallonie"}
""",
            "consumption": """
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

À la fin de chaque réponse, tu dois extraire les données pertinentes du message de l'utilisateur dans un format JSON.
Exemple: {"electricityUsage": 3500, "gasUsage": 15000, "waterUsage": 120}
""",
            "property": """
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

À la fin de chaque réponse, tu dois extraire les données pertinentes du message de l'utilisateur dans un format JSON.
Exemple: {"propertyType": "house", "propertySize": 120, "yearBuilt": 1995, "heatingType": "gaz"}
"""
        }
    
    async def process_message(
        self, 
        user_message: str, 
        agent_type: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> ChatCompletionResponse:
        """
        Traite un message utilisateur avec le modèle de langage
        
        Args:
            user_message: Le message de l'utilisateur
            agent_type: Le type d'agent ('profile', 'consumption', 'property')
            conversation_history: L'historique de la conversation
            
        Returns:
            La réponse du modèle avec les données extraites
        """
        if agent_type not in self.system_instructions:
            raise ValueError(f"Type d'agent non supporté: {agent_type}")
        
        # Construire les messages pour la requête
        messages = []
        
        # Ajouter l'instruction système
        messages.append(ChatMessage(
            role="system",
            content=self.system_instructions[agent_type]
        ))
        
        # Ajouter l'historique de conversation si disponible
        if conversation_history:
            for msg in conversation_history:
                messages.append(ChatMessage(
                    role=msg["role"],
                    content=msg["content"]
                ))
        
        # Ajouter le message de l'utilisateur
        messages.append(ChatMessage(
            role="user",
            content=user_message
        ))
        
        # Si la clé API est disponible, appeler l'API OpenAI
        if self.api_key:
            try:
                return await self._call_openai_api(messages)
            except Exception as e:
                logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
                # En cas d'erreur, utiliser le mode simulation
                return await self._simulate_llm_response(user_message, agent_type)
        else:
            # Mode simulation
            return await self._simulate_llm_response(user_message, agent_type)
    
    async def _call_openai_api(self, messages: List[ChatMessage]) -> ChatCompletionResponse:
        """
        Appelle l'API OpenAI pour obtenir une réponse
        
        Args:
            messages: Liste des messages de la conversation
            
        Returns:
            La réponse du modèle avec les données extraites
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "gpt-4",  # Utiliser GPT-4 pour de meilleures performances
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": 0.7,
            "max_tokens": 500,
            "response_format": {"type": "json_object"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Erreur API OpenAI ({response.status}): {error_text}")
                
                data = await response.json()
                
                # Extraire la réponse
                assistant_message = data["choices"][0]["message"]["content"]
                
                # Analyser la réponse pour extraire le texte et les données
                try:
                    # La réponse est au format JSON
                    response_data = json.loads(assistant_message)
                    
                    # Extraire le message et les données
                    message = response_data.get("response", "")
                    extracted_data = response_data.get("extracted_data", {})
                    
                    return ChatCompletionResponse(
                        message=message,
                        extracted_data=extracted_data
                    )
                except json.JSONDecodeError:
                    # Si la réponse n'est pas au format JSON, utiliser le texte complet
                    return ChatCompletionResponse(
                        message=assistant_message,
                        extracted_data={}
                    )
    
    async def _simulate_llm_response(self, user_message: str, agent_type: str) -> ChatCompletionResponse:
        """
        Simule une réponse LLM pour le développement et les tests
        
        Args:
            user_message: Le message de l'utilisateur
            agent_type: Le type d'agent ('profile', 'consumption', 'property')
            
        Returns:
            Une réponse simulée avec des données extraites
        """
        # Simuler un délai de traitement
        await asyncio.sleep(1)
        
        user_message_lower = user_message.lower()
        extracted_data = {}
        response = ""
        
        # Logique de simulation basée sur le type d'agent
        if agent_type == "profile":
            # Extraction du type d'utilisateur
            if "particulier" in user_message_lower:
                extracted_data["userType"] = "individual"
            elif "entreprise" in user_message_lower:
                extracted_data["userType"] = "business"
            elif any(term in user_message_lower for term in ["indépendant", "independant", "auto-entrepreneur"]):
                extracted_data["userType"] = "self_employed"
            
            # Extraction de la région
            if "wallonie" in user_message_lower:
                extracted_data["region"] = "wallonie"
            elif "bruxelles" in user_message_lower:
                extracted_data["region"] = "bruxelles"
            elif "flandre" in user_message_lower:
                extracted_data["region"] = "flandre"
            
            # Génération de réponse
            if "userType" in extracted_data and "region" in extracted_data:
                response = f"Merci pour ces informations. Vous êtes {extracted_data['userType']} en {extracted_data['region']}. Passons maintenant à l'analyse de votre consommation énergétique. Pouvez-vous me dire quelle est votre consommation annuelle d'électricité en kWh ?"
            elif "userType" in extracted_data:
                response = f"Merci de m'avoir indiqué que vous êtes {extracted_data['userType']}. Dans quelle région de Belgique êtes-vous situé(e) ? Wallonie, Bruxelles ou Flandre ?"
            elif "region" in extracted_data:
                response = f"Vous êtes en {extracted_data['region']}. Êtes-vous un particulier, un indépendant ou une entreprise ?"
            else:
                response = "Pourriez-vous me préciser si vous êtes un particulier, un indépendant ou une entreprise ? Et dans quelle région de Belgique êtes-vous situé(e) ?"
        
        elif agent_type == "consumption":
            # Extraction de la consommation électrique
            electricity_match = re.search(r"(\d+)\s*(?:kwh|kilowatt)", user_message_lower)
            if electricity_match:
                extracted_data["electricityUsage"] = int(electricity_match.group(1))
            
            # Extraction de la consommation de gaz
            gas_match = re.search(r"(\d+)\s*(?:m3|mètres cubes|metres cubes).*gaz", user_message_lower) or re.search(r"gaz.*(\d+)\s*(?:m3|mètres cubes|metres cubes)", user_message_lower)
            if gas_match:
                extracted_data["gasUsage"] = int(gas_match.group(1))
            
            # Génération de réponse
            if extracted_data:
                response = "Merci pour ces informations sur votre consommation. "
                if "electricityUsage" in extracted_data:
                    response += f"J'ai noté une consommation électrique de {extracted_data['electricityUsage']} kWh. "
                if "gasUsage" in extracted_data:
                    response += f"Votre consommation de gaz est de {extracted_data['gasUsage']} m³. "
                response += "Parlons maintenant de votre propriété. S'agit-il d'une maison, d'un appartement ou d'un autre type de bâtiment ?"
            else:
                response = "Pourriez-vous me donner des informations sur votre consommation annuelle d'électricité en kWh et/ou de gaz en m³ ?"
        
        elif agent_type == "property":
            # Extraction du type de propriété
            if "maison" in user_message_lower:
                extracted_data["propertyType"] = "house"
            elif "appartement" in user_message_lower:
                extracted_data["propertyType"] = "apartment"
            elif any(term in user_message_lower for term in ["bureau", "commercial"]):
                extracted_data["propertyType"] = "commercial"
            
            # Extraction de la superficie
            size_match = re.search(r"(\d+)\s*(?:m2|mètres carrés|metres carres)", user_message_lower)
            if size_match:
                extracted_data["propertySize"] = int(size_match.group(1))
            
            # Extraction de l'année de construction
            year_match = re.search(r"(?:construit|bâti|construction).*?(\d{4})", user_message_lower) or re.search(r"(\d{4}).*(?:construit|bâti|construction)", user_message_lower)
            if year_match:
                extracted_data["yearBuilt"] = int(year_match.group(1))
            
            # Génération de réponse
            if extracted_data:
                response = "Merci pour ces informations sur votre propriété. "
                if "propertyType" in extracted_data:
                    property_type_fr = {"house": "maison", "apartment": "appartement", "commercial": "local commercial"}
                    response += f"Vous avez une {property_type_fr[extracted_data['propertyType']]}. "
                if "propertySize" in extracted_data:
                    response += f"Sa superficie est de {extracted_data['propertySize']} m². "
                if "yearBuilt" in extracted_data:
                    response += f"Elle a été construite en {extracted_data['yearBuilt']}. "
                response += "Merci pour toutes ces informations ! Je vais maintenant pouvoir générer des recommandations personnalisées pour améliorer l'efficacité énergétique de votre propriété."
            else:
                response = "Pourriez-vous me décrire votre propriété ? J'ai besoin de savoir s'il s'agit d'une maison, d'un appartement, etc., ainsi que sa superficie et son année de construction."
        
        return ChatCompletionResponse(
            message=response,
            extracted_data=extracted_data
        )
