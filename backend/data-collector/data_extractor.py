"""
Module d'extraction de données pour le Data Collector Agent
----------------------------------------------------------
Ce module analyse les conversations et extrait des données structurées.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("data-extractor")

class DataExtractor:
    """Service d'extraction de données à partir de conversations"""
    
    def __init__(self):
        """Initialise l'extracteur de données"""
        # Définition des patterns d'extraction pour différents types de données
        self.patterns = {
            # Patterns pour les données de profil
            "profile": {
                "userType": [
                    r"(?:je suis|nous sommes)(?:\sun|\sune)?\s(particulier|indépendant|entreprise|TPE|PME)",
                    r"(?:type|statut).*?(?:particulier|indépendant|entreprise|TPE|PME)"
                ],
                "region": [
                    r"(?:je|nous)(?:\svis|\svivons|\ssuis|\ssommes)(?:\sà|en|au)?\s(Wallonie|Flandre|Bruxelles)",
                    r"(?:région|province).*?(Wallonie|Flandre|Bruxelles)"
                ],
                "email": [
                    r"(?:mon|notre)\semail.*?([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",
                    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
                ],
                "phone": [
                    r"(?:téléphone|portable|GSM).*?((?:\+32|0)\s?[0-9]{1,2}\s?[0-9]{2}\s?[0-9]{2}\s?[0-9]{2})",
                    r"((?:\+32|0)\s?[0-9]{1,2}\s?[0-9]{2}\s?[0-9]{2}\s?[0-9]{2})"
                ],
                "companyName": [
                    r"(?:nom\sde\sl'entreprise|société).*?[\"']?([^\"'.,;!?]+)[\"']?",
                    r"(?:entreprise|société)\s(?:s'appelle|est)\s[\"']?([^\"'.,;!?]+)[\"']?"
                ],
                "companySize": [
                    r"(?:taille|nombre\sd'employés).*?([0-9]+)",
                    r"([0-9]+)\s(?:employés|personnes|salariés)"
                ]
            },
            
            # Patterns pour les données de consommation
            "consumption": {
                "electricityUsage": [
                    r"(?:consommation|utilisation).*?électricité.*?([0-9]+(?:[.,][0-9]+)?)\s?(?:kWh|kilowatt)",
                    r"([0-9]+(?:[.,][0-9]+)?)\s?(?:kWh|kilowatt)"
                ],
                "gasUsage": [
                    r"(?:consommation|utilisation).*?gaz.*?([0-9]+(?:[.,][0-9]+)?)\s?(?:kWh|m3)",
                    r"([0-9]+(?:[.,][0-9]+)?)\s?(?:kWh|m3).*?gaz"
                ],
                "waterUsage": [
                    r"(?:consommation|utilisation).*?eau.*?([0-9]+(?:[.,][0-9]+)?)\s?(?:m3|litres|L)",
                    r"([0-9]+(?:[.,][0-9]+)?)\s?(?:m3|litres|L).*?eau"
                ],
                "energyProvider": [
                    r"(?:fournisseur|opérateur).*?(?:énergie|électricité|gaz).*?[\"']?([^\"'.,;!?]+)[\"']?",
                    r"(?:énergie|électricité|gaz).*?(?:fourni|livré).*?par\s[\"']?([^\"'.,;!?]+)[\"']?"
                ],
                "energyCost": [
                    r"(?:facture|coût|montant).*?(?:énergie|électricité|gaz).*?([0-9]+(?:[.,][0-9]+)?)\s?(?:€|euros)",
                    r"([0-9]+(?:[.,][0-9]+)?)\s?(?:€|euros).*?(?:énergie|électricité|gaz)"
                ]
            },
            
            # Patterns pour les données de propriété
            "property": {
                "propertyType": [
                    r"(?:j'habite|nous habitons|je vis|nous vivons)(?:\sdans|\sune|\sun)?\s(appartement|maison|villa|studio|loft)",
                    r"(?:type\sde\slogement|habitation).*?(appartement|maison|villa|studio|loft)"
                ],
                "propertySize": [
                    r"(?:superficie|surface|taille).*?([0-9]+(?:[.,][0-9]+)?)\s?(?:m2|mètres carrés)",
                    r"([0-9]+(?:[.,][0-9]+)?)\s?(?:m2|mètres carrés)"
                ],
                "yearBuilt": [
                    r"(?:construit|bâti|date\sde\sconstruction).*?(?:en)?\s([0-9]{4})",
                    r"(?:maison|bâtiment|immeuble).*?(?:de)?\s([0-9]{4})"
                ],
                "heatingType": [
                    r"(?:chauffage).*?(électrique|gaz|mazout|pompe\sà\schaleur|bois|pellets)",
                    r"(?:chauffé).*?(électrique|gaz|mazout|pompe\sà\schaleur|bois|pellets)"
                ],
                "occupants": [
                    r"(?:nous\ssommes|il\sy\sa)\s([0-9]+)\s(?:personnes|occupants)",
                    r"([0-9]+)\s(?:personnes|occupants)"
                ]
            }
        }
    
    def extract_data(self, message: str, agent_type: str) -> Dict[str, Any]:
        """
        Extrait des données structurées à partir d'un message utilisateur
        
        Args:
            message: Le message de l'utilisateur
            agent_type: Le type d'agent ('profile', 'consumption', 'property')
            
        Returns:
            Dictionnaire contenant les données extraites
        """
        if agent_type not in self.patterns:
            logger.warning(f"Type d'agent non reconnu: {agent_type}")
            return {}
        
        extracted_data = {}
        
        # Normalisation du message
        normalized_message = self._normalize_message(message)
        
        # Extraction des données selon le type d'agent
        for field, patterns in self.patterns[agent_type].items():
            for pattern in patterns:
                match = re.search(pattern, normalized_message, re.IGNORECASE)
                if match:
                    value = match.group(1).strip()
                    # Conversion des valeurs numériques
                    if self._is_numeric_field(field):
                        value = self._convert_to_number(value)
                    extracted_data[field] = value
                    break  # Arrêter après la première correspondance pour ce champ
        
        logger.info(f"Données extraites ({agent_type}): {extracted_data}")
        return extracted_data
    
    def _normalize_message(self, message: str) -> str:
        """Normalise un message pour l'extraction de données"""
        # Convertir en minuscules
        normalized = message.lower()
        # Remplacer les caractères accentués
        normalized = self._remove_accents(normalized)
        # Normaliser les espaces
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def _remove_accents(self, text: str) -> str:
        """Supprime les accents d'un texte"""
        accents = {
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
            'à': 'a', 'â': 'a', 'ä': 'a',
            'î': 'i', 'ï': 'i',
            'ô': 'o', 'ö': 'o',
            'ù': 'u', 'û': 'u', 'ü': 'u',
            'ÿ': 'y', 'ç': 'c'
        }
        for accent, replacement in accents.items():
            text = text.replace(accent, replacement)
        return text
    
    def _is_numeric_field(self, field: str) -> bool:
        """Détermine si un champ doit être converti en nombre"""
        numeric_fields = [
            'electricityUsage', 'gasUsage', 'waterUsage', 
            'energyCost', 'propertySize', 'yearBuilt', 
            'occupants', 'companySize'
        ]
        return field in numeric_fields
    
    def _convert_to_number(self, value: str) -> float:
        """Convertit une chaîne en nombre"""
        # Remplacer la virgule par un point pour les décimaux
        value = value.replace(',', '.')
        # Extraire uniquement les chiffres et le point décimal
        value = re.sub(r'[^\d.]', '', value)
        try:
            return float(value)
        except ValueError:
            return 0.0
    
    def generate_follow_up_questions(self, message: str, extracted_data: Dict[str, Any], agent_type: str) -> List[str]:
        """
        Génère des questions de suivi basées sur les données manquantes
        
        Args:
            message: Le message de l'utilisateur
            extracted_data: Les données déjà extraites
            agent_type: Le type d'agent ('profile', 'consumption', 'property')
            
        Returns:
            Liste de questions de suivi suggérées
        """
        if agent_type not in self.patterns:
            return []
        
        questions = []
        
        # Définition des questions par défaut pour les champs manquants
        default_questions = {
            "profile": {
                "userType": "Êtes-vous un particulier, un indépendant ou une entreprise ?",
                "region": "Dans quelle région de Belgique êtes-vous situé(e) ?",
                "email": "Quelle est votre adresse email ?",
                "phone": "Quel est votre numéro de téléphone ?",
                "companyName": "Quel est le nom de votre entreprise ?",
                "companySize": "Combien d'employés compte votre entreprise ?"
            },
            "consumption": {
                "electricityUsage": "Quelle est votre consommation annuelle d'électricité en kWh ?",
                "gasUsage": "Quelle est votre consommation annuelle de gaz en kWh ou m³ ?",
                "waterUsage": "Quelle est votre consommation annuelle d'eau en m³ ?",
                "energyProvider": "Qui est votre fournisseur d'énergie actuel ?",
                "energyCost": "Quel est le montant annuel de vos factures d'énergie ?"
            },
            "property": {
                "propertyType": "Quel type de logement habitez-vous (appartement, maison, etc.) ?",
                "propertySize": "Quelle est la superficie de votre logement en m² ?",
                "yearBuilt": "En quelle année a été construit votre logement ?",
                "heatingType": "Quel type de chauffage utilisez-vous ?",
                "occupants": "Combien de personnes vivent dans votre logement ?"
            }
        }
        
        # Priorités des champs (les plus importants d'abord)
        field_priorities = {
            "profile": ["userType", "region", "email", "phone", "companyName", "companySize"],
            "consumption": ["electricityUsage", "gasUsage", "waterUsage", "energyProvider", "energyCost"],
            "property": ["propertyType", "propertySize", "yearBuilt", "heatingType", "occupants"]
        }
        
        # Ajouter des questions pour les champs manquants selon la priorité
        for field in field_priorities.get(agent_type, []):
            if field not in extracted_data and (
                # Pour les champs d'entreprise, ne les demander que si le type d'utilisateur est approprié
                not field.startswith("company") or 
                extracted_data.get("userType") in ["indépendant", "entreprise", "TPE", "PME"]
            ):
                questions.append(default_questions[agent_type][field])
            
            # Limiter à 2 questions maximum pour ne pas submerger l'utilisateur
            if len(questions) >= 2:
                break
        
        return questions
