#!/usr/bin/env python3
"""
Test RiskRobo API with multiple real BSC contract addresses
This script demonstrates the scanning capabilities of your RiskRobo project.
"""

import requests
import json
import time
from typing import Dict, List

# Real BSC contract addresses for testing
TEST_ADDRESSES = {
    "CAKE Token": "0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82",
    "BNB Token": "0xbb4CdB9CBd36B01bD1cBaeBF2De08d9173bc095c",
    "BUSD Token": "0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56",
    "USDT Token": "0x55d398326f99059fF775485246999027B3197955",
    "PancakeSwap Router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
    "PancakeSwap Factory": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
    "Venus Protocol": "0xcF6BB5389c92Bdda8a3747Ddb454cB7a64626C63",
    "Belt Finance": "0xE0e514c71282b6f4e823703a39374Cf58dc3eA4f",
    "Alpaca Finance": "0x8F0528cE5eF7B51152A59745bEfDD91D97091d2F",
    "Biswap Router": "0x3a6d8cA21D1CF76F653A67577FA0D27453350dD8"
}

def test_api_health(base_url: str = "http://localhost:8000") -> bool:
    """Test if the API is running"""
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Health Check: {data}")
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def analyze_contract(address: str, name: str, base_url: str = "http://localhost:8000") -> Dict:
    """Analyze a single contract address"""
    print(f"\n🔍 Analyzing {name} ({address})")
    print("-" * 50)
    
    try:
        # Prepare the analysis request
        analysis_request = {
            "contract_address": address,
            "network": "bsc"
        }
        
        # Send analysis request
        response = requests.post(
            f"{base_url}/analyze/contract",
            json=analysis_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Display results
            print(f"✅ Analysis completed for {name}")
            print(f"📊 Risk Score: {result.get('risk_score', 'N/A')}/100")
            
            # Show vulnerability flags
            vuln_flags = result.get('vulnerability_flags', [])
            if vuln_flags:
                print(f"🚨 Vulnerabilities: {', '.join(vuln_flags)}")
            else:
                print("✅ No vulnerabilities detected")
            
            # Show liquidity data
            liquidity = result.get('liquidity_data', {})
            if liquidity.get('has_liquidity'):
                print(f"💰 Liquidity: {liquidity.get('total_liquidity_bnb', 'N/A')} BNB")
            else:
                print("⚠️ No liquidity found")
            
            # Show holder analysis
            holders = result.get('holder_analysis', {})
            if 'top_10_percentage' in holders:
                print(f"👥 Top 10 holders: {holders.get('top_10_percentage', 'N/A')}%")
            
            return result
            
        else:
            print(f"❌ Analysis failed: {response.status_code} - {response.text}")
            return {"error": f"HTTP {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Error analyzing {name}: {e}")
        return {"error": str(e)}

def test_custom_address():
    """Let user test a custom address"""
    print("\n🎯 Test Custom Address")
    print("=" * 30)
    
    while True:
        address = input("\nEnter BSC contract address (or 'quit' to exit): ").strip()
        
        if address.lower() == 'quit':
            break
        
        if not address.startswith('0x') or len(address) != 42:
            print("❌ Invalid address format. Must be 42 characters starting with 0x")
            continue
        
        # Analyze the custom address
        result = analyze_contract(address, "Custom Contract")
        
        # Ask if user wants to see full details
        show_details = input("\nShow full analysis details? (y/N): ").strip().lower()
        if show_details == 'y':
            print("\n📋 Full Analysis Details:")
            print(json.dumps(result, indent=2))

def main():
    """Main function"""
    print("🚀 RiskRobo Contract Scanner - Multi-Address Test")
    print("=" * 60)
    print("This script tests your RiskRobo API with real BSC addresses")
    print("=" * 60)
    
    # Test API health first
    if not test_api_health():
        print("\n❌ API is not running. Please start the backend first:")
        print("cd backend && python main.py")
        return
    
    print("\n📋 Available test addresses:")
    for i, (name, address) in enumerate(TEST_ADDRESSES.items(), 1):
        print(f"{i:2d}. {name}: {address}")
    
    print("\n🎯 Choose an option:")
    print("1. Test all addresses")
    print("2. Test specific address")
    print("3. Test custom address")
    print("4. Quick test (first 3 addresses)")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        # Test all addresses
        print("\n🔍 Testing all addresses...")
        results = {}
        for name, address in TEST_ADDRESSES.items():
            results[name] = analyze_contract(address, name)
            time.sleep(1)  # Rate limiting
        
        # Summary
        print("\n📊 Summary:")
        print("-" * 30)
        for name, result in results.items():
            risk_score = result.get('risk_score', 'N/A')
            print(f"{name}: {risk_score}/100 risk")
    
    elif choice == "2":
        # Test specific address
        print("\nSelect address to test:")
        for i, (name, address) in enumerate(TEST_ADDRESSES.items(), 1):
            print(f"{i}. {name}")
        
        try:
            selection = int(input("Enter number: ")) - 1
            if 0 <= selection < len(TEST_ADDRESSES):
                name, address = list(TEST_ADDRESSES.items())[selection]
                analyze_contract(address, name)
            else:
                print("❌ Invalid selection")
        except ValueError:
            print("❌ Invalid input")
    
    elif choice == "3":
        # Test custom address
        test_custom_address()
    
    elif choice == "4":
        # Quick test
        print("\n🔍 Quick test (first 3 addresses)...")
        for i, (name, address) in enumerate(list(TEST_ADDRESSES.items())[:3]):
            analyze_contract(address, name)
            time.sleep(1)
    
    else:
        print("❌ Invalid choice")
    
    print("\n🎉 Testing completed!")
    print("\n💡 Tips:")
    print("- Use BscScan to find contract addresses: https://bscscan.com")
    print("- Look for 'Contract' tab on token pages")
    print("- Copy the contract address (not the token address)")
    print("- Test with both legitimate and suspicious contracts")

if __name__ == "__main__":
    main() 