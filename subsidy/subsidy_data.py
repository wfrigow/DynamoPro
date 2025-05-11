"""
Données de subventions pour la Belgique
--------------------------------------
Module contenant les données structurées des subventions 
et aides financières disponibles en Belgique.
"""

from typing import List, Dict, Any
import uuid
from datetime import datetime

from subsidy_db import (
    SubsidyProvider, Subsidy, SubsidyCondition, RequiredDocument,
    SubsidyType, SubsidyConditionType, SubsidyDocumentType, SubsidyKeyword
)

def load_subsidy_providers() -> List[SubsidyProvider]:
    """Charge les données des fournisseurs de subventions"""
    providers = [
        SubsidyProvider(
            id="rw-energie",
            name="Service Public de Wallonie - Énergie",
            type="public",
            level="regional",
            website="https://energie.wallonie.be",
            contact_email="energie@spw.wallonie.be",
            contact_phone="+32 81 33 55 06"
        ),
        SubsidyProvider(
            id="rb-environnement",
            name="Bruxelles Environnement",
            type="public",
            level="regional",
            website="https://environnement.brussels",
            contact_email="info@environnement.brussels",
            contact_phone="+32 2 775 75 75"
        ),
        SubsidyProvider(
            id="vea",
            name="Agence flamande de l'Énergie",
            type="public",
            level="regional",
            website="https://www.energiesparen.be",
            contact_email="energie@vlaanderen.be",
            contact_phone="+32 2 553 46 00"
        ),
        SubsidyProvider(
            id="spf-finance",
            name="Service Public Fédéral Finances",
            type="public",
            level="federal",
            website="https://finances.belgium.be",
            contact_email="info.tax@minfin.fed.be",
            contact_phone="+32 2 572 57 57"
        ),
        SubsidyProvider(
            id="awex",
            name="Agence wallonne à l'Exportation et aux Investissements étrangers",
            type="public",
            level="regional",
            website="https://www.awex.be",
            contact_email="info@awex.be",
            contact_phone="+32 81 33 28 50"
        ),
        SubsidyProvider(
            id="hub-brussels",
            name="hub.brussels",
            type="public",
            level="regional",
            website="https://hub.brussels",
            contact_email="info@hub.brussels",
            contact_phone="+32 2 800 40 00"
        ),
        SubsidyProvider(
            id="flanders-innovation",
            name="Agence pour l'Innovation et l'Entrepreneuriat (VLAIO)",
            type="public",
            level="regional",
            website="https://www.vlaio.be",
            contact_email="info@vlaio.be",
            contact_phone="+32 800 20 555"
        ),
        SubsidyProvider(
            id="rw-eau",
            name="Service Public de Wallonie - Environnement",
            type="public",
            level="regional",
            website="https://environnement.wallonie.be",
            contact_email="eau@spw.wallonie.be",
            contact_phone="+32 81 33 50 50"
        )
    ]
    
    return providers

