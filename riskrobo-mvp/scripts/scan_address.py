#!/usr/bin/env python3
"""
Simple script to scan any BSC contract address with RiskRobo
Usage: python scan_address.py <contract_address>
"""

import requests
import json
import sys

def scan_address(address: str, base_url: str = "http://localhost:8000"):
    """Scan a contract address with RiskRobo"""
    
    print(f"🔍 Scanning contract: {address}")
    print("=" * 50)
    
    try:
        # Prepare request
        analysis_request = {
            "contract_address": address,
            "network": "bsc"
        }
        
        # Send request
        response = requests.post(
            f"{base_url}/analyze/contract",
            json=analysis_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Display results
            print(f"✅ Analysis completed!")
            print(f"📊 Risk Score: {result.get('risk_score', 'N/A')}/100")
            
            # Vulnerabilities
            vuln_flags = result.get('vulnerability_flags', [])
            if vuln_flags:
                print(f"🚨 Vulnerabilities: {', '.join(vuln_flags)}")
            else:
                print("✅ No vulnerabilities detected")
            
            # Liquidity
            liquidity = result.get('liquidity_data', {})
            if liquidity.get('has_liquidity'):
                print(f"💰 Liquidity: {liquidity.get('total_liquidity_bnb', 'N/A')} BNB")
                print(f"💵 USD Value: ~${liquidity.get('total_liquidity_usd', 'N/A')}")
            else:
                print("⚠️ No liquidity found")
            
            # Holder distribution
            holders = result.get('holder_analysis', {})
            if 'top_10_percentage' in holders:
                print(f"👥 Top 10 holders: {holders.get('top_10_percentage', 'N/A')}%")
                if holders.get('concentration_risk'):
                    print("⚠️ High holder concentration detected")
            
            # Show full details if requested
            show_full = input("\nShow full analysis details? (y/N): ").strip().lower()
            if show_full == 'y':
                print("\n📋 Full Analysis:")
                print(json.dumps(result, indent=2))
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python scan_address.py <contract_address>")
        print("Example: python scan_address.py 0x0E09FaBB73Bd3Ade0a17ECC321fD13a19e81cE82")
        sys.exit(1)
    
    address = sys.argv[1]
    
    # Validate address format
    if not address.startswith('0x') or len(address) != 42:
        print("❌ Invalid address format. Must be 42 characters starting with 0x")
        sys.exit(1)
    
    # Check if API is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ API is not responding. Please start the backend first:")
            print("cd backend && python main.py")
            sys.exit(1)
    except:
        print("❌ Cannot connect to API. Please start the backend first:")
        print("cd backend && python main.py")
        sys.exit(1)
    
    # Scan the address
    scan_address(address)

if __name__ == "__main__":
    main() 