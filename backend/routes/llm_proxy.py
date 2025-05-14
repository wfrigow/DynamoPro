"""
Module pour proxifier les requêtes vers OpenAI depuis le frontend.
Ce proxy est nécessaire pour protéger la clé API OpenAI qui ne doit pas être exposée côté client.
"""
import os
import httpx
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

# URL de l'API OpenAI
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

@router.post("/api/llm")
async def proxy_openai(request: Request):
    """
    Endpoint qui proxifie les requêtes vers l'API OpenAI.
    Le frontend envoie une requête à cet endpoint, qui la transfère à OpenAI
    et renvoie la réponse au frontend.
    """
    try:
        # Récupérer la clé API OpenAI depuis les variables d'environnement
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="La clé API OpenAI n'est pas configurée sur le serveur")
        
        # Récupérer le corps de la requête (contenant model, messages, etc.)
        request_data = await request.json()
        
        # Configurer les headers avec l'authentification OpenAI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Créer un client HTTP asynchrone avec un timeout approprié
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Transférer la requête à OpenAI
            response = await client.post(
                OPENAI_API_URL,
                json=request_data,
                headers=headers
            )
            
            # Récupérer la réponse JSON d'OpenAI
            response_data = response.json()
            
            # Retourner directement la réponse d'OpenAI au frontend
            return response_data
            
    except httpx.HTTPStatusError as e:
        # En cas d'erreur HTTP de la part d'OpenAI
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erreur OpenAI: {e.response.text}"
        )
    except httpx.RequestError as e:
        # En cas d'erreur réseau
        raise HTTPException(
            status_code=500,
            detail=f"Erreur de connexion à OpenAI: {str(e)}"
        )
    except Exception as e:
        # Pour toute autre erreur
        raise HTTPException(
            status_code=500,
            detail=f"Erreur inattendue: {str(e)}"
        )
