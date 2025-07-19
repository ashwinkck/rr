from web3 import Web3
import json
import os
from dotenv import load_dotenv

load_dotenv()

def deploy_risk_scanner():
    """Deploy RiskScanner contract to BSC testnet"""
    
    # Connect to BSC testnet
    w3 = Web3(Web3.HTTPProvider('https://bsc-testnet-dataseed.bnbchain.org'))
    
    # Account setup
    private_key = os.getenv('PRIVATE_KEY')
    account = w3.eth.account.from_key(private_key)
    
    print(f"Deploying from account: {account.address}")
    print(f"Balance: {w3.from_wei(w3.eth.get_balance(account.address), 'ether')} BNB")
    
    # Load compiled contract (you'd get this from hardhat artifacts)
    # For now, using placeholder - compile with: npx hardhat compile
    contract_path = '../contracts/artifacts/contracts/RiskScanner.sol/RiskScanner.json'
    
    try:
        with open(contract_path, 'r') as f:
            contract_data = json.load(f)
        
        # Create contract instance
        contract = w3.eth.contract(
            abi=contract_data['abi'],
            bytecode=contract_data['bytecode']
        )
        
        # Build deployment transaction
        transaction = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000,
            'gasPrice': w3.to_wei('5', 'gwei')
        })
        
        # Sign and send transaction
        signed_tx = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        print(f"Transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        print(f"Contract deployed at: {receipt.contractAddress}")
        print(f"Gas used: {receipt.gasUsed}")
        
        return receipt.contractAddress
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        return None

if __name__ == "__main__":
    deploy_risk_scanner()
