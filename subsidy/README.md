# API de Subventions DynamoPro

## Vue d'ensemble

L'API de Subventions DynamoPro est un service backend qui fournit des données sur les subventions disponibles en Belgique pour promouvoir des pratiques durables. Elle permet également de gérer les applications de subventions et s'intègre avec d'autres services de la plateforme DynamoPro.

## Fonctionnalités

- **Authentification JWT** : Sécurisation des endpoints avec authentification par token JWT
- **Données de subventions enrichies** : Informations détaillées sur les subventions disponibles
- **Support multilingue** : Contenu disponible en français et en néerlandais
- **Gestion des applications** : Soumission, suivi et gestion des demandes de subventions
- **Intégration avec d'autres services** : Connexion avec les services de recommandations, d'optimisation et de passeport vert

## Structure du projet

```
backend/subsidy/
├── api/                  # Endpoints de l'API
│   ├── auth_routes.py    # Routes d'authentification
│   ├── application_routes.py # Routes pour les applications de subventions
│   ├── enriched_subsidy_routes.py # Routes pour les données de subventions
│   ├── integration_routes.py # Routes d'intégration avec d'autres services
│   └── green_passport_routes.py # Routes pour l'intégration avec le passeport vert
├── data/                 # Gestion des données
│   ├── application_data_manager.py # Gestionnaire des données d'applications
│   ├── subsidy_data_manager.py # Gestionnaire des données de subventions
│   ├── subsidies_extended.py # Données de subventions enrichies
│   └── subsidies_extended_part2.py # Données de subventions supplémentaires
├── models/               # Modèles de données
│   └── application_models.py # Modèles pour les applications de subventions
├── tests/                # Tests unitaires et d'intégration
│   ├── conftest.py       # Configuration des tests
│   ├── test_auth.py      # Tests d'authentification
│   ├── test_applications.py # Tests des applications de subventions
│   ├── test_subsidies.py # Tests des données de subventions
│   └── test_integrations.py # Tests des intégrations
├── auth.py               # Logique d'authentification
├── config.py             # Configuration de l'API
└── start_enriched_subsidy_api.py # Point d'entrée de l'API
```

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Rust (pour certaines dépendances)

## Installation

1. **Installer Rust (si nécessaire)**

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. **Installer les dépendances Python**

```bash
cd /chemin/vers/DynamoPro
pip install -r backend/requirements.txt
```

3. **Configuration**

Créez un fichier `.env` dans le répertoire `backend/subsidy` avec les variables suivantes :

```
SECRET_KEY=votre_clé_secrète_ici
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./subsidy.db
RECOMMENDATION_SERVICE_URL=http://localhost:8002
OPTIMIZATION_SERVICE_URL=http://localhost:8003
GREEN_PASSPORT_SERVICE_URL=http://localhost:8004
CORS_ORIGINS=["http://localhost:3000"]
```

## Exécution

Pour démarrer l'API de subventions :

```bash
cd /chemin/vers/DynamoPro
python -m backend.subsidy.start_enriched_subsidy_api
```

L'API sera accessible à l'adresse `http://localhost:8001` et la documentation Swagger à `http://localhost:8001/api/v1/docs`.

## Tests

Pour exécuter les tests unitaires et d'intégration :

```bash
cd /chemin/vers/DynamoPro/backend/subsidy
python -m tests.run_tests
```

## Endpoints principaux

### Authentification

- `POST /api/v1/auth/token` - Obtenir un token JWT
- `GET /api/v1/auth/me` - Obtenir les informations de l'utilisateur connecté

### Subventions

- `GET /api/v1/subsidies` - Liste des subventions disponibles
- `GET /api/v1/subsidies/{subsidy_id}` - Détails d'une subvention
- `GET /api/v1/subsidies/regions/{region}` - Subventions par région
- `GET /api/v1/subsidies/domains/{domain}` - Subventions par domaine
- `GET /api/v1/subsidies/keywords/{keyword}` - Subventions par mot-clé

### Applications de subventions

- `POST /api/v1/subsidies/{subsidy_id}/applications` - Soumettre une application
- `POST /api/v1/subsidies/{subsidy_id}/applications/drafts` - Sauvegarder un brouillon
- `GET /api/v1/subsidies/applications/{application_id}` - Détails d'une application
- `POST /api/v1/subsidies/applications/{application_id}/notes` - Ajouter une note
- `POST /api/v1/subsidies/applications/{application_id}/documents/{document_id}` - Télécharger un document

### Intégrations

- `GET /api/v1/integrations/recommendations/{recommendation_id}/subsidies` - Subventions pour une recommandation
- `GET /api/v1/green-passport/properties/{property_id}/subsidies` - Subventions pour une propriété

## Modèle de données

### Subvention

```json
{
  "id": "sub1",
  "name": "Prime Rénovation",
  "provider": "Bruxelles Environnement",
  "description": "Prime pour la rénovation énergétique des bâtiments",
  "regions": ["bruxelles"],
  "domains": ["energy", "renovation"],
  "max_amount": 10000,
  "percentage": 40,
  "keywords": ["isolation", "chauffage", "énergie"]
}
```

### Application de subvention

```json
{
  "id": "app1",
  "subsidyId": "sub1",
  "status": "submitted",
  "submissionDate": "2025-05-07T12:00:00Z",
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
  "documents": [
    {
      "id": "doc1",
      "name": "facture.pdf",
      "status": "pending",
      "uploadDate": "2025-05-07T12:30:00Z"
    }
  ]
}
```

## Intégration avec le frontend

Le frontend peut se connecter à l'API en utilisant le service centralisé `api.ts` qui gère l'authentification et les appels API. Exemple d'utilisation :

```typescript
import { apiService } from '../services/api';
import { SubsidyService } from '../services/SubsidyService';

// Utilisation du service de subventions
const subsidyService = new SubsidyService();

// Récupérer les détails d'une subvention
const subsidyDetails = await subsidyService.getSubsidyDetails('sub1');

// Soumettre une application
const applicationData = {
  applicant: { /* ... */ },
  property: { /* ... */ },
  project: { /* ... */ },
  bankDetails: { /* ... */ }
};
const result = await subsidyService.submitApplication('sub1', applicationData);
```

## Prochaines étapes

1. Implémenter une base de données réelle pour stocker les utilisateurs et les applications
2. Ajouter des fonctionnalités d'inscription et de réinitialisation de mot de passe
3. Améliorer la validation des données et la gestion des erreurs
4. Ajouter des tests de performance et de charge
5. Implémenter un système de notifications pour les mises à jour des applications
