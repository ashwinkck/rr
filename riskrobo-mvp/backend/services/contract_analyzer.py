import asyncio
from web3 import Web3
from typing import List, Dict, Any
import requests
import os

class ContractAnalyzer:
    def __init__(self, web3_instance: Web3):
        self.w3 = web3_instance
        self.bscscan_api_key = os.getenv('BSCSCAN_API_KEY')
        self.bscscan_base_url = "https://api.bscscan.com/api"
    
    async def analyze_vulnerabilities(self, contract_address: str) -> List[str]:
        """Analyze contract for common vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Get contract source code from BscScan
            source_code = await self._get_contract_source(contract_address)
            if not source_code:
                return ["SOURCE_CODE_NOT_VERIFIED"]
            
            # Check for common vulnerability patterns
            vulnerabilities.extend(self._check_reentrancy_vulnerability(source_code))
            vulnerabilities.extend(self._check_access_control(source_code))
            vulnerabilities.extend(self._check_overflow_underflow(source_code))
            vulnerabilities.extend(self._check_honeypot_patterns(source_code))
            
            # Check contract age
            contract_age = await self._get_contract_age(contract_address)
            if contract_age < 7:  # Less than 7 days old
                vulnerabilities.append("NEW_CONTRACT_HIGH_RISK")
            
            return vulnerabilities
            
        except Exception as e:
            print(f"Error analyzing vulnerabilities: {e}")
            return ["ANALYSIS_FAILED"]
    
    async def _get_contract_source(self, address: str) -> str:
        """Fetch contract source code from BscScan"""
        params = {
            'module': 'contract',
            'action': 'getsourcecode',
            'address': address,
            'apikey': self.bscscan_api_key
        }
        
        try:
            response = requests.get(self.bscscan_base_url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == '1' and data['result'][0]['SourceCode']:
                return data['result'][0]['SourceCode']
            return None
            
        except Exception as e:
            print(f"Error fetching source code: {e}")
            return None
    
    def _check_reentrancy_vulnerability(self, source_code: str) -> List[str]:
        """Check for reentrancy vulnerability patterns"""
        vulnerabilities = []
        
        # Simple pattern matching for reentrancy indicators
        reentrancy_patterns = [
            'call.value(',
            '.call{value:',
            'send(',
            'transfer('
        ]
        
        # Check if external calls are made before state changes
        lines = source_code.split('\n')
        for i, line in enumerate(lines):
            for pattern in reentrancy_patterns:
                if pattern in line.lower():
                    # Look for state changes after external calls (simplified)
                    for j in range(i+1, min(i+10, len(lines))):
                        if '=' in lines[j] and ('balance' in lines[j].lower() or 'amount' in lines[j].lower()):
                            vulnerabilities.append("POTENTIAL_REENTRANCY")
                            break
        
        return vulnerabilities
    
    def _check_access_control(self, source_code: str) -> List[str]:
        """Check for access control vulnerabilities"""
        vulnerabilities = []
        
        # Check for unprotected critical functions
        critical_functions = ['mint', 'burn', 'withdraw', 'setOwner', 'transferOwnership']
        
        for func in critical_functions:
            if func in source_code:
                # Simple check - look for modifier usage
                func_line_index = source_code.find(f'function {func}')
                if func_line_index != -1:
                    func_section = source_code[func_line_index:func_line_index+200]
                    if 'onlyOwner' not in func_section and 'require(' not in func_section:
                        vulnerabilities.append(f"UNPROTECTED_FUNCTION_{func.upper()}")
        
        return vulnerabilities
    
    def _check_overflow_underflow(self, source_code: str) -> List[str]:
        """Check for integer overflow/underflow vulnerabilities"""
        vulnerabilities = []
        
        # Check if SafeMath is used or Solidity version >= 0.8.0
        if 'SafeMath' not in source_code and 'pragma solidity ^0.8' not in source_code:
            if '+' in source_code or '-' in source_code or '*' in source_code:
                vulnerabilities.append("POTENTIAL_INTEGER_OVERFLOW")
        
        return vulnerabilities
    
    def _check_honeypot_patterns(self, source_code: str) -> List[str]:
        """Check for common honeypot patterns"""
        vulnerabilities = []
        
        # Check for hidden transfer restrictions
        honeypot_indicators = [
            'onlyOwner',
            'blacklist',
            'isBot',
            'cooldown',
            'maxTxAmount'
        ]
        
        for indicator in honeypot_indicators:
            if indicator in source_code:
                vulnerabilities.append(f"HONEYPOT_INDICATOR_{indicator.upper()}")
        
        return vulnerabilities
    
    async def _get_contract_age(self, address: str) -> int:
        """Get contract age in days"""
        try:
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': address,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': 1,
                'sort': 'asc',
                'apikey': self.bscscan_api_key
            }
            
            response = requests.get(self.bscscan_base_url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == '1' and data['result']:
                creation_timestamp = int(data['result'][0]['timeStamp'])
                current_timestamp = asyncio.get_event_loop().time()
                return int((current_timestamp - creation_timestamp) / 86400)  # Convert to days
            
            return 0
            
        except Exception as e:
            print(f"Error getting contract age: {e}")
            return 0
    
    async def analyze_holder_distribution(self, contract_address: str) -> Dict[str, Any]:
        """Analyze token holder distribution"""
        try:
            # Get top token holders
            holders_data = await self._get_top_holders(contract_address)
            
            if not holders_data:
                return {"error": "Unable to fetch holder data"}
            
            total_supply = float(holders_data.get('total_supply', 0))
            holders = holders_data.get('holders', [])
            
            if not holders or total_supply == 0:
                return {"error": "Invalid holder data"}
            
            # Calculate concentration metrics
            top_1_percentage = (float(holders[0]['balance']) / total_supply) * 100 if holders else 0
            top_5_percentage = sum(float(h['balance']) for h in holders[:5]) / total_supply * 100
            top_10_percentage = sum(float(h['balance']) for h in holders[:10]) / total_supply * 100
            
            return {
                "total_holders": len(holders),
                "top_1_percentage": round(top_1_percentage, 2),
                "top_5_percentage": round(top_5_percentage, 2),
                "top_10_percentage": round(top_10_percentage, 2),
                "concentration_risk": top_10_percentage > 70,
                "holders": holders[:10]  # Return top 10 for analysis
            }
            
        except Exception as e:
            print(f"Error analyzing holder distribution: {e}")
            return {"error": str(e)}
    
    async def _get_top_holders(self, contract_address: str) -> Dict[str, Any]:
        """Fetch top token holders from BscScan"""
        # Note: This is a simplified version. BscScan API has limitations for holder data
        # In production, you might need to use alternative data sources or build your own indexer
        
        try:
            # This is a placeholder - implement actual holder fetching logic
            # You might need to use services like Bitquery, The Graph, or Moralis
            return {
                "total_supply": 1000000,
                "holders": [
                    {"address": "0x123...", "balance": 100000},
                    {"address": "0x456...", "balance": 50000},
                    # ... more holders
                ]
            }
        except Exception as e:
            print(f"Error fetching holders: {e}")
            return None
