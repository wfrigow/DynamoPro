"""
Tests pour les routes d'intégration
---------------------------------
Tests unitaires pour les fonctionnalités d'intégration avec d'autres services
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status

from backend.subsidy.config import settings


def test_get_subsidies_for_recommendation_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération des subventions pour une recommandation avec authentification"""
    recommendation_id = "rec1"
    response = client.get(
        f"{settings.API_PREFIX}/integrations/recommendations/{recommendation_id}/subsidies",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for subsidy in data:
        assert "subsidy_id" in subsidy
        assert "name" in subsidy
        assert "provider" in subsidy
        assert "description" in subsidy
        assert "recommendation_id" in subsidy
        assert subsidy["recommendation_id"] == recommendation_id


def test_get_subsidies_for_recommendation_unauthenticated(client: TestClient):
    """Test de récupération des subventions pour une recommandation sans authentification"""
    recommendation_id = "rec1"
    response = client.get(
        f"{settings.API_PREFIX}/integrations/recommendations/{recommendation_id}/subsidies"
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data


def test_get_best_subsidies_for_recommendation_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération des meilleures subventions pour une recommandation avec authentification"""
    recommendation_id = "rec1"
    response = client.get(
        f"{settings.API_PREFIX}/integrations/recommendations/{recommendation_id}/best-subsidies",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Vérifier que les subventions sont triées par score de pertinence décroissant
    if len(data) > 1:
        assert data[0]["relevance_score"] >= data[1]["relevance_score"]


def test_get_subsidies_for_recommendation_set_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération des subventions pour un ensemble de recommandations avec authentification"""
    recommendation_set_id = "recset1"
    response = client.get(
        f"{settings.API_PREFIX}/integrations/recommendation-sets/{recommendation_set_id}/subsidies",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "recommendation_set_id" in data
    assert data["recommendation_set_id"] == recommendation_set_id
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_get_subsidies_for_optimization_measure_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération des subventions pour une mesure d'optimisation avec authentification"""
    measure_id = "measure1"
    response = client.get(
        f"{settings.API_PREFIX}/integrations/optimization/measures/{measure_id}/subsidies",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for subsidy in data:
        assert "subsidy_id" in subsidy
        assert "name" in subsidy
        assert "provider" in subsidy
        assert "description" in subsidy
        assert "measure_id" in subsidy
        assert subsidy["measure_id"] == measure_id


def test_get_subsidies_for_optimization_project_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération des subventions pour un projet d'optimisation avec authentification"""
    project_id = "project1"
    response = client.get(
        f"{settings.API_PREFIX}/integrations/optimization/projects/{project_id}/subsidies",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "project_id" in data
    assert data["project_id"] == project_id
    assert "measures" in data
    assert isinstance(data["measures"], list)


def test_get_subsidies_for_property_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération des subventions pour une propriété avec authentification"""
    property_id = "property1"
    response = client.get(
        f"{settings.API_PREFIX}/green-passport/properties/{property_id}/subsidies",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "property_id" in data
    assert data["property_id"] == property_id
    assert "property_address" in data
    assert "subsidies" in data
    assert isinstance(data["subsidies"], list)


def test_get_best_subsidies_for_property_authenticated(client: TestClient, auth_headers: dict):
    """Test de récupération des meilleures subventions pour une propriété avec authentification"""
    property_id = "property1"
    response = client.get(
        f"{settings.API_PREFIX}/green-passport/properties/{property_id}/best-subsidies",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    # Vérifier que les subventions sont triées par score de pertinence décroissant
    if len(data) > 1:
        assert data[0]["relevance_score"] >= data[1]["relevance_score"]
