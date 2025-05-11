"""
Tests pour les routes de subventions
----------------------------------
Tests unitaires pour les fonctionnalités de subventions
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status

from backend.subsidy.config import settings


def test_get_subsidies(client: TestClient):
    """Test de récupération de la liste des subventions"""
    response = client.get(f"{settings.API_PREFIX}/subsidies")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_get_subsidy_by_id(client: TestClient):
    """Test de récupération d'une subvention par son ID"""
    # Utiliser un ID de subvention qui existe dans les données de test
    subsidy_id = "sub1"
    response = client.get(f"{settings.API_PREFIX}/subsidies/{subsidy_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == subsidy_id
    assert "name" in data
    assert "description" in data
    assert "provider" in data
    assert "regions" in data
    assert "domains" in data
    assert "keywords" in data


def test_get_subsidy_by_id_not_found(client: TestClient):
    """Test de récupération d'une subvention qui n'existe pas"""
    subsidy_id = "non_existent_id"
    response = client.get(f"{settings.API_PREFIX}/subsidies/{subsidy_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "detail" in data


def test_search_subsidies(client: TestClient):
    """Test de recherche de subventions"""
    query = "énergie"
    response = client.get(
        f"{settings.API_PREFIX}/subsidies",
        params={"query": query}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_filter_subsidies_by_region(client: TestClient):
    """Test de filtrage des subventions par région"""
    region = "wallonie"
    response = client.get(f"{settings.API_PREFIX}/subsidies/regions/{region}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    # Vérifier que toutes les subventions retournées sont pour la région spécifiée
    for subsidy in data["results"]:
        assert region in [r.lower() for r in subsidy["regions"]]


def test_filter_subsidies_by_domain(client: TestClient):
    """Test de filtrage des subventions par domaine"""
    domain = "energy"
    response = client.get(f"{settings.API_PREFIX}/subsidies/domains/{domain}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    # Vérifier que toutes les subventions retournées sont pour le domaine spécifié
    for subsidy in data["results"]:
        assert domain in [d.lower() for d in subsidy["domains"]]


def test_filter_subsidies_by_user_type(client: TestClient):
    """Test de filtrage des subventions par type d'utilisateur"""
    user_type = "individual"
    response = client.get(f"{settings.API_PREFIX}/subsidies/user-types/{user_type}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)


def test_filter_subsidies_by_keyword(client: TestClient):
    """Test de filtrage des subventions par mot-clé"""
    keyword = "isolation"
    response = client.get(f"{settings.API_PREFIX}/subsidies/keywords/{keyword}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert isinstance(data["results"], list)
    # Vérifier que toutes les subventions retournées contiennent le mot-clé spécifié
    for subsidy in data["results"]:
        assert keyword.lower() in [k.lower() for k in subsidy["keywords"]]
