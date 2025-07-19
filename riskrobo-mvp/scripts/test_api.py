import requests
import json

def test_api_endpoints():
    """Test the FastAPI endpoints"""
    
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    response = requests.get(f"{base_url}/")
    print("Root endpoint:", response.json())
    
    # Test contract analysis
    test_contract = "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82"  # CAKE token
    
    analysis_request = {
        "contract_address": test_contract,
        "network": "bsc"
    }
    
    response = requests.post(
        f"{base_url}/analyze/contract",
        json=analysis_request
    )
    
    if response.status_code == 200:
        result = response.json()
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api_endpoints()
