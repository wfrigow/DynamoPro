"""
Module contenant les données enrichies des subventions disponibles en Belgique.
Inclut le support multilingue (français et néerlandais) et des données plus détaillées.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date

class Language(str, Enum):
    """Langues supportées pour les subventions."""
    FR = "fr"
    NL = "nl"

class Region(str, Enum):
    """Régions belges où les subventions sont disponibles."""
    WALLONIE = "wallonie"
    BRUXELLES = "bruxelles"
    FLANDRE = "flandre"
    FEDERAL = "federal"  # Pour les subventions au niveau fédéral

class Domain(str, Enum):
    """Domaines couverts par les subventions."""
    ENERGY = "energy"
    WATER = "water"
    WASTE = "waste"
    BIODIVERSITY = "biodiversity"
    RENOVATION = "renovation"
    MOBILITY = "mobility"
    CIRCULAR_ECONOMY = "circular_economy"

class UserType(str, Enum):
    """Types d'utilisateurs éligibles pour les subventions."""
    INDIVIDUAL = "individual"  # Particulier
    SELF_EMPLOYED = "self_employed"  # Indépendant
    SMALL_BUSINESS = "small_business"  # Petite entreprise (<50 employés)
    MEDIUM_BUSINESS = "medium_business"  # Moyenne entreprise (50-250 employés)
    LARGE_BUSINESS = "large_business"  # Grande entreprise (>250 employés)
    PUBLIC_ENTITY = "public_entity"  # Entité publique
    NON_PROFIT = "non_profit"  # Association sans but lucratif

class DocumentType(str, Enum):
    """Types de documents requis pour les demandes de subvention."""
    IDENTITY = "identity"  # Carte d'identité
    OWNERSHIP = "ownership"  # Preuve de propriété
    INVOICE = "invoice"  # Facture
    QUOTE = "quote"  # Devis
    TECHNICAL_SPEC = "technical_spec"  # Spécification technique
    CERTIFICATE = "certificate"  # Certificat
    PERMIT = "permit"  # Permis
    PHOTO = "photo"  # Photo
    TAX = "tax"  # Document fiscal
    BUSINESS_REGISTRATION = "business_registration"  # Enregistrement d'entreprise
    OTHER = "other"  # Autre

class SubsidyStatus(str, Enum):
    """Statut des subventions."""
    ACTIVE = "active"  # Subvention active
    EXPIRED = "expired"  # Subvention expirée
    COMING_SOON = "coming_soon"  # Subvention à venir
    SUSPENDED = "suspended"  # Subvention temporairement suspendue

class TranslatedText:
    """Classe pour gérer les textes multilingues."""
    def __init__(self, fr: str, nl: str):
        self.fr = fr
        self.nl = nl
    
    def get(self, lang: Language = Language.FR) -> str:
        """Récupère le texte dans la langue spécifiée."""
        if lang == Language.NL:
            return self.nl
        return self.fr
    
    def to_dict(self) -> Dict[str, str]:
        """Convertit l'objet en dictionnaire."""
        return {
            "fr": self.fr,
            "nl": self.nl
        }

