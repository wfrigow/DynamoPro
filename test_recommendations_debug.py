#!/usr/bin/env python3
"""
Script de débogage pour le moteur de recommandations
"""
import asyncio
import json
import os
import sys
import time

# Ajouter le répertoire backend au chemin d'importation
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer le moteur de recommandations
from subsidy.integrations.recommendation_engine import RecommendationEngine

async def test_recommendations_debug():
    """Test détaillé du moteur de recommandations avec affichage des étapes intermédiaires"""
    print("Initialisation du moteur de recommandations...")
    start_time = time.time()
    
    # Créer une instance du moteur de recommandations
    engine = RecommendationEngine()
    
    print(f"Moteur initialisé en {time.time() - start_time:.2f} secondes")
    
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
    
    print("\nDébut du test du moteur de recommandations...")
    print("Données d'audit utilisées:")
    print(json.dumps(audit_data, indent=2, ensure_ascii=False))
    
    try:
        # Mesurer le temps de génération des recommandations
        gen_start_time = time.time()
        
        print("\nGénération des recommandations...")
        result = await engine.generate_recommendations(audit_data, user_id)
        
        gen_time = time.time() - gen_start_time
        print(f"\nRecommandations générées en {gen_time:.2f} secondes")
        
        print("\nRésultat:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Vérifier la structure des recommandations
        if "recommendations" in result:
            print(f"\nNombre de recommandations générées: {len(result['recommendations'])}")
            
            # Vérifier les champs de chaque recommandation
            for i, rec in enumerate(result["recommendations"]):
                print(f"\nRecommandation #{i+1}:")
                print(f"  Titre: {rec.get('title', 'Non défini')}")
                print(f"  Domaine: {rec.get('domain', 'Non défini')}")
                print(f"  Coût estimé: {rec.get('estimated_cost_min', 'N/A')} - {rec.get('estimated_cost_max', 'N/A')} €")
                print(f"  Économies annuelles: {rec.get('estimated_savings_per_year', 'N/A')} €")
                print(f"  ROI: {rec.get('estimated_roi_months', 'N/A')} mois")
                print(f"  Score d'impact: {rec.get('ecological_impact_score', 'N/A')}/10")
                
                # Vérifier les subventions applicables
                subsidies = rec.get('applicable_subsidies', [])
                if subsidies:
                    print(f"  Subventions applicables: {', '.join(subsidies)}")
                else:
                    print("  Aucune subvention applicable")
        
        return True
    except Exception as e:
        print(f"\nErreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Test de débogage du moteur de recommandations ===\n")
    asyncio.run(test_recommendations_debug())
    print("\n=== Fin du test ===")
