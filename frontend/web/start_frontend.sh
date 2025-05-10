#!/bin/bash

# Script pour démarrer le frontend de DynamoPro
# Ce script configure les variables d'environnement nécessaires et lance le serveur de développement

# Définir l'URL de l'API backend
export REACT_APP_API_URL="http://localhost:8020/api/v1"

# Afficher les informations de configuration
echo "====== Configuration de DynamoPro Frontend ======"
echo "API URL: $REACT_APP_API_URL"
echo "============================================="

# Installer les dépendances si nécessaire
if [ ! -d "node_modules" ]; then
  echo "Installation des dépendances..."
  npm install
fi

# Démarrer le serveur de développement
echo "Démarrage du serveur de développement..."
npm start