class RequiredDocument:
    """Classe représentant un document requis pour une demande de subvention."""
    def __init__(
        self,
        id: str,
        name: TranslatedText,
        description: TranslatedText,
        type: DocumentType,
        required: bool = True,
        format: Optional[List[str]] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.type = type
        self.required = required
        self.format = format or ["pdf", "jpg", "png"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name.to_dict(),
            "description": self.description.to_dict(),
            "type": self.type,
            "required": self.required,
            "format": self.format
        }

class EnrichedSubsidy:
    """Classe représentant une subvention enrichie avec des données détaillées."""
    def __init__(
        self,
        id: str,
        name: TranslatedText,
        provider: TranslatedText,
        description: TranslatedText,
        regions: List[Region],
        domains: List[Domain],
        max_amount: Optional[float] = None,
        percentage: Optional[float] = None,
        conditions: TranslatedText = None,
        eligibility: List[TranslatedText] = None,
        user_types: List[UserType] = None,
        required_documents: List[RequiredDocument] = None,
        application_process: TranslatedText = None,
        documentation_url: Dict[Language, str] = None,
        expiration_date: Optional[date] = None,
        status: SubsidyStatus = SubsidyStatus.ACTIVE,
        keywords: List[TranslatedText] = None,
        min_year_built: Optional[int] = None,
        max_year_built: Optional[int] = None,
        additional_info: Optional[TranslatedText] = None
    ):
        self.id = id
        self.name = name
        self.provider = provider
        self.description = description
        self.regions = regions
        self.domains = domains
        self.max_amount = max_amount
        self.percentage = percentage
        self.conditions = conditions
        self.eligibility = eligibility or []
        self.user_types = user_types or [UserType.INDIVIDUAL]
        self.required_documents = required_documents or []
        self.application_process = application_process
        self.documentation_url = documentation_url or {}
        self.expiration_date = expiration_date
        self.status = status
        self.keywords = keywords or []
        self.min_year_built = min_year_built
        self.max_year_built = max_year_built
        self.additional_info = additional_info
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'objet en dictionnaire."""
        return {
            "id": self.id,
            "name": self.name.to_dict(),
            "provider": self.provider.to_dict(),
            "description": self.description.to_dict(),
            "regions": [r.value for r in self.regions],
            "domains": [d.value for d in self.domains],
            "max_amount": self.max_amount,
            "percentage": self.percentage,
            "conditions": self.conditions.to_dict() if self.conditions else None,
            "eligibility": [e.to_dict() for e in self.eligibility],
            "user_types": [ut.value for ut in self.user_types],
            "required_documents": [doc.to_dict() for doc in self.required_documents],
            "application_process": self.application_process.to_dict() if self.application_process else None,
            "documentation_url": {k.value: v for k, v in self.documentation_url.items()},
            "expiration_date": self.expiration_date.isoformat() if self.expiration_date else None,
            "status": self.status.value,
            "keywords": [k.to_dict() for k in self.keywords],
            "min_year_built": self.min_year_built,
            "max_year_built": self.max_year_built,
            "additional_info": self.additional_info.to_dict() if self.additional_info else None
        }

# Création des documents requis communs
identity_card_doc = RequiredDocument(
    id="doc_identity",
    name=TranslatedText(
        fr="Carte d'identité",
        nl="Identiteitskaart"
    ),
    description=TranslatedText(
        fr="Copie recto-verso de la carte d'identité du demandeur",
        nl="Kopie van de identiteitskaart van de aanvrager (voor- en achterkant)"
    ),
    type=DocumentType.IDENTITY
)

property_proof_doc = RequiredDocument(
    id="doc_property",
    name=TranslatedText(
        fr="Preuve de propriété",
        nl="Eigendomsbewijs"
    ),
    description=TranslatedText(
        fr="Acte de propriété ou bail de location",
        nl="Eigendomsakte of huurcontract"
    ),
    type=DocumentType.OWNERSHIP
)

quote_doc = RequiredDocument(
    id="doc_quote",
    name=TranslatedText(
        fr="Devis détaillé",
        nl="Gedetailleerde offerte"
    ),
    description=TranslatedText(
        fr="Devis détaillé de l'entrepreneur mentionnant les matériaux, les surfaces et les coûts",
        nl="Gedetailleerde offerte van de aannemer met vermelding van materialen, oppervlakten en kosten"
    ),
    type=DocumentType.QUOTE
)

invoice_doc = RequiredDocument(
    id="doc_invoice",
    name=TranslatedText(
        fr="Facture",
        nl="Factuur"
    ),
    description=TranslatedText(
        fr="Facture détaillée des travaux réalisés",
        nl="Gedetailleerde factuur van de uitgevoerde werken"
    ),
    type=DocumentType.INVOICE
)

technical_sheet_doc = RequiredDocument(
    id="doc_technical",
    name=TranslatedText(
        fr="Fiche technique",
        nl="Technische fiche"
    ),
    description=TranslatedText(
        fr="Fiche technique des matériaux utilisés",
        nl="Technische fiche van de gebruikte materialen"
    ),
    type=DocumentType.TECHNICAL_SPEC
)

photos_doc = RequiredDocument(
    id="doc_photos",
    name=TranslatedText(
        fr="Photos avant travaux",
        nl="Foto's vóór de werken"
    ),
    description=TranslatedText(
        fr="Photos montrant l'état actuel avant les travaux",
        nl="Foto's die de huidige staat vóór de werken tonen"
    ),
    type=DocumentType.PHOTO
)

contractor_cert_doc = RequiredDocument(
    id="doc_contractor_cert",
    name=TranslatedText(
        fr="Certification de l'entrepreneur",
        nl="Certificering van de aannemer"
    ),
    description=TranslatedText(
        fr="Preuve de certification de l'entrepreneur pour les travaux concernés",
        nl="Bewijs van certificering van de aannemer voor de betrokken werken"
    ),
    type=DocumentType.CERTIFICATE
)

# Exemple de subventions enrichies
ENRICHED_SUBSIDIES = [
    # 1. Prime Énergie - Isolation Toiture (Wallonie)
    EnrichedSubsidy(
        id="subsidy-isolation-toiture-wallonie",
        name=TranslatedText(
            fr="Prime Énergie - Isolation Toiture",
            nl="Energiepremie - Dakisolatie"
        ),
        provider=TranslatedText(
            fr="Service Public de Wallonie - Énergie",
            nl="Waalse Overheidsdienst - Energie"
        ),
        description=TranslatedText(
            fr="Prime pour l'isolation thermique du toit ou des combles dans une habitation existante. Cette prime vise à encourager l'amélioration de l'efficacité énergétique des bâtiments résidentiels en Wallonie.",
            nl="Premie voor de thermische isolatie van het dak of de zolder in een bestaande woning. Deze premie is bedoeld om de verbetering van de energie-efficiëntie van residentiële gebouwen in Wallonië aan te moedigen."
        ),
        regions=[Region.WALLONIE],
        domains=[Domain.ENERGY, Domain.RENOVATION],
        max_amount=2000,
        percentage=35,
        conditions=TranslatedText(
            fr="Le coefficient de résistance thermique R doit être ≥ 4,5 m²K/W. Les travaux doivent être réalisés par un entrepreneur enregistré.",
            nl="De thermische weerstandscoëfficiënt R moet ≥ 4,5 m²K/W zijn. De werkzaamheden moeten worden uitgevoerd door een geregistreerde aannemer."
        ),
        eligibility=[
            TranslatedText(
                fr="Habitation située en Wallonie",
                nl="Woning gelegen in Wallonië"
            ),
            TranslatedText(
                fr="Coefficient de résistance thermique R ≥ 4,5 m²K/W",
                nl="Thermische weerstandscoëfficiënt R ≥ 4,5 m²K/W"
            ),
            TranslatedText(
                fr="Travaux réalisés par un entrepreneur enregistré",
                nl="Werkzaamheden uitgevoerd door een geregistreerde aannemer"
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
            photos_doc,
            contractor_cert_doc
        ],
        application_process=TranslatedText(
            fr="Demande en ligne via le portail Energie de la Région Wallonne. Vous devez créer un compte et suivre les étapes indiquées.",
            nl="Online aanvraag via het Energieportaal van het Waalse Gewest. U moet een account aanmaken en de aangegeven stappen volgen."
        ),
        documentation_url={
            Language.FR: "https://energie.wallonie.be/fr/prime-isolation-du-toit.html",
            Language.NL: "https://energie.wallonie.be/nl/premie-dakisolatie.html"
        },
        status=SubsidyStatus.ACTIVE,
        keywords=[
            TranslatedText(fr="Isolation", nl="Isolatie"),
            TranslatedText(fr="Rénovation", nl="Renovatie"),
            TranslatedText(fr="Économie d'énergie", nl="Energiebesparing"),
            TranslatedText(fr="Toiture", nl="Dak")
        ],
        min_year_built=None,
        max_year_built=2015  # Habitations construites avant 2015
    ),
    
    # 2. Prime Rénovation - Fenêtres (Bruxelles)
    EnrichedSubsidy(
        id="subsidy-renovation-fenetres-bruxelles",
        name=TranslatedText(
            fr="Prime Rénovation - Fenêtres",
            nl="Renovatiepremie - Ramen"
        ),
        provider=TranslatedText(
            fr="Bruxelles Environnement",
            nl="Leefmilieu Brussel"
        ),
        description=TranslatedText(
            fr="Prime pour le remplacement de châssis/fenêtres par du vitrage à haute performance énergétique. Cette prime s'inscrit dans le cadre du programme régional pour la rénovation des bâtiments à Bruxelles.",
            nl="Premie voor de vervanging van raamkozijnen/ramen door hoogrendementsglas. Deze premie maakt deel uit van het gewestelijke programma voor de renovatie van gebouwen in Brussel."
        ),
        regions=[Region.BRUXELLES],
        domains=[Domain.ENERGY, Domain.RENOVATION],
        max_amount=1500,
        percentage=25,
        conditions=TranslatedText(
            fr="Le coefficient de transmission thermique du vitrage Ug doit être ≤ 1,1 W/m²K. L'installation doit être réalisée par un professionnel.",
            nl="De thermische transmissiecoëfficiënt van het glas Ug moet ≤ 1,1 W/m²K zijn. De installatie moet worden uitgevoerd door een professional."
        ),
        eligibility=[
            TranslatedText(
                fr="Bâtiment situé dans la Région de Bruxelles-Capitale",
                nl="Gebouw gelegen in het Brussels Hoofdstedelijk Gewest"
            ),
            TranslatedText(
                fr="Coefficient de transmission thermique du vitrage Ug ≤ 1,1 W/m²K",
                nl="Thermische transmissiecoëfficiënt van het glas Ug ≤ 1,1 W/m²K"
            ),
            TranslatedText(
                fr="Installation par un professionnel",
                nl="Installatie door een professional"
            ),
            TranslatedText(
                fr="Bâtiment de plus de 10 ans",
                nl="Gebouw ouder dan 10 jaar"
            )
        ],
        user_types=[UserType.INDIVIDUAL, UserType.SELF_EMPLOYED, UserType.NON_PROFIT],
        required_documents=[
            identity_card_doc,
            property_proof_doc,
            quote_doc,
            invoice_doc,
            technical_sheet_doc,
            photos_doc
        ],
        application_process=TranslatedText(
            fr="Demande via le formulaire en ligne sur le site de Bruxelles Environnement. Les documents doivent être soumis dans les 12 mois suivant la dernière facture.",
            nl="Aanvraag via het online formulier op de website van Leefmilieu Brussel. De documenten moeten worden ingediend binnen 12 maanden na de laatste factuur."
        ),
        documentation_url={
            Language.FR: "https://environnement.brussels/thematiques/batiment/primes-et-incitants",
            Language.NL: "https://leefmilieu.brussels/themas/gebouwen/premies-en-stimuli"
        },
        status=SubsidyStatus.ACTIVE,
        keywords=[
            TranslatedText(fr="Isolation", nl="Isolatie"),
            TranslatedText(fr="Fenêtres", nl="Ramen"),
            TranslatedText(fr="Rénovation", nl="Renovatie"),
            TranslatedText(fr="Vitrage", nl="Beglazing")
        ],
        min_year_built=None,
        max_year_built=2015
    )
]
