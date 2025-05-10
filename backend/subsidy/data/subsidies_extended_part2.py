"""
Module contenant des données supplémentaires de subventions disponibles en Belgique.
Ce fichier complète subsidies_extended.py avec plus de subventions.
"""

from datetime import date
from .subsidies_extended import (
    EnrichedSubsidy, 
    TranslatedText, 
    RequiredDocument,
    Region, 
    Domain, 
    UserType, 
    DocumentType, 
    SubsidyStatus,
    Language,
    identity_card_doc,
    property_proof_doc,
    quote_doc,
    invoice_doc,
    technical_sheet_doc,
    photos_doc,
    contractor_cert_doc
)

# Documents spécifiques supplémentaires
energy_audit_doc = RequiredDocument(
    id="doc_energy_audit",
    name=TranslatedText(
        fr="Audit énergétique",
        nl="Energieaudit"
    ),
    description=TranslatedText(
        fr="Rapport d'audit énergétique réalisé par un auditeur agréé",
        nl="Energieauditrapport uitgevoerd door een erkende auditor"
    ),
    type=DocumentType.CERTIFICATE
)

peb_certificate_doc = RequiredDocument(
    id="doc_peb",
    name=TranslatedText(
        fr="Certificat PEB",
        nl="EPB-certificaat"
    ),
    description=TranslatedText(
        fr="Certificat de Performance Énergétique du Bâtiment",
        nl="Energieprestatiecertificaat van het gebouw"
    ),
    type=DocumentType.CERTIFICATE
)

urban_planning_permit_doc = RequiredDocument(
    id="doc_urban_permit",
    name=TranslatedText(
        fr="Permis d'urbanisme",
        nl="Stedenbouwkundige vergunning"
    ),
    description=TranslatedText(
        fr="Permis d'urbanisme pour les travaux de rénovation",
        nl="Stedenbouwkundige vergunning voor renovatiewerken"
    ),
    type=DocumentType.PERMIT
)

income_proof_doc = RequiredDocument(
    id="doc_income",
    name=TranslatedText(
        fr="Preuve de revenus",
        nl="Inkomensbewijs"
    ),
    description=TranslatedText(
        fr="Avertissement-extrait de rôle ou autre preuve de revenus",
        nl="Aanslagbiljet of ander inkomensbewijs"
    ),
    type=DocumentType.TAX
)