def load_subsidy_data() -> List[Subsidy]:
    """Charge les données des subventions"""
    
    # Documents courants pour les subventions
    identity_doc = RequiredDocument(
        type=SubsidyDocumentType.IDENTITY,
        description="Copie de la carte d'identité du demandeur"
    )
    
    ownership_doc = RequiredDocument(
        type=SubsidyDocumentType.OWNERSHIP,
        description="Preuve de propriété ou bail"
    )
    
    invoice_doc = RequiredDocument(
        type=SubsidyDocumentType.INVOICE,
        description="Facture détaillée des travaux"
    )
    
    quote_doc = RequiredDocument(
        type=SubsidyDocumentType.QUOTE,
        description="Devis détaillé des travaux"
    )
    
    # Liste des subventions pour la Wallonie - Énergie
    wallonia_energy_subsidies = [
        # Isolation toiture
        Subsidy(
            id=str(uuid.uuid4()),
            name="Prime Énergie - Isolation Toiture (Wallonie)",
            description="Prime pour l'isolation thermique du toit ou des combles dans une habitation existante.",
            provider_id="rw-energie",
            regions=["wallonie"],
            eligible_user_types=["individual", "self_employed", "small_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.INSULATION, SubsidyKeyword.RENOVATION],
            max_amount=2000,
            percentage=35,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Le coefficient de résistance thermique R doit être ≥ 4,5 m²K/W",
                    technical_parameter="r_value",
                    technical_value=4.5
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.PROVIDER,
                    description="Les travaux doivent être réalisés par un entrepreneur enregistré"
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.TEMPORAL,
                    description="Les travaux doivent être réalisés après le 1er janvier 2023"
                )
            ],
            required_documents=[
                identity_doc, 
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.TECHNICAL_SPEC,
                    description="Fiche technique du matériau isolant utilisé"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.CERTIFICATE,
                    description="Attestation de l'entrepreneur"
                )
            ],
            application_process="Demande en ligne via le portail Energie de la Région Wallonne.",
            documentation_url="https://energie.wallonie.be/fr/prime-isolation-du-toit.html",
            application_url="https://monespace.wallonie.be",
            typical_processing_time_days=60,
            active=True
        ),
        
        # Pompe à chaleur
        Subsidy(
            id=str(uuid.uuid4()),
            name="Prime Énergie - Pompe à Chaleur (Wallonie)",
            description="Prime pour l'installation d'une pompe à chaleur pour le chauffage ou combiné eau chaude sanitaire.",
            provider_id="rw-energie",
            regions=["wallonie"],
            eligible_user_types=["individual", "self_employed", "small_business", "medium_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.HEAT_PUMP, SubsidyKeyword.HEATING],
            max_amount=4000,
            percentage=30,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Coefficient de performance saisonnier (SCOP) ≥ 3,5",
                    technical_parameter="scop",
                    technical_value=3.5
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.PROVIDER,
                    description="Installation réalisée par un installateur certifié"
                )
            ],
            required_documents=[
                identity_doc,
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.TECHNICAL_SPEC,
                    description="Fiche technique de la pompe à chaleur"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.CERTIFICATE,
                    description="Certificat de l'installateur"
                )
            ],
            application_process="Demande en ligne via le portail Energie de la Région Wallonne.",
            documentation_url="https://energie.wallonie.be/fr/prime-pompe-a-chaleur.html",
            application_url="https://monespace.wallonie.be",
            typical_processing_time_days=60,
            active=True
        ),
        
        # Panneaux photovoltaïques
        Subsidy(
            id=str(uuid.uuid4()),
            name="Prime Énergie - Panneaux Photovoltaïques (Wallonie)",
            description="Prime pour l'installation de panneaux photovoltaïques pour la production d'électricité.",
            provider_id="rw-energie",
            regions=["wallonie"],
            eligible_user_types=["individual", "self_employed", "small_business", "medium_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.SOLAR],
            max_amount=1500,
            percentage=20,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.PROVIDER,
                    description="Installation réalisée par un installateur certifié"
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Panneau avec rendement ≥ 21%",
                    technical_parameter="efficiency",
                    technical_value=21
                )
            ],
            required_documents=[
                identity_doc,
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.CERTIFICATE,
                    description="Certificat de l'installateur"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.TECHNICAL_SPEC,
                    description="Fiche technique des panneaux photovoltaïques"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.PLAN,
                    description="Schéma d'implantation des panneaux"
                )
            ],
            application_process="Demande en ligne via le portail Energie de la Région Wallonne.",
            documentation_url="https://energie.wallonie.be/fr/prime-photovoltaique.html",
            application_url="https://monespace.wallonie.be",
            typical_processing_time_days=60,
            active=True
        ),
        
        # Audit énergétique
        Subsidy(
            id=str(uuid.uuid4()),
            name="Primes Rénovation - Audit Énergétique (Wallonie)",
            description="Prime pour la réalisation d'un audit énergétique par un auditeur agréé.",
            provider_id="rw-energie",
            regions=["wallonie"],
            eligible_user_types=["individual", "self_employed", "small_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.AUDIT, SubsidyKeyword.RENOVATION],
            max_amount=900,
            percentage=70,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.PROVIDER,
                    description="L'audit doit être réalisé par un auditeur agréé PAE (Procédure d'Avis Énergétique)"
                )
            ],
            required_documents=[
                identity_doc,
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.CERTIFICATE,
                    description="Copie du rapport d'audit énergétique"
                )
            ],
            application_process="Demande en ligne via le portail Energie de la Région Wallonne.",
            documentation_url="https://energie.wallonie.be/fr/audit-energetique.html",
            application_url="https://monespace.wallonie.be",
            typical_processing_time_days=45,
            active=True
        ),
        
        # Remplacement châssis/fenêtres
        Subsidy(
            id=str(uuid.uuid4()),
            name="Prime Rénovation - Remplacement Châssis/Fenêtres (Wallonie)",
            description="Prime pour le remplacement de châssis et fenêtres par du vitrage à haut rendement.",
            provider_id="rw-energie",
            regions=["wallonie"],
            eligible_user_types=["individual", "self_employed", "small_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.WINDOWS, SubsidyKeyword.RENOVATION],
            max_amount=1500,
            percentage=30,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Le coefficient de transmission thermique U du vitrage doit être ≤ 1,0 W/m²K",
                    technical_parameter="u_value",
                    technical_value=1.0
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.PROVIDER,
                    description="Installation réalisée par un entrepreneur enregistré"
                )
            ],
            required_documents=[
                identity_doc,
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.TECHNICAL_SPEC,
                    description="Fiche technique du vitrage"
                )
            ],
            application_process="Demande en ligne via le portail Energie de la Région Wallonne.",
            documentation_url="https://energie.wallonie.be/fr/prime-renovation-chassis.html",
            application_url="https://monespace.wallonie.be",
            typical_processing_time_days=60,
            active=True
        )
    ]
    
    # Liste des subventions pour la Wallonie - Eau
    wallonia_water_subsidies = [
        # Récupération eau de pluie
        Subsidy(
            id=str(uuid.uuid4()),
            name="Prime Eau - Récupération Eau de Pluie (Wallonie)",
            description="Prime pour l'installation d'un système de récupération et d'utilisation de l'eau de pluie.",
            provider_id="rw-eau",
            regions=["wallonie"],
            eligible_user_types=["individual", "self_employed", "small_business"],
            domains=["water"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.RAINWATER, SubsidyKeyword.WATER_SAVING],
            max_amount=1000,
            percentage=25,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="La citerne doit avoir une capacité minimale de 5000 litres",
                    technical_parameter="capacity",
                    technical_value=5000
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="La citerne doit être raccordée à au moins un WC ou un lave-linge"
                )
            ],
            required_documents=[
                identity_doc,
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.TECHNICAL_SPEC,
                    description="Schéma d'installation du système"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.PHOTOS,
                    description="Photos de l'installation réalisée"
                )
            ],
            application_process="Demande auprès de la commune ou de l'intercommunale compétente.",
            documentation_url="https://environnement.wallonie.be/eau/prime-eau-pluie.html",
            typical_processing_time_days=45,
            active=True
        )
    ]
    
    # Liste des subventions pour Bruxelles Environnement
    brussels_subsidies = [
        # Isolation toiture
        Subsidy(
            id=str(uuid.uuid4()),
            name="Prime Rénolution - Isolation Toiture (Bruxelles)",
            description="Prime pour l'isolation thermique du toit ou des combles dans un bâtiment existant à Bruxelles.",
            provider_id="rb-environnement",
            regions=["bruxelles"],
            eligible_user_types=["individual", "self_employed", "small_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.INSULATION, SubsidyKeyword.RENOVATION],
            percentage=40,
            max_amount=2500,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Le coefficient de résistance thermique R doit être ≥ 4,5 m²K/W",
                    technical_parameter="r_value",
                    technical_value=4.5
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.PROVIDER,
                    description="Les travaux doivent être réalisés par un entrepreneur enregistré"
                )
            ],
            required_documents=[
                identity_doc,
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.TECHNICAL_SPEC,
                    description="Fiche technique du matériau isolant"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.PHOTOS,
                    description="Photos avant et après travaux"
                )
            ],
            application_process="Demande en ligne via le guichet électronique IRISbox.",
            documentation_url="https://renolution.brussels/fr/prime-isolation",
            application_url="https://irisbox.brussels",
            typical_processing_time_days=90,
            active=True
        ),
        
        # Citerne eau de pluie
        Subsidy(
            id=str(uuid.uuid4()),
            name="Prime Rénolution - Citerne Eau de Pluie (Bruxelles)",
            description="Prime pour l'installation ou la rénovation d'une citerne d'eau de pluie.",
            provider_id="rb-environnement",
            regions=["bruxelles"],
            eligible_user_types=["individual", "self_employed", "small_business"],
            domains=["water"],
            subsidy_type=SubsidyType.PRIME,
            keywords=[SubsidyKeyword.RAINWATER, SubsidyKeyword.WATER_SAVING],
            max_amount=1500,
            percentage=50,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Volume minimum de 1000 litres",
                    technical_parameter="capacity",
                    technical_value=1000
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Raccordement à au moins un point d'utilisation (WC, lave-linge, etc.)"
                )
            ],
            required_documents=[
                identity_doc,
                ownership_doc,
                invoice_doc,
                RequiredDocument(
                    type=SubsidyDocumentType.PLAN,
                    description="Plan de l'installation"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.PHOTOS,
                    description="Photos de l'installation"
                )
            ],
            application_process="Demande en ligne via le guichet électronique IRISbox.",
            documentation_url="https://renolution.brussels/fr/prime-eau",
            application_url="https://irisbox.brussels",
            typical_processing_time_days=90,
            active=True
        )
    ]
    
    # Liste des subventions fédérales
    federal_subsidies = [
        # Réduction fiscale pour investissements économiseurs d'énergie
        Subsidy(
            id=str(uuid.uuid4()),
            name="Réduction Fiscale - Investissements Économiseurs d'Énergie",
            description="Déduction fiscale pour les entreprises investissant dans des mesures d'économie d'énergie.",
            provider_id="spf-finance",
            regions=["wallonie", "flandre", "bruxelles"],
            eligible_user_types=["self_employed", "small_business", "medium_business", "large_business"],
            domains=["energy"],
            subsidy_type=SubsidyType.TAX_REDUCTION,
            keywords=[SubsidyKeyword.RENOVATION, SubsidyKeyword.HEATING, SubsidyKeyword.INSULATION],
            percentage=13.5,
            conditions=[
                SubsidyCondition(
                    type=SubsidyConditionType.TECHNICAL,
                    description="Les investissements doivent concerner l'utilisation rationnelle de l'énergie"
                ),
                SubsidyCondition(
                    type=SubsidyConditionType.ADMINISTRATIVE,
                    description="Investissements neufs et amortissables"
                )
            ],
            required_documents=[
                RequiredDocument(
                    type=SubsidyDocumentType.TAX,
                    description="Formulaire de déclaration fiscale"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.INVOICE,
                    description="Factures des investissements"
                ),
                RequiredDocument(
                    type=SubsidyDocumentType.TECHNICAL_SPEC,
                    description="Documentation technique des investissements"
                )
            ],
            application_process="Via la déclaration fiscale annuelle.",
            documentation_url="https://finances.belgium.be/fr/entreprises/impot_des_societes/avantages_fiscaux/deduction_pour_investissement/economiseurs_energie",
            typical_processing_time_days=180,  # Traitement fiscal
            active=True
        )
    ]
    
    # Fusionner toutes les subventions
    all_subsidies = (
        wallonia_energy_subsidies +
        wallonia_water_subsidies +
        brussels_subsidies +
        federal_subsidies
    )
    
    return all_subsidies

def initialize_subsidy_database(db):
    """Initialise la base de données avec les données de subventions"""
    # Ajouter les fournisseurs
    providers = load_subsidy_providers()
    for provider in providers:
        db.add_provider(provider)
    
    # Ajouter les subventions
    subsidies = load_subsidy_data()
    for subsidy in subsidies:
        db.add_subsidy(subsidy)
    
    return len(subsidies), len(providers)
