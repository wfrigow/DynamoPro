#!/usr/bin/env python
"""
Script pour initialiser la base de données et démarrer l'API de subventions
------------------------------------------------------------------------
"""

import os
import logging
import uvicorn
from database.init_db import init_db

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """
    Fonction principale pour initialiser la base de données et démarrer l'API
    """
    # Initialiser la base de données
    logger.info("Initialisation de la base de données...")
    init_db()
    logger.info("Base de données initialisée avec succès")
    
    # Démarrer l'API
    logger.info("Démarrage de l'API de subventions...")
    uvicorn.run("start_enriched_subsidy_api:app", host="0.0.0.0", port=8001, reload=True)


if __name__ == "__main__":
    main()
