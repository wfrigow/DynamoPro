"""
Moteur de recommandations basé sur l'IA pour DynamoPro
----------------------------------------------------
Ce module utilise l'IA pour générer des recommandations personnalisées
basées sur les données d'audit collectées.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from uuid import uuid4

from common.ai_utils import LLMService

logger = logging.getLogger("subsidy.recommendation_engine")

class RecommendationEngine:
    """Moteur de recommandations basé sur l'IA pour DynamoPro"""
    
    def __init__(self):
        """Initialise le moteur de recommandations"""
        self.llm_service = LLMService()
        # Charger la base de connaissances des recommandations possibles
        self.recommendations_db = self._load_recommendations_db()
        
    def _load_recommendations_db(self) -> Dict[str, Any]:
        """Charge la base de connaissances des recommandations"""
        db_path = os.path.join(os.path.dirname(__file__), "../data/recommendations_knowledge.json")
        try:
            if os.path.exists(db_path):
                with open(db_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Base de connaissances des recommandations non trouvée: {db_path}")
                return {
                    "energy": [],
                    "water": [],
                    "waste": [],
                    "biodiversity": []
                }
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la base de connaissances: {e}")
            return {
                "energy": [],
                "water": [],
                "waste": [],
                "biodiversity": []
            }
    
    async def generate_recommendations(self, audit_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Génère des recommandations personnalisées basées sur les données d'audit
        en utilisant un modèle d'IA pour l'analyse et la personnalisation
        
        Args:
            audit_data: Données collectées lors de l'audit
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dictionnaire contenant l'analyse, les recommandations et les questions supplémentaires
        """
        # Construire le prompt pour l'IA avec toutes les données d'audit
        prompt = self._build_analysis_prompt(audit_data)
        
        # Obtenir l'analyse de l'IA
        system_message = "Tu es un expert en durabilité et efficacité énergétique en Belgique avec une connaissance approfondie des subventions disponibles dans les différentes régions."
        
        try:
            analysis_result = await self.llm_service.generate_structured_response(
                prompt, 
                system_message,
                output_schema={
                    "analysis": "Analyse détaillée de la situation actuelle",
                    "recommendations": [{
                        "title": "Titre de la recommandation",
                        "description": "Description détaillée",
                        "domain": "Domaine (energy, water, waste, biodiversity)",
                        "estimated_cost_min": "Coût minimum estimé en euros (nombre)",
                        "estimated_cost_max": "Coût maximum estimé en euros (nombre)",
                        "estimated_savings_per_year": "Économies annuelles estimées en euros (nombre)",
                        "estimated_roi_months": "Retour sur investissement en mois (nombre)",
                        "ecological_impact_score": "Score d'impact écologique (1-10) (nombre)",
                        "difficulty": "Difficulté de mise en œuvre (1-10) (nombre)",
                        "applicable_subsidies": ["Noms des subventions applicables"],
                        "priority_score": "Score de priorité (1-100) (nombre)",
                        "reasoning": "Explication du raisonnement derrière cette recommandation"
                    }],
                    "additional_questions": ["Questions supplémentaires pour affiner les recommandations"]
                }
            )
        except Exception as e:
            logger.error(f"Erreur lors de la génération des recommandations: {e}")
            # Fournir une réponse par défaut en cas d'erreur
            return self._generate_fallback_recommendations(audit_data, user_id, str(e))
        
        # Enrichir les recommandations avec des IDs et des détails supplémentaires
        enriched_recommendations = self._enrich_recommendations(
            analysis_result.get("recommendations", []), 
            user_id
        )
        
        return {
            "analysis": analysis_result.get("analysis", ""),
            "recommendations": enriched_recommendations,
            "additional_questions": analysis_result.get("additional_questions", [])
        }
    
    def _build_analysis_prompt(self, audit_data: Dict[str, Any]) -> str:
        """
        Construit un prompt détaillé pour l'analyse IA
        
        Args:
            audit_data: Données collectées lors de l'audit
            
        Returns:
            Prompt formaté pour l'IA
        """
        profile = audit_data.get("profile", {})
        consumption = audit_data.get("consumption", {})
        property_data = audit_data.get("property", {})
        
        # Calculer la surface du toit approximative basée sur la surface au sol
        roof_area = property_data.get("area", 0)
        if property_data.get("propertyType") == "house":
            roof_area = roof_area * 0.8  # Approximation pour une maison
        
        prompt = f"""
        Analyse les données d'audit suivantes et génère des recommandations personnalisées 
        pour améliorer la durabilité et l'efficacité énergétique:
        
        PROFIL:
        - Type d'utilisateur: {profile.get("userType", "Non spécifié")}
        - Région: {profile.get("region", "Non spécifiée")}
        
        CONSOMMATION:
        - Électricité: {consumption.get("electricityUsage", 0)} kWh/an
        - Utilisation du gaz: {"Oui" if consumption.get("gasUsage") else "Non"}
        - Consommation de gaz: {consumption.get("gasConsumption", 0)} m³/an
        
        PROPRIÉTÉ:
        - Type: {property_data.get("propertyType", "Non spécifié")}
        - Surface: {property_data.get("area", 0)} m²
        - Surface de toit approximative: {roof_area} m²
        - Année de construction: {property_data.get("constructionYear", "Non spécifiée")}
        - État d'isolation: {property_data.get("insulationStatus", "Non spécifié")}
        
        Génère des recommandations très détaillées et personnalisées en fonction de ces données.
        Pour chaque recommandation, fournis:
        1. Un titre concis
        2. Une description détaillée expliquant pourquoi cette recommandation est pertinente pour ce cas spécifique
        3. Les coûts estimés (minimum et maximum) en euros
        4. Les économies annuelles estimées en euros
        5. Le retour sur investissement en mois
        6. L'impact écologique sur une échelle de 1 à 10
        7. La difficulté de mise en œuvre sur une échelle de 1 à 10
        8. Les subventions belges applicables spécifiques à la région {profile.get("region", "wallonie")}
        9. Un score de priorité (1-100) basé sur l'impact, le ROI et la facilité de mise en œuvre
        10. Une explication détaillée du raisonnement derrière cette recommandation
        
        Tiens compte des spécificités régionales belges (Wallonie, Flandre, Bruxelles) dans tes recommandations,
        notamment pour les subventions disponibles.
        
        Propose également 3 à 5 questions supplémentaires qui permettraient d'affiner davantage les recommandations.
        Ces questions doivent être spécifiques et pertinentes par rapport aux données déjà fournies.
        
        IMPORTANT:
        - Assure-toi que les valeurs numériques (coûts, économies, ROI, scores) sont réalistes et cohérentes
        - Adapte les recommandations au type d'utilisateur et à la région
        - Priorise les recommandations avec le meilleur rapport impact/coût
        - Fournis des descriptions détaillées et personnalisées, pas des généralités
        """
        
        return prompt
    
    def _enrich_recommendations(self, recommendations: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Enrichit les recommandations avec des IDs et des détails supplémentaires
        
        Args:
            recommendations: Liste des recommandations générées par l'IA
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Liste des recommandations enrichies
        """
        enriched = []
        
        for rec in recommendations:
            # Générer un ID unique
            rec_id = str(uuid4())
            
            # Convertir les valeurs numériques
            try:
                # Utiliser des valeurs par défaut en cas d'erreur de conversion
                estimated_cost_min = self._safe_convert_to_float(rec.get("estimated_cost_min"), 1000)
                estimated_cost_max = self._safe_convert_to_float(rec.get("estimated_cost_max"), 5000)
                estimated_savings = self._safe_convert_to_float(rec.get("estimated_savings_per_year"), 200)
                estimated_roi = self._safe_convert_to_int(rec.get("estimated_roi_months"), 60)
                ecological_impact = self._safe_convert_to_int(rec.get("ecological_impact_score"), 5)
                difficulty = self._safe_convert_to_int(rec.get("difficulty"), 5)
                priority_score = self._safe_convert_to_float(rec.get("priority_score"), 50)
                
                # S'assurer que les valeurs sont dans les plages acceptables
                ecological_impact = max(1, min(10, ecological_impact))
                difficulty = max(1, min(10, difficulty))
                priority_score = max(1, min(100, priority_score))
                
                # Créer la recommandation enrichie
                enriched_rec = {
                    "id": rec_id,
                    "user_id": user_id,
                    "title": rec.get("title", "Recommandation"),
                    "description": rec.get("description", ""),
                    "domain": rec.get("domain", "energy"),
                    "estimated_cost_min": estimated_cost_min,
                    "estimated_cost_max": estimated_cost_max,
                    "estimated_savings_per_year": estimated_savings,
                    "estimated_roi_months": estimated_roi,
                    "ecological_impact_score": ecological_impact,
                    "difficulty": difficulty,
                    "applicable_subsidies": rec.get("applicable_subsidies", []),
                    "priority_score": priority_score,
                    "reasoning": rec.get("reasoning", ""),
                    "status": "pending"
                }
                
                enriched.append(enriched_rec)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'enrichissement d'une recommandation: {e}")
                # Continuer avec la recommandation suivante
        
        # Trier les recommandations par score de priorité décroissant
        enriched.sort(key=lambda x: x["priority_score"], reverse=True)
        
        return enriched
    
    def _safe_convert_to_float(self, value: Any, default: float = 0.0) -> float:
        """Convertit une valeur en float de manière sécurisée"""
        try:
            if isinstance(value, str):
                # Supprimer les symboles monétaires et les espaces
                value = value.replace('€', '').replace(' ', '').replace(',', '.')
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def _safe_convert_to_int(self, value: Any, default: int = 0) -> int:
        """Convertit une valeur en int de manière sécurisée"""
        try:
            if isinstance(value, str):
                # Supprimer les symboles et les espaces
                value = value.replace(' ', '')
            return int(float(value))
        except (ValueError, TypeError):
            return default
    
    def _generate_fallback_recommendations(self, audit_data: Dict[str, Any], user_id: str, error_message: str) -> Dict[str, Any]:
        """
        Génère des recommandations de secours en cas d'erreur avec l'IA
        
        Args:
            audit_data: Données collectées lors de l'audit
            user_id: Identifiant de l'utilisateur
            error_message: Message d'erreur
            
        Returns:
            Dictionnaire contenant l'analyse, les recommandations et les questions supplémentaires
        """
        logger.warning(f"Utilisation des recommandations de secours suite à une erreur: {error_message}")
        
        profile = audit_data.get("profile", {})
        consumption = audit_data.get("consumption", {})
        property_data = audit_data.get("property", {})
        
        # Analyse de base
        analysis = f"Analyse basée sur un profil {profile.get('userType', 'non spécifié')} en {profile.get('region', 'Belgique')}."
        
        # Recommandations de base
        recommendations = []
        
        # Recommandation pour l'énergie
        if consumption.get("electricityUsage", 0) > 3000:
            recommendations.append({
                "id": str(uuid4()),
                "user_id": user_id,
                "title": "Installation de panneaux solaires",
                "description": f"Avec une consommation électrique de {consumption.get('electricityUsage', 0)} kWh, l'installation de panneaux solaires pourrait réduire significativement votre facture d'électricité.",
                "domain": "energy",
                "estimated_cost_min": 4000,
                "estimated_cost_max": 12000,
                "estimated_savings_per_year": 800,
                "estimated_roi_months": 60,
                "ecological_impact_score": 8,
                "difficulty": 6,
                "applicable_subsidies": ["Prime Énergie"],
                "priority_score": 80,
                "reasoning": "Votre consommation électrique élevée rend cette solution particulièrement rentable.",
                "status": "pending"
            })
        
        # Recommandation pour l'isolation
        if property_data.get("constructionYear", 2020) < 2000:
            recommendations.append({
                "id": str(uuid4()),
                "user_id": user_id,
                "title": "Amélioration de l'isolation thermique",
                "description": f"Votre propriété datant de {property_data.get('constructionYear', 'avant 2000')}, une amélioration de l'isolation permettrait de réduire significativement vos besoins en chauffage.",
                "domain": "energy",
                "estimated_cost_min": 3000,
                "estimated_cost_max": 10000,
                "estimated_savings_per_year": 600,
                "estimated_roi_months": 72,
                "ecological_impact_score": 7,
                "difficulty": 5,
                "applicable_subsidies": ["Prime Isolation"],
                "priority_score": 75,
                "reasoning": "Les bâtiments anciens ont souvent une isolation insuffisante, ce qui entraîne des pertes de chaleur importantes.",
                "status": "pending"
            })
        
        # Recommandation pour l'eau
        recommendations.append({
            "id": str(uuid4()),
            "user_id": user_id,
            "title": "Installation de dispositifs hydro-économes",
            "description": "Les dispositifs hydro-économes permettent de réduire votre consommation d'eau de 30 à 50% avec un investissement minimal.",
            "domain": "water",
            "estimated_cost_min": 50,
            "estimated_cost_max": 300,
            "estimated_savings_per_year": 150,
            "estimated_roi_months": 12,
            "ecological_impact_score": 6,
            "difficulty": 2,
            "applicable_subsidies": [],
            "priority_score": 85,
            "reasoning": "Solution simple à mettre en œuvre avec un retour sur investissement rapide.",
            "status": "pending"
        })
        
        # Questions supplémentaires
        additional_questions = [
            "Quel est votre système de chauffage actuel ?",
            "Avez-vous déjà réalisé des travaux de rénovation énergétique ?",
            "Quelle est votre consommation d'eau annuelle ?"
        ]
        
        return {
            "analysis": analysis,
            "recommendations": recommendations,
            "additional_questions": additional_questions
        }


# Singleton pour accéder au moteur de recommandations
_recommendation_engine = None

def get_recommendation_engine() -> RecommendationEngine:
    """Récupère l'instance du moteur de recommandations"""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine
