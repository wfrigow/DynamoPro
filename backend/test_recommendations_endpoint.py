#!/usr/bin/env python3
"""
Test script pour l'endpoint de recommandations avec la nouvelle implémentation
"""
import asyncio
import json
import os
import sys

# Ajouter le répertoire backend au chemin d'importation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer les modules nécessaires
from subsidy.integrations.recommendation_engine import RecommendationEngine

async def test_recommendations_engine():
    """Test direct du moteur de recommandations avec la nouvelle implémentation"""
    # Créer une instance du moteur de recommandations
    engine = RecommendationEngine()
    
    # Données d'audit de test
    audit_data = {
        "profile": {
            "userType": "particulier",
            "region": "wallonie",
            "postalCode": "4000",
            "familySize": 4
        },
        "consumption": {
            "electricityUsage": 4500,
            "gasUsage": 18000,
            "waterUsage": 120
        },
        "property": {
            "type": "house",
            "size": 180,
            "constructionYear": 1985,
            "heatingSystem": "gas",
            "insulation": "partial"
        }
    }
    
    # ID utilisateur de test
    user_id = "test-user-123"
    
    print("Test du moteur de recommandations avec la nouvelle implémentation...")
    
    try:
        # Appeler la méthode generate_recommendations
        result = await engine.generate_recommendations(audit_data, user_id)
        
        print("Succès ! Résultat :")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return True
    except Exception as e:
        print(f"Erreur : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_recommendations_engine())
