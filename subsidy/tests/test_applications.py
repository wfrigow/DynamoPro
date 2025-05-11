"""
Tests pour les applications de subventions
----------------------------------------
Tests unitaires pour les fonctionnalités de gestion des applications de subventions
"""

import pytest
import json
from fastapi.testclient import TestClient
from fastapi import FastAPI, status

from backend.subsidy.config import settings


def test_submit_application_authenticated(client: TestClient, auth_headers: dict):
    """Test de soumission d'une application de subvention avec authentification"""
    subsidy_id = "sub1"
    application_data = {
        "applicant": {
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+32 470 12 34 56",
            "address": "Rue de la Science 123, 1040 Bruxelles",
            "userType": "individual"
        },
        "property": {
            "address": "Rue de la Science 123, 1040 Bruxelles",
            "type": "house",
            "yearBuilt": "1975"
        },
        "project": {
            "description": "Isolation de la toiture avec des matériaux écologiques",
            "estimatedCost": 5000,
            "estimatedCompletionDate": "2025-09-15",
            "workStarted": "no",
            "contractorSelected": "yes",
            "contractorName": "Iso-Pro SPRL"
        },
        "bankDetails": {
            "accountHolder": "Jean Dupont",
            "iban": "BE68 5390 0754 7034"
        }
    }
    
    response = client.post(
        f"{settings.API_PREFIX}/subsidies/{subsidy_id}/applications",
        headers=auth_headers,
        json=application_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["subsidyId"] == subsidy_id
    assert data["status"] == "submitted"
    assert "submissionDate" in data
    assert "referenceNumber" in data


def test_submit_application_unauthenticated(client: TestClient):
    """Test de soumission d'une application de subvention sans authentification"""
    subsidy_id = "sub1"
    application_data = {
        "applicant": {
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com"
        }
    }
    
    response = client.post(
        f"{settings.API_PREFIX}/subsidies/{subsidy_id}/applications",
        json=application_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data


def test_save_draft_authenticated(client: TestClient, auth_headers: dict):
    """Test de sauvegarde d'un brouillon d'application avec authentification"""
    subsidy_id = "sub1"
    draft_data = {
        "applicant": {
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+32 470 12 34 56"
        },
        "property": {
            "address": "Rue de la Science 123, 1040 Bruxelles"
        }
    }
    
    response = client.post(
        f"{settings.API_PREFIX}/subsidies/{subsidy_id}/applications/drafts",
        headers=auth_headers,
        json=draft_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["subsidyId"] == subsidy_id
    assert data["status"] == "draft"
    assert "lastUpdated" in data
    
    # Test de mise à jour d'un brouillon existant
    draft_id = data["id"]
    updated_draft_data = {
        "applicant": {
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+32 470 12 34 56"
        },
        "property": {
            "address": "Rue de la Science 123, 1040 Bruxelles",
            "type": "house",
            "yearBuilt": "1975"
        }
    }
    
    response = client.put(
        f"{settings.API_PREFIX}/subsidies/{subsidy_id}/applications/drafts/{draft_id}",
        headers=auth_headers,
        json=updated_draft_data
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == draft_id
    assert "lastUpdated" in data


def test_get_application_by_id_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération d'une application par son ID avec authentification"""
    application_id = "app1"
    response = client.get(
        f"{settings.API_PREFIX}/subsidies/applications/{application_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == application_id
    assert "subsidyId" in data
    assert "status" in data
    assert "submissionDate" in data
    assert "applicant" in data
    assert "property" in data
    assert "project" in data
    assert "documents" in data
    assert "notes" in data
    assert "history" in data


def test_get_application_by_id_unauthenticated(client: TestClient):
    """Test de récupération d'une application par son ID sans authentification"""
    application_id = "app1"
    response = client.get(
        f"{settings.API_PREFIX}/subsidies/applications/{application_id}"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data


def test_add_application_note_authenticated(client: TestClient, auth_headers: dict):
    """Test d'ajout d'une note à une application avec authentification"""
    application_id = "app1"
    note_content = "Voici une note de test pour l'application."
    
    response = client.post(
        f"{settings.API_PREFIX}/subsidies/applications/{application_id}/notes",
        headers=auth_headers,
        json={"content": note_content}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "id" in data
    assert data["content"] == note_content
    assert "date" in data
    assert "author" in data
    assert "authorType" in data


def test_upload_application_document_authenticated(client: TestClient, auth_headers: dict):
    """Test de téléchargement d'un document pour une application avec authentification"""
    application_id = "app1"
    document_id = "doc1"
    
    # Créer un fichier de test
    test_file_content = b"Test file content"
    files = {"file": ("test_document.pdf", test_file_content, "application/pdf")}
    
    response = client.post(
        f"{settings.API_PREFIX}/subsidies/applications/{application_id}/documents/{document_id}",
        headers=auth_headers,
        files=files
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == document_id
    assert "name" in data
    assert data["status"] == "pending"
    assert "uploadDate" in data
    assert "size" in data
