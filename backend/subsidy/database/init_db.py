"""
Script d'initialisation de la base de données pour l'API de subventions
------------------------------------------------------------------
Crée les tables dans la base de données et ajoute des données de test
"""

import logging
from sqlalchemy.orm import Session
from . import models, database, crud
from ..auth import get_password_hash

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """Initialise la base de données et ajoute des données de test"""
    # Création des tables
    models.Base.metadata.create_all(bind=database.engine)
    logger.info("Tables créées dans la base de données")
    
    # Ajout de données de test
    db = database.SessionLocal()
    try:
        # Vérifier si des utilisateurs existent déjà
        user_count = db.query(models.User).count()
        if user_count == 0:
            add_test_data(db)
            logger.info("Données de test ajoutées à la base de données")
        else:
            logger.info("La base de données contient déjà des données, aucune donnée de test ajoutée")
    finally:
        db.close()


def add_test_data(db: Session):
    """Ajoute des données de test à la base de données"""
    # Création d'utilisateurs de test
    admin_user = crud.create_user(
        db=db,
        email="admin@dynamopro.be",
        password="admin123",
        first_name="Admin",
        last_name="DynamoPro",
        is_superuser=True
    )
    logger.info(f"Utilisateur administrateur créé: {admin_user.email}")
    
    test_user = crud.create_user(
        db=db,
        email="user@example.com",
        password="password123",
        first_name="Jean",
        last_name="Dupont"
    )
    logger.info(f"Utilisateur de test créé: {test_user.email}")
    
    # Création d'applications de test
    test_application = crud.create_application(
        db=db,
        subsidy_id="sub1",
        user_id=test_user.id,
        applicant_data={
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+32 470 12 34 56",
            "address": "Rue de la Science 123, 1040 Bruxelles",
            "userType": "individual"
        },
        property_data={
            "address": "Rue de la Science 123, 1040 Bruxelles",
            "type": "house",
            "yearBuilt": "1975"
        },
        project_data={
            "description": "Isolation de la toiture avec des matériaux écologiques",
            "estimatedCost": 5000,
            "estimatedCompletionDate": "2025-09-15",
            "workStarted": "no",
            "contractorSelected": "yes",
            "contractorName": "Iso-Pro SPRL"
        },
        bank_details={
            "accountHolder": "Jean Dupont",
            "iban": "BE68 5390 0754 7034"
        },
        subsidy_data={
            "id": "sub1",
            "name": "Prime Rénovation",
            "provider": "Bruxelles Environnement",
            "maxAmount": 10000,
            "percentage": 40,
            "calculatedAmount": 2000
        }
    )
    logger.info(f"Application de test créée: {test_application.reference_number}")
    
    # Ajout d'un document à l'application
    test_document = crud.create_document(
        db=db,
        application_id=test_application.id,
        name="facture.pdf",
        size=1024 * 1024,  # 1 MB
        content_type="application/pdf"
    )
    logger.info(f"Document de test créé: {test_document.name}")
    
    # Ajout d'une note à l'application
    test_note = crud.create_note(
        db=db,
        application_id=test_application.id,
        content="Veuillez fournir des informations supplémentaires sur les matériaux utilisés.",
        author="Admin DynamoPro",
        author_type="admin"
    )
    logger.info(f"Note de test créée pour l'application")
    
    # Création d'un brouillon de test
    test_draft = crud.create_draft(
        db=db,
        subsidy_id="sub2",
        user_id=test_user.id,
        applicant_data={
            "name": "Jean Dupont",
            "email": "jean.dupont@example.com",
            "phone": "+32 470 12 34 56",
            "address": "Rue de la Science 123, 1040 Bruxelles",
            "userType": "individual"
        },
        property_data={
            "address": "Rue de la Science 123, 1040 Bruxelles",
            "type": "house",
            "yearBuilt": "1975"
        }
    )
    logger.info(f"Brouillon de test créé: {test_draft.id}")


if __name__ == "__main__":
    logger.info("Initialisation de la base de données...")
    init_db()
    logger.info("Initialisation de la base de données terminée")
