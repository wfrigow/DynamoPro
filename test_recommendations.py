#!/usr/bin/env python3
"""
Test script for the recommendations API endpoint
"""
import asyncio
import json
import httpx

async def test_recommendations():
    """Test the recommendations API endpoint"""
    # Sample audit data
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
    
    # Call the API
    url = "http://localhost:8000/detailed-recommendations"
    headers = {"Content-Type": "application/json"}
    
    print(f"Calling {url} with audit data...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=audit_data, headers=headers, timeout=60.0)
            
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("Success! Recommendations received:")
                print(json.dumps(result, indent=2))
                return True
            else:
                print(f"Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            return False

if __name__ == "__main__":
    asyncio.run(test_recommendations())
