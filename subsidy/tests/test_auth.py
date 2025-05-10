"""
Tests pour les routes d'authentification
---------------------------------------
Tests unitaires pour les fonctionnalités d'authentification
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from jose import jwt

from backend.subsidy.config import settings


def test_login_success(client: TestClient):
    """Test de connexion réussie"""
    response = client.post(
        f"{settings.API_PREFIX}/auth/token",
        data={"username": "user@example.com", "password": "password"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Vérifier que le token est valide
    token = data["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert "sub" in payload
    assert "exp" in payload


def test_login_invalid_credentials(client: TestClient):
    """Test de connexion avec des identifiants invalides"""
    response = client.post(
        f"{settings.API_PREFIX}/auth/token",
        data={"username": "user@example.com", "password": "wrong_password"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data


def test_me_endpoint_authenticated(client: TestClient, auth_headers: dict):
    """Test de l'endpoint /me avec authentification"""
    response = client.get(
        f"{settings.API_PREFIX}/auth/me",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "hashed_password" not in data


def test_me_endpoint_unauthenticated(client: TestClient):
    """Test de l'endpoint /me sans authentification"""
    response = client.get(f"{settings.API_PREFIX}/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data
