#!/usr/bin/env python3
"""
Test script for the LLMService generate_structured_response method
"""
import asyncio
import json
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the LLMService
from common.ai_utils import LLMService

async def test_llm_service():
    """Test the LLMService generate_structured_response method"""
    # Create an instance of LLMService
    llm_service = LLMService()
    
    # Test prompt
    prompt = "Analyse les données suivantes et fais des recommandations: Maison de 180m², construite en 1985, chauffage au gaz, isolation partielle."
    
    # System message
    system_message = "Tu es un expert en durabilité et efficacité énergétique en Belgique."
    
    # Output schema
    output_schema = {
        "analysis": "Analyse détaillée de la situation actuelle",
        "recommendations": [{
            "title": "Titre de la recommandation",
            "description": "Description détaillée",
            "domain": "Domaine (energy, water, waste, biodiversity)",
            "estimated_cost_min": "Coût minimum estimé en euros (nombre)",
            "estimated_cost_max": "Coût maximum estimé en euros (nombre)"
        }]
    }
    
    print("Testing LLMService.generate_structured_response...")
    
    try:
        # Call the generate_structured_response method
        result = await llm_service.generate_structured_response(
            prompt=prompt,
            system_message=system_message,
            output_schema=output_schema
        )
        
        print("Success! Result:")
        print(json.dumps(result, indent=2))
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_llm_service())
