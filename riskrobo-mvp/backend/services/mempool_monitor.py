import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Callable
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()

class MempoolMonitor:
    def __init__(self, web3_instance: Web3, alert_callback: Callable = None):
        self.w3 = web3_instance
        self.alert_callback = alert_callback
        self.websocket_url = os.getenv('BSC_WEBSOCKET_URL')
        self.pancake_router = os.getenv('PANCAKE_ROUTER_V2').lower()
        self.is_running = False
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Risk patterns to monitor
        self.risk_patterns = {
            'large_sell': 10,  # BNB threshold for large sells
            'honeypot_interaction': True,
            'suspicious_tokens': []  # Will be populated
        }
    
    async def start_monitoring(self):
        """Start the mempool monitoring daemon"""
        self.is_running = True
        self.logger.info("Starting mempool monitoring daemon...")
        
        while self.is_running:
            try:
                await self._connect_and_monitor()
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(5)  # Wait before reconnecting
    
    async def stop_monitoring(self):
        """Stop the mempool monitoring daemon"""
        self.is_running = False
        self.logger.info("Stopping mempool monitoring daemon...")
    
    async def _connect_and_monitor(self):
        """Connect to BSC WebSocket and monitor transactions"""
        try:
            async with websockets.connect(self.websocket_url) as websocket:
                self.logger.info("Connected to BSC WebSocket")
                
                # Subscribe to pending transactions
                subscribe_message = {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": ["newPendingTransactions"]
                }
                
                await websocket.send(json.dumps(subscribe_message))
                subscription_response = await websocket.recv()
                self.logger.info(f"Subscription response: {subscription_response}")
                
                # Start listening for transactions
                async for message in websocket:
                    if not self.is_running:
                        break
                    
                    await self._process_mempool_message(message)
                    
        except Exception as e:
            self.logger.error(f"WebSocket connection error: {e}")
            raise
    
    async def _process_mempool_message(self, message: str):
        """Process incoming mempool messages"""
        try:
            data = json.loads(message)
            
            if 'params' in data and 'result' in data['params']:
                tx_hash = data['params']['result']
                await self._analyze_transaction(tx_hash)
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    async def _analyze_transaction(self, tx_hash: str):
        """Analyze a pending transaction for risk factors"""
        try:
            # Get transaction details
            tx = self.w3.eth.get_transaction(tx_hash)
            
            if not tx or not tx['to']:
                return
            
            # Check if transaction is interacting with PancakeSwap
            if tx['to'].lower() != self.pancake_router:
                return
            
            # Decode transaction data
            risk_data = await self._decode_pancake_transaction(tx)
            
            if risk_data['has_risk']:
                await self._trigger_alert(tx_hash, tx, risk_data)
                
        except Exception as e:
            self.logger.error(f"Error analyzing transaction {tx_hash}: {e}")
    
    async def _decode_pancake_transaction(self, tx: Dict[str, Any]) -> Dict[str, Any]:
        """Decode PancakeSwap transaction and assess risk"""
        try:
            # PancakeSwap Router method signatures
            method_signatures = {
                '0x38ed1739': 'swapExactTokensForTokens',
                '0x8803dbee': 'swapTokensForExactTokens', 
                '0x7ff36ab5': 'swapExactETHForTokens',
                '0x4a25d94a': 'swapTokensForExactETH',
                '0x18cbafe5': 'swapExactTokensForETH',
                '0xfb3bdb41': 'swapETHForExactTokens',
                '0x02751cec': 'removeLiquidity',
                '0xaf2979eb': 'removeLiquidityETH'
            }
            
            data = tx['data']
            if len(data) < 10:
                return {'has_risk': False}
            
            method_sig = data[:10]
            method_name = method_signatures.get(method_sig, 'unknown')
            
            risk_data = {
                'has_risk': False,
                'risk_type': None,
                'risk_level': 'low',
                'method': method_name,
                'value_bnb': float(self.w3.from_wei(tx['value'], 'ether'))
            }
            
            # Check for large value transactions
            if risk_data['value_bnb'] > self.risk_patterns['large_sell']:
                risk_data['has_risk'] = True
                risk_data['risk_type'] = 'large_transaction'
                risk_data['risk_level'] = 'high'
            
            # Check for liquidity removal (potential rug pull)
            if 'removeLiquidity' in method_name:
                # Decode the transaction data to get amounts
                if risk_data['value_bnb'] > 1.0:  # Removing significant liquidity
                    risk_data['has_risk'] = True
                    risk_data['risk_type'] = 'liquidity_removal'
                    risk_data['risk_level'] = 'critical'
            
            # TODO: Add more sophisticated analysis
            # - Check if interacting with suspicious tokens
            # - Analyze gas price (MEV bots often use high gas)
            # - Check transaction patterns
            
            return risk_data
            
        except Exception as e:
            self.logger.error(f"Error decoding transaction: {e}")
            return {'has_risk': False}
    
    async def _trigger_alert(self, tx_hash: str, tx: Dict[str, Any], risk_data: Dict[str, Any]):
        """Trigger risk alert"""
        alert = {
            'timestamp': asyncio.get_event_loop().time(),
            'tx_hash': tx_hash,
            'from_address': tx['from'],
            'to_address': tx['to'],
            'value_bnb': risk_data['value_bnb'],
            'risk_type': risk_data['risk_type'],
            'risk_level': risk_data['risk_level'],
            'method': risk_data['method']
        }
        
        self.logger.warning(f"RISK ALERT: {alert}")
        
        if self.alert_callback:
            await self.alert_callback(alert)

# Daemon wrapper for background execution
async def run_mempool_daemon():
    """Run the mempool monitor as a daemon"""
    from backend.main import get_web3_connection
    
    w3 = get_web3_connection()
    
    async def alert_handler(alert):
        # Store alert in database or send to API endpoint
        print(f"ALERT TRIGGERED: {alert}")
        # TODO: Implement alert storage/notification system
    
    monitor = MempoolMonitor(w3, alert_handler)
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(run_mempool_daemon())
