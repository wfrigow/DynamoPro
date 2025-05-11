#!/usr/bin/env python3
"""
Proxy LLM simple pour DynamoPro
Relais sécurisé des requêtes vers OpenAI
"""

import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv("backend/subsidy/.env")

# Récupérer la clé API OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY non définie dans les variables d'environnement")

print(f"Clé API OpenAI trouvée : {OPENAI_API_KEY[:5]}...{OPENAI_API_KEY[-5:]}")

# Initialiser l'application FastAPI
app = FastAPI(
    title="DynamoPro LLM Proxy",
    description="Proxy sécurisé pour les requêtes OpenAI",
    version="1.0.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/llm")
async def llm_proxy(request: Request):
    """Relais des requêtes vers l'API OpenAI"""
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY non configurée sur le serveur")
    
    # Récupérer le corps de la requête
    body = await request.json()
    
    # Préparer les en-têtes pour OpenAI
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # URL de l'API OpenAI
    openai_url = "https://api.openai.com/v1/chat/completions"
    
    # Effectuer la requête à OpenAI
    async with httpx.AsyncClient() as client:
        try:
            print(f"Envoi de la requête à OpenAI : {body.get('model', 'unknown')}")
            resp = await client.post(openai_url, headers=headers, json=body, timeout=30.0)
            
            if resp.status_code != 200:
                print(f"Erreur OpenAI : {resp.status_code} - {resp.text}")
                raise HTTPException(
                    status_code=resp.status_code, 
                    detail=f"Erreur OpenAI : {resp.text}"
                )
            
            # Retourner la réponse d'OpenAI
            response_data = resp.json()
            print("Réponse OpenAI reçue avec succès")
            return response_data
            
        except Exception as e:
            print(f"Exception lors de l'appel à OpenAI : {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erreur lors de l'appel à OpenAI : {str(e)}"
            )

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy", "openai_key_configured": bool(OPENAI_API_KEY)}

if __name__ == "__main__":
    # Lancer le serveur
    port = int(os.getenv("PORT", "8003"))
    print(f"Démarrage du proxy LLM sur le port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
