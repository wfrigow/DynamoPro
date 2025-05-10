# DynamoPro

## Mission
Rendre l'amélioration de la durabilité (énergie, eau, déchets, biodiversité) simple, rentable et accessible à tous en Belgique.

## Description
DynamoPro est une plateforme intelligente qui utilise l'IA pour aider les particuliers, indépendants, et entreprises à optimiser leur consommation énergétique et d'eau, à identifier des opportunités d'économie, et à naviguer dans les subventions disponibles en Belgique.

## Composants Principaux
- **Interfaces Utilisateur** : Applications mobiles et web
- **Agent Manager** : Orchestrateur central des Agents IA
- **Agents Spécialisés** :
  - Data-Collector Agent
  - Optimizer Agent
  - Subsidy Agent
  - Procurement Agent
  - Monitoring Agent

## Structure du Projet
```
DynamoPro/
├── backend/                  # Services backend et microservices
│   ├── agent-manager/        # Orchestrateur central
│   ├── data-collector/       # Agent de collecte de données
│   ├── optimizer/            # Agent d'optimisation
│   ├── subsidy/              # Agent de gestion des subventions
│   ├── procurement/          # Agent de mise en relation avec les fournisseurs
│   ├── monitoring/           # Agent de suivi
│   └── common/               # Code partagé entre les agents
├── frontend/                 # Interfaces utilisateur
│   ├── web/                  # Application web responsive
│   ├── mobile/               # Applications mobiles (iOS & Android)
│   │   ├── ios/              # Code spécifique iOS
│   │   └── android/          # Code spécifique Android
│   └── supplier-portal/      # Portail pour les fournisseurs
├── database/                 # Scripts et schémas de base de données
│   ├── migrations/           # Scripts de migration
│   └── schemas/              # Définitions des schémas
├── infrastructure/           # Code d'infrastructure (IaC)
├── docs/                     # Documentation du projet
└── tests/                    # Tests (unitaires, intégration, e2e)
```

## Installation & Configuration
*À compléter*

## Développement
*À compléter*

## Licence
*À définir*
