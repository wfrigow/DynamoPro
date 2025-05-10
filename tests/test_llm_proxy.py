import os
import sys
import json
import pathlib
import pytest
from fastapi.testclient import TestClient
from types import SimpleNamespace

# Assure que le répertoire racine est dans sys.path
ROOT_DIR = pathlib.Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

# Importer l'application FastAPI du module subsidy
from backend.subsidy.main import app  # type: ignore

client = TestClient(app)

@pytest.fixture(autouse=True)
def set_openai_key(monkeypatch):
    # Définir une fausse clé API pour les tests
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

@pytest.fixture(autouse=True)
def mock_httpx_post(monkeypatch):
    """Intercepte les appels httpx vers l'API OpenAI et renvoie une réponse simulée."""
    async def _fake_post(url, headers=None, json=None):
        # On vérifie que le proxy envoie bien les champs attendus
        assert json["model"] == "gpt-4"
        assert isinstance(json["messages"], list)
        # Réponse simulée de l'API OpenAI
        fake_content = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 0,
            "model": "gpt-4",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Bonjour ! Voici ma réponse. {\"userType\":\"particulier\"}"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        # Construire un objet Response-like minimal
        return SimpleNamespace(status_code=200, json=lambda: fake_content)
    
    # Patch httpx.AsyncClient.post
    monkeypatch.setattr("backend.app.api.llm.httpx.AsyncClient.post", _fake_post)


def test_llm_proxy_ok():
    payload = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "test"},
            {"role": "user", "content": "Bonjour"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    response = client.post("/api/llm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert data["choices"][0]["message"]["content"].startswith("Bonjour")
