"""
Configuration pour les tests de l'API de subventions
--------------------------------------------------
Fixtures et configurations partagées pour les tests
"""

import os
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from datetime import timedelta

from backend.subsidy.auth import create_access_token, UserInDB
from backend.subsidy.start_enriched_subsidy_api import app as subsidy_app


@pytest.fixture
def app() -> FastAPI:
    """Fixture pour l'application FastAPI"""
    return subsidy_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """Fixture pour le client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def test_user() -> UserInDB:
    """Fixture pour un utilisateur de test"""
    return UserInDB(
        id="550e8400-e29b-41d4-a716-446655440000",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=False
    )


@pytest.fixture
def test_admin() -> UserInDB:
    """Fixture pour un administrateur de test"""
    return UserInDB(
        id="550e8400-e29b-41d4-a716-446655440001",
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        is_superuser=True
    )


@pytest.fixture
def user_token(test_user: UserInDB) -> str:
    """Fixture pour un token JWT d'utilisateur"""
    access_token_expires = timedelta(minutes=30)
    return create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=access_token_expires
    )


@pytest.fixture
def admin_token(test_admin: UserInDB) -> str:
    """Fixture pour un token JWT d'administrateur"""
    access_token_expires = timedelta(minutes=30)
    return create_access_token(
        data={"sub": str(test_admin.id)},
        expires_delta=access_token_expires
    )


@pytest.fixture
def auth_headers(user_token: str) -> dict:
    """Fixture pour les en-têtes d'authentification"""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Fixture pour les en-têtes d'authentification d'administrateur"""
    return {"Authorization": f"Bearer {admin_token}"}