# Subventions supplémentaires
MORE_ENRICHED_SUBSIDIES = [
    # 3. Prime Pompe à Chaleur (Wallonie)
    EnrichedSubsidy(
        id="subsidy-pompe-chaleur-wallonie",
        name=TranslatedText(
            fr="Prime Énergie - Pompe à Chaleur",
            nl="Energiepremie - Warmtepomp"
        ),
        provider=TranslatedText(
            fr="Service Public de Wallonie - Énergie",
            nl="Waalse Overheidsdienst - Energie"
        ),
        description=TranslatedText(
            fr="Prime pour l'installation d'une pompe à chaleur pour le chauffage ou combiné eau chaude sanitaire. Cette prime encourage l'utilisation de technologies renouvelables pour réduire la consommation d'énergie fossile.",
            nl="Premie voor de installatie van een warmtepomp voor verwarming of gecombineerd met sanitair warm water. Deze premie moedigt het gebruik van hernieuwbare technologieën aan om het verbruik van fossiele energie te verminderen."
        ),
        regions=[Region.WALLONIE],
        domains=[Domain.ENERGY],
        max_amount=4000,
        percentage=30,
        conditions=TranslatedText(
            fr="La pompe à chaleur doit respecter des exigences minimales de performance. L'installation doit être réalisée par un installateur certifié QualiPAC.",
            nl="De warmtepomp moet voldoen aan minimale prestatievereisten. De installatie moet worden uitgevoerd door een QualiPAC-gecertificeerde installateur."
        ),
        eligibility=[
            TranslatedText(
                fr="Habitation située en Wallonie",
                nl="Woning gelegen in Wallonië"
            ),
            TranslatedText(
                fr="Coefficient de performance saisonnier (SCOP) ≥ 3,5",
                nl="Seizoensgebonden prestatiecoëfficiënt (SCOP) ≥ 3,5"
            ),
            TranslatedText(
                fr="Installation par un entrepreneur certifié QualiPAC",
                nl="Installatie door een QualiPAC-gecertificeerde aannemer"
            ),
            TranslatedText(
                fr="Demande introduite dans les 4 mois suivant la facture finale",
                nl="Aanvraag ingediend binnen 4 maanden na de eindfactuur"
            )
        ],
        user_types=[UserType.INDIVIDUAL, UserType.SELF_EMPLOYED, UserType.SMALL_BUSINESS],
        required_documents=[
            identity_card_doc,
            property_proof_doc,
            quote_doc,
            invoice_doc,
            technical_sheet_doc,
            contractor_cert_doc
        ],
        application_process=TranslatedText(
            fr="Demande en ligne via le portail Energie de la Région Wallonne. Vous devez créer un compte et suivre les étapes indiquées.",
            nl="Online aanvraag via het Energieportaal van het Waalse Gewest. U moet een account aanmaken en de aangegeven stappen volgen."
        ),
        documentation_url={
            Language.FR: "https://energie.wallonie.be/fr/prime-pompe-a-chaleur.html",
            Language.NL: "https://energie.wallonie.be/nl/premie-warmtepomp.html"
        },
        status=SubsidyStatus.ACTIVE,
        keywords=[
            TranslatedText(fr="Pompe à chaleur", nl="Warmtepomp"),
            TranslatedText(fr="Chauffage", nl="Verwarming"),
            TranslatedText(fr="Énergie renouvelable", nl="Hernieuwbare energie"),
            TranslatedText(fr="Économie d'énergie", nl="Energiebesparing")
        ],
        min_year_built=None,
        max_year_built=None
    ),
    
    # 4. Prime Panneaux Photovoltaïques (Flandre)
    EnrichedSubsidy(
        id="subsidy-photovoltaique-flandre",
        name=TranslatedText(
            fr="Prime Panneaux Photovoltaïques",
            nl="Premie Zonnepanelen"
        ),
        provider=TranslatedText(
            fr="Agence Flamande de l'Énergie",
            nl="Vlaams Energieagentschap"
        ),
        description=TranslatedText(
            fr="Prime pour l'installation de panneaux photovoltaïques pour la production d'électricité. Cette prime vise à encourager l'utilisation d'énergie solaire pour réduire l'empreinte carbone.",
            nl="Premie voor de installatie van zonnepanelen voor elektriciteitsproductie. Deze premie is bedoeld om het gebruik van zonne-energie aan te moedigen om de koolstofvoetafdruk te verminderen."
        ),
        regions=[Region.FLANDRE],
        domains=[Domain.ENERGY],
        max_amount=1500,
        percentage=20,
        conditions=TranslatedText(
            fr="L'installation doit être réalisée par un installateur certifié. Les panneaux doivent avoir un rendement minimum de 21%.",
            nl="De installatie moet worden uitgevoerd door een gecertificeerde installateur. De panelen moeten een minimaal rendement van 21% hebben."
        ),
        eligibility=[
            TranslatedText(
                fr="Bâtiment situé en Flandre",
                nl="Gebouw gelegen in Vlaanderen"
            ),
            TranslatedText(
                fr="Installation par un professionnel certifié",
                nl="Installatie door een gecertificeerde professional"
            ),
            TranslatedText(
                fr="Mise en service après le 1er janvier 2021",
                nl="Inbedrijfstelling na 1 januari 2021"
            ),
            TranslatedText(
                fr="Rendement minimum des panneaux de 21%",
                nl="Minimaal rendement van de panelen van 21%"
            )
        ],
        user_types=[UserType.INDIVIDUAL, UserType.SELF_EMPLOYED, UserType.SMALL_BUSINESS, UserType.MEDIUM_BUSINESS],
        required_documents=[
            identity_card_doc,
            property_proof_doc,
            quote_doc,
            invoice_doc,
            technical_sheet_doc,
            contractor_cert_doc
        ],
        application_process=TranslatedText(
            fr="Demande en ligne via le site de l'Agence Flamande de l'Énergie. La demande doit être introduite dans les 12 mois suivant la mise en service.",
            nl="Online aanvraag via de website van het Vlaams Energieagentschap. De aanvraag moet worden ingediend binnen 12 maanden na de inbedrijfstelling."
        ),
        documentation_url={
            Language.FR: "https://www.energiesparen.be/premie-zonnepanelen",
            Language.NL: "https://www.energiesparen.be/premie-zonnepanelen"
        },
        status=SubsidyStatus.ACTIVE,
        keywords=[
            TranslatedText(fr="Solaire", nl="Zonne-energie"),
            TranslatedText(fr="Photovoltaïque", nl="Fotovoltaïsch"),
            TranslatedText(fr="Énergie verte", nl="Groene energie"),
            TranslatedText(fr="Production d'électricité", nl="Elektriciteitsproductie")
        ],
        min_year_built=None,
        max_year_built=None
    ),
    
    # 5. Prêt à taux zéro - Énergie Verte (Wallonie)
    EnrichedSubsidy(
        id="subsidy-pret-zero-energie-wallonie",
        name=TranslatedText(
            fr="Prêt à taux zéro - Énergie Verte",
            nl="Renteloze lening - Groene Energie"
        ),
        provider=TranslatedText(
            fr="Fonds du Logement Wallon",
            nl="Waals Woningfonds"
        ),
        description=TranslatedText(
            fr="Prêt sans intérêt pour financer des travaux d'amélioration énergétique dans votre habitation. Ce prêt permet d'étaler le coût des travaux sur plusieurs années sans frais supplémentaires.",
            nl="Renteloze lening om energieverbeterende werkzaamheden in uw woning te financieren. Met deze lening kunt u de kosten van de werkzaamheden over meerdere jaren spreiden zonder extra kosten."
        ),
        regions=[Region.WALLONIE],
        domains=[Domain.ENERGY, Domain.RENOVATION],
        max_amount=30000,
        percentage=None,
        conditions=TranslatedText(
            fr="Le prêt est accessible aux propriétaires occupants dont les revenus ne dépassent pas certains plafonds. La durée maximale du prêt est de 15 ans.",
            nl="De lening is toegankelijk voor eigenaar-bewoners met een inkomen dat bepaalde plafonds niet overschrijdt. De maximale looptijd van de lening is 15 jaar."
        ),
        eligibility=[
            TranslatedText(
                fr="Être propriétaire occupant",
                nl="Eigenaar-bewoner zijn"
            ),
            TranslatedText(
                fr="Revenus du ménage ne dépassant pas certains plafonds",
                nl="Gezinsinkomen dat bepaalde plafonds niet overschrijdt"
            ),
            TranslatedText(
                fr="Habitation située en Wallonie et existante depuis au moins 15 ans",
                nl="Woning gelegen in Wallonië en minstens 15 jaar oud"
            ),
            TranslatedText(
                fr="Travaux visant à améliorer la performance énergétique",
                nl="Werkzaamheden gericht op het verbeteren van de energieprestatie"
            )
        ],
        user_types=[UserType.INDIVIDUAL],
        required_documents=[
            identity_card_doc,
            property_proof_doc,
            quote_doc,
            income_proof_doc,
            energy_audit_doc
        ],
        application_process=TranslatedText(
            fr="Demande auprès du Fonds du Logement Wallon. Un audit énergétique préalable est nécessaire pour déterminer les travaux prioritaires.",
            nl="Aanvraag bij het Waals Woningfonds. Een voorafgaande energieaudit is nodig om de prioritaire werkzaamheden te bepalen."
        ),
        documentation_url={
            Language.FR: "https://www.flw.be/pret-a-taux-zero",
            Language.NL: "https://www.flw.be/nl/renteloze-lening"
        },
        status=SubsidyStatus.ACTIVE,
        keywords=[
            TranslatedText(fr="Prêt", nl="Lening"),
            TranslatedText(fr="Énergie verte", nl="Groene energie"),
            TranslatedText(fr="Rénovation", nl="Renovatie"),
            TranslatedText(fr="Financement", nl="Financiering")
        ],
        min_year_built=None,
        max_year_built=2008  # Habitations d'au moins 15 ans
    ),
    
    # 6. Prime Citerne d'eau de pluie (Bruxelles)
    EnrichedSubsidy(
        id="subsidy-citerne-eau-bruxelles",
        name=TranslatedText(
            fr="Prime Citerne d'eau de pluie",
            nl="Premie Regenwaterput"
        ),
        provider=TranslatedText(
            fr="Bruxelles Environnement",
            nl="Leefmilieu Brussel"
        ),
        description=TranslatedText(
            fr="Prime pour l'installation d'une citerne d'eau de pluie pour la récupération et l'utilisation de l'eau pluviale. Cette prime encourage la gestion durable de l'eau.",
            nl="Premie voor de installatie van een regenwaterput voor het opvangen en gebruiken van regenwater. Deze premie moedigt duurzaam waterbeheer aan."
        ),
        regions=[Region.BRUXELLES],
        domains=[Domain.WATER],
        max_amount=3500,
        percentage=50,
        conditions=TranslatedText(
            fr="La citerne doit avoir une capacité minimale de 1000 litres et être raccordée à au moins un point d'utilisation (WC, machine à laver, etc.).",
            nl="De tank moet een minimale capaciteit van 1000 liter hebben en aangesloten zijn op ten minste één gebruikspunt (toilet, wasmachine, enz.)."
        ),
        eligibility=[
            TranslatedText(
                fr="Bâtiment situé dans la Région de Bruxelles-Capitale",
                nl="Gebouw gelegen in het Brussels Hoofdstedelijk Gewest"
            ),
            TranslatedText(
                fr="Capacité minimale de la citerne de 1000 litres",
                nl="Minimale capaciteit van de tank van 1000 liter"
            ),
            TranslatedText(
                fr="Raccordement à au moins un point d'utilisation",
                nl="Aansluiting op ten minste één gebruikspunt"
            ),
            TranslatedText(
                fr="Installation par un professionnel",
                nl="Installatie door een professional"
            )
        ],
        user_types=[UserType.INDIVIDUAL, UserType.SELF_EMPLOYED, UserType.NON_PROFIT, UserType.PUBLIC_ENTITY],
        required_documents=[
            identity_card_doc,
            property_proof_doc,
            quote_doc,
            invoice_doc,
            photos_doc,
            technical_sheet_doc
        ],
        application_process=TranslatedText(
            fr="Demande via le formulaire en ligne sur le site de Bruxelles Environnement. Les documents doivent être soumis dans les 12 mois suivant la dernière facture.",
            nl="Aanvraag via het online formulier op de website van Leefmilieu Brussel. De documenten moeten worden ingediend binnen 12 maanden na de laatste factuur."
        ),
        documentation_url={
            Language.FR: "https://environnement.brussels/thematiques/batiment/primes-et-incitants/prime-citerne",
            Language.NL: "https://leefmilieu.brussels/themas/gebouwen/premies-en-stimuli/regenwaterput-premie"
        },
        status=SubsidyStatus.ACTIVE,
        keywords=[
            TranslatedText(fr="Eau de pluie", nl="Regenwater"),
            TranslatedText(fr="Citerne", nl="Waterput"),
            TranslatedText(fr="Gestion de l'eau", nl="Waterbeheer"),
            TranslatedText(fr="Économie d'eau", nl="Waterbesparing")
        ],
        min_year_built=None,
        max_year_built=None
    )
]
