import asyncio
from web3 import Web3
from typing import Dict, Any, List
import json
import os

class LiquidityAnalyzer:
    def __init__(self, web3_instance: Web3):
        self.w3 = web3_instance
        self.pancake_factory = os.getenv('PANCAKE_FACTORY_V2')
        self.pancake_router = os.getenv('PANCAKE_ROUTER_V2')
        
        # PancakeSwap V2 Factory ABI (minimal)
        self.factory_abi = [
            {
                "constant": True,
                "inputs": [
                    {"name": "tokenA", "type": "address"},
                    {"name": "tokenB", "type": "address"}
                ],
                "name": "getPair",
                "outputs": [{"name": "pair", "type": "address"}],
                "type": "function"
            }
        ]
        
        # ERC20 ABI (minimal)
        self.erc20_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }
        ]
        
        # PancakeSwap V2 Pair ABI (minimal)
        self.pair_abi = [
            {
                "constant": True,
                "inputs": [],
                "name": "getReserves",
                "outputs": [
                    {"name": "_reserve0", "type": "uint112"},
                    {"name": "_reserve1", "type": "uint112"},
                    {"name": "_blockTimestampLast", "type": "uint32"}
                ],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token0",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "token1",
                "outputs": [{"name": "", "type": "address"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]
    
    async def analyze_pancake_liquidity(self, token_address: str) -> Dict[str, Any]:
        """Analyze PancakeSwap liquidity for a token"""
        try:
            # WBNB address on BSC
            WBNB = "0xbb4CdB9CBd36B01bD1cBaeBF2De08d9173bc095c"
            
            # Get the pair address for token/WBNB
            factory_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.pancake_factory),
                abi=self.factory_abi
            )
            
            pair_address = factory_contract.functions.getPair(
                Web3.to_checksum_address(token_address),
                Web3.to_checksum_address(WBNB)
            ).call()
            
            if pair_address == "0x0000000000000000000000000000000000000000":
                return {
                    "error": "No PancakeSwap pair found",
                    "has_liquidity": False,
                    "pair_address": None
                }
            
            # Analyze the pair
            pair_data = await self._analyze_pair(pair_address, token_address, WBNB)
            
            return {
                "pair_address": pair_address,
                "has_liquidity": True,
                **pair_data
            }
            
        except Exception as e:
            print(f"Error analyzing PancakeSwap liquidity: {e}")
            return {
                "error": str(e),
                "has_liquidity": False
            }
    
    async def _analyze_pair(self, pair_address: str, token_address: str, wbnb_address: str) -> Dict[str, Any]:
        """Analyze a specific PancakeSwap pair"""
        try:
            pair_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=self.pair_abi
            )
            
            # Get pair reserves
            reserves = pair_contract.functions.getReserves().call()
            reserve0, reserve1, _ = reserves
            
            # Get token addresses in the pair
            token0 = pair_contract.functions.token0().call()
            token1 = pair_contract.functions.token1().call()
            
            # Determine which reserve corresponds to our token
            if token0.lower() == token_address.lower():
                token_reserve = reserve0
                bnb_reserve = reserve1
            else:
                token_reserve = reserve1
                bnb_reserve = reserve0
            
            # Convert reserves to readable format (assuming 18 decimals)
            token_reserve_readable = token_reserve / (10 ** 18)
            bnb_reserve_readable = bnb_reserve / (10 ** 18)
            
            # Calculate total liquidity in BNB
            total_liquidity_bnb = bnb_reserve_readable * 2  # Total pool value in BNB
            
            # Get LP token total supply to calculate concentration
            lp_total_supply = pair_contract.functions.totalSupply().call()
            
            # Analyze LP token holder concentration
            concentration_data = await self._analyze_lp_concentration(pair_address, lp_total_supply)
            
            return {
                "token_reserve": token_reserve_readable,
                "bnb_reserve": bnb_reserve_readable,
                "total_liquidity_bnb": total_liquidity_bnb,
                "total_liquidity_usd": total_liquidity_bnb * 300,  # Approximate BNB price
                "lp_total_supply": lp_total_supply,
                "concentration_risk": concentration_data.get("concentration_risk", False),
                "top_lp_holders": concentration_data.get("top_holders", []),
                "liquidity_locked": await self._check_liquidity_locks(pair_address)
            }
            
        except Exception as e:
            print(f"Error analyzing pair: {e}")
            return {"error": str(e)}
    
    async def _analyze_lp_concentration(self, pair_address: str, total_supply: int) -> Dict[str, Any]:
        """Analyze LP token holder concentration"""
        try:
            # This is a simplified version
            # In production, you'd query the top LP holders from BSCScan or other sources
            
            # Placeholder data - implement actual LP holder analysis
            return {
                "concentration_risk": False,  # True if top 3 holders have >60% of LP tokens
                "top_holders": [
                    {"address": "0x123...", "percentage": 25.5},
                    {"address": "0x456...", "percentage": 18.2},
                    {"address": "0x789...", "percentage": 15.1}
                ]
            }
            
        except Exception as e:
            print(f"Error analyzing LP concentration: {e}")
            return {"concentration_risk": True}  # Assume risk on error
    
    async def _check_liquidity_locks(self, pair_address: str) -> Dict[str, Any]:
        """Check if liquidity is locked in common locking contracts"""
        try:
            # Common BSC liquidity lock contracts
            lock_contracts = [
                "0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE",  # PinkLock
                "0x71B5759d73262FBb223956913ecF4ecC51057641",  # Team.Finance
                "0xC765bddB93b0D1c1A88282BA0fa6B2d00E3e0c83",  # CryptEx Lock
            ]
            
            erc20_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address),
                abi=self.erc20_abi
            )
            
            locked_balances = []
            total_locked = 0
            
            for lock_contract in lock_contracts:
                try:
                    balance = erc20_contract.functions.balanceOf(
                        Web3.to_checksum_address(lock_contract)
                    ).call()
                    
                    if balance > 0:
                        locked_balances.append({
                            "lock_contract": lock_contract,
                            "locked_amount": balance
                        })
                        total_locked += balance
                        
                except Exception:
                    continue
            
            # Get total LP supply
            total_supply = erc20_contract.functions.totalSupply().call()
            locked_percentage = (total_locked / total_supply * 100) if total_supply > 0 else 0
            
            return {
                "is_locked": locked_percentage > 0,
                "locked_percentage": round(locked_percentage, 2),
                "locked_balances": locked_balances,
                "liquidity_safety_score": min(100, locked_percentage)  # Higher is safer
            }
            
        except Exception as e:
            print(f"Error checking liquidity locks: {e}")
            return {
                "is_locked": False,
                "locked_percentage": 0,
                "liquidity_safety_score": 0
            }
