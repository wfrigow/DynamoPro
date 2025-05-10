"""
Utilitaires pour l'IA et les LLM
-------------------------------
Module partagé pour l'intégration des modèles de langage et IA
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

import openai
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from .config import settings

# Configuration du logging
logger = logging.getLogger("ai_utils")

# Configuration de l'API OpenAI
openai.api_key = settings.OPENAI_API_KEY


class LLMService:
    """Service pour interagir avec les modèles de langage"""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.DEFAULT_LLM_MODEL
        self.test_mode = settings.OPENAI_API_KEY in [None, "", "sk-dummy-key-for-testing"]
        
        if not self.test_mode:
            self.chat_model = ChatOpenAI(
                model_name=self.model_name,
                temperature=0.7,
                max_tokens=2000
            )
        else:
            logger.warning("LLM en mode test - les réponses seront simulées")
            self.chat_model = None
    
    async def generate_response(
        self, 
        prompt: str, 
        system_message: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Génère une réponse simple à partir d'un prompt"""
        if self.test_mode:
            return f"Réponse simulée en mode test pour: {prompt[:50]}..."
            
        messages = []
        
        if system_message:
            messages.append(SystemMessage(content=system_message))
            
        messages.append(HumanMessage(content=prompt))
        
        self.chat_model.temperature = temperature
        response = await self.chat_model.agenerate([messages])
        return response.generations[0][0].text
    
    async def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        system_message: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Génère une réponse en tenant compte de l'historique de conversation"""
        if self.test_mode:
            last_message = messages[-1].get("content", "") if messages else ""
            return f"Réponse simulée en mode test pour conversation avec dernier message: {last_message[:50]}..."
            
        formatted_messages = []
        
        if system_message:
            formatted_messages.append(SystemMessage(content=system_message))
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "user":
                formatted_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                formatted_messages.append(AIMessage(content=content))
            elif role == "system":
                formatted_messages.append(SystemMessage(content=content))
        
        self.chat_model.temperature = temperature
        response = await self.chat_model.agenerate([formatted_messages])
        return response.generations[0][0].text
    
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extrait des données structurées à partir de texte selon un schéma"""
        if self.test_mode:
            # Générer des données de test basées sur le schéma
            mock_data = {}
            for key, value in schema.items():
                if isinstance(value, dict) and "type" in value:
                    if value["type"] == "string":
                        mock_data[key] = f"Exemple {key}"
                    elif value["type"] == "number" or value["type"] == "integer":
                        mock_data[key] = 42
                    elif value["type"] == "boolean":
                        mock_data[key] = True
                    elif value["type"] == "array":
                        mock_data[key] = []
                    elif value["type"] == "object":
                        mock_data[key] = {}
                else:
                    mock_data[key] = f"Exemple {key}"
            return mock_data
            
        default_system_prompt = f"""
        Tu es un assistant spécialisé dans l'extraction de données structurées.
        Ton rôle est d'analyser le texte fourni et d'en extraire les informations
        selon le schéma JSON spécifié. Réponds UNIQUEMENT avec un objet JSON valide
        correspondant au schéma, sans aucun texte supplémentaire.
        
        Schéma: {json.dumps(schema, ensure_ascii=False)}
        """
        
        final_system_prompt = system_prompt or default_system_prompt
        
        prompt = f"""
        Voici le texte à analyser:
        
        {text}
        
        Extrait les données selon le schéma spécifié et retourne un JSON valide.
        """
        
        response = await self.generate_response(
            prompt=prompt,
            system_message=final_system_prompt,
            temperature=0.2  # Température basse pour plus de précision
        )
        
        try:
            # Nettoyage: parfois le modèle ajoute du texte autour du JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response.replace("```json", "", 1)
            if response.endswith("```"):
                response = response.rsplit("```", 1)[0]
            
            data = json.loads(response.strip())
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {e}, réponse: {response}")
            return {"error": "Format JSON invalide", "raw_response": response}
            
    async def generate_structured_response(
        self,
        prompt: str,
        system_message: str,
        output_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Génère une réponse structurée à partir d'un prompt en utilisant un schéma de sortie spécifié
        
        Args:
            prompt: Le prompt à envoyer au modèle
            system_message: Le message système pour guider la génération
            output_schema: Le schéma de la structure de sortie attendue
            
        Returns:
            Dictionnaire contenant la réponse structurée selon le schéma
        """
        if self.test_mode:
            # Générer des données de test basées sur le schéma
            mock_data = {}
            for key, value in output_schema.items():
                if isinstance(value, str):
                    mock_data[key] = f"Exemple de {key}"
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    mock_data[key] = [{
                        k: f"Exemple de {k}" if isinstance(v, str) else 42 if "nombre" in v else ["Exemple"] if isinstance(v, list) else True
                        for k, v in value[0].items()
                    }]
                elif isinstance(value, list):
                    mock_data[key] = ["Exemple 1", "Exemple 2"]
            return mock_data
        
        try:
            # Construire un prompt spécifique pour la génération structurée
            structured_prompt = f"""
{prompt}

Réponds en fournissant uniquement un objet JSON valide selon le schéma suivant, sans aucun texte supplémentaire:
{json.dumps(output_schema, ensure_ascii=False, indent=2)}
"""
            
            # Utiliser l'API OpenAI directement pour obtenir une réponse structurée
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": structured_prompt}
            ]
            
            response = await openai.ChatCompletion.acreate(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extraire la réponse JSON
            response_text = response.choices[0].message.content.strip()
            
            # Nettoyer la réponse pour s'assurer qu'elle ne contient que du JSON valide
            # Supprimer les délimiteurs de code markdown s'ils sont présents
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            response_text = response_text.strip()
            
            # Convertir la réponse en dictionnaire
            structured_response = json.loads(response_text)
            
            logger.info(f"Réponse structurée générée avec succès")
            return structured_response
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération de la réponse structurée: {e}")
            # En cas d'erreur, renvoyer un dictionnaire vide qui correspond à la structure attendue
            mock_data = {}
            for key, value in output_schema.items():
                if isinstance(value, str):
                    mock_data[key] = f"Erreur: {e}"
                elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                    mock_data[key] = []
                elif isinstance(value, list):
                    mock_data[key] = []
            return mock_data


class OCRService:
    """Service pour la reconnaissance optique de caractères (OCR)"""
    
    @staticmethod
    async def extract_text_from_image(image_path: str) -> str:
        """Extrait le texte d'une image"""
        # À implémenter avec une bibliothèque OCR ou API
        # Exemple avec API Vision de Google ou autre
        return "Texte extrait de l'image (stub)"
    
    @staticmethod
    async def extract_structured_data_from_image(
        image_path: str,
        schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extrait des données structurées d'une image selon un schéma"""
        # Extraction du texte puis structuration via LLM
        text = await OCRService.extract_text_from_image(image_path)
        
        llm_service = LLMService()
        structured_data = await llm_service.extract_structured_data(text, schema)
        
        return structured_data


class ConversationalAgent:
    """Agent conversationnel pour interagir avec les utilisateurs"""
    
    def __init__(
        self,
        system_message: str,
        model_name: Optional[str] = None,
        memory_key: str = "chat_history"
    ):
        self.system_message = system_message
        self.model_name = model_name or settings.DEFAULT_LLM_MODEL
        self.memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
        self.llm_service = LLMService(model_name=self.model_name)
    
    async def process_message(
        self,
        user_message: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Traite un message utilisateur et génère une réponse"""
        # Ajout du contexte si disponible
        context_str = ""
        if context:
            context_str = f"Contexte: {json.dumps(context, ensure_ascii=False)}\n\n"
        
        # Construction du prompt avec contexte
        prompt = f"{context_str}{user_message}"
        
        # Récupération de l'historique
        history = self.memory.load_memory_variables({}).get("chat_history", [])
        
        # Conversion de l'historique au format attendu
        formatted_history = []
        for message in history:
            if isinstance(message, HumanMessage):
                formatted_history.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                formatted_history.append({"role": "assistant", "content": message.content})
        
        # Ajout du nouveau message
        formatted_history.append({"role": "user", "content": prompt})
        
        # Génération de la réponse
        response = await self.llm_service.chat_with_history(
            messages=formatted_history,
            system_message=self.system_message
        )
        
        # Mise à jour de la mémoire
        self.memory.save_context(
            {"input": prompt},
            {"output": response}
        )
        
        return response
