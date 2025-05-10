#!/usr/bin/env python3
"""
Script de démarrage pour l'agent de subventions
----------------------------------------------
Ce script initialise la base de données de subventions et démarre le serveur
FastAPI pour l'agent de subventions.
"""

import os
import sys
import logging
import uvicorn

# Ajouter le répertoire parent au chemin pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from subsidy.subsidy_db import get_subsidy_database
from subsidy.subsidy_data import initialize_subsidy_database


def setup_logging():
    """Configure le système de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join(current_dir, "subsidy_agent.log"))
        ]
    )
    return logging.getLogger("subsidy_agent")


def init_database():
    """Initialise la base de données de subventions"""
    logger = logging.getLogger("subsidy_agent")
    
    try:
        # Créer le répertoire data s'il n'existe pas
        data_dir = os.path.join(current_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Créer le répertoire pour les applications
        applications_dir = os.path.join(data_dir, "applications")
        os.makedirs(applications_dir, exist_ok=True)
        
        # Créer le répertoire temp pour les fichiers téléchargés
        temp_dir = os.path.join(current_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Initialiser la base de données
        subsidy_db = get_subsidy_database()
        num_subsidies, num_providers = initialize_subsidy_database(subsidy_db)
        
        logger.info(f"Base de données initialisée avec {num_subsidies} subventions et {num_providers} fournisseurs")
        
        return True
    
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        return False


def start_server(port=8003, host="0.0.0.0", reload=True):
    """Démarre le serveur FastAPI"""
    logger = logging.getLogger("subsidy_agent")
    logger.info(f"Démarrage du serveur sur {host}:{port}")
    
    try:
        uvicorn.run(
            "subsidy.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du serveur: {str(e)}")


def main():
    """Fonction principale"""
    logger = setup_logging()
    logger.info("Démarrage de l'agent de subventions")
    
    # Initialiser la base de données
    if not init_database():
        logger.error("Impossible d'initialiser la base de données. Arrêt du programme.")
        sys.exit(1)
    
    # Démarrer le serveur
    start_server()


if __name__ == "__main__":
    main()
