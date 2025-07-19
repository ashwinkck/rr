from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from web3 import Web3
import os
from dotenv import load_dotenv
import asyncio
from typing import List, Dict, Any

load_dotenv()

app = FastAPI(title="RiskRobo API", version="1.0.0")

class ContractAnalysisRequest(BaseModel):
    contract_address: str
    network: str = "bsc"

class AnalysisResponse(BaseModel):
    contract_address: str
    risk_score: int
    vulnerability_flags: List[str]
    liquidity_data: Dict[str, Any]
    holder_analysis: Dict[str, Any]

# Initialize Web3 connections with failover
def get_web3_connection():
    rpc_urls = [
        os.getenv('BSC_MAINNET_RPC_1'),
        os.getenv('BSC_MAINNET_RPC_2'),
        os.getenv('BSC_MAINNET_RPC_3'),
        os.getenv('BSC_MAINNET_RPC_4'),
        os.getenv('QUICKNODE_BSC_RPC'),
        os.getenv('ALCHEMY_BSC_RPC'),
        os.getenv('INFURA_BSC_RPC')
    ]
    
    # Filter out None values
    rpc_urls = [url for url in rpc_urls if url and url != 'your-quicknode-bsc-endpoint' and url != 'your-alchemy-bsc-endpoint' and url != 'your-infura-bsc-endpoint']
    
    if not rpc_urls:
        raise Exception("No valid RPC URLs configured. Please check your .env file.")
    
    for url in rpc_urls:
        try:
            w3 = Web3(Web3.HTTPProvider(url))
            if w3.is_connected():
                print(f"Connected to BSC via {url}")
                return w3
        except Exception as e:
            print(f"Failed to connect to {url}: {e}")
            continue
    
    raise Exception("Failed to connect to BSC network. All RPC endpoints failed.")

w3 = get_web3_connection()

@app.get("/")
async def root():
    return {"message": "RiskRobo API is running", "network": "BSC", "connected": w3.is_connected()}

@app.post("/analyze/contract", response_model=AnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
    try:
        from services.contract_analyzer import ContractAnalyzer
        from services.liquidity_analyzer import LiquidityAnalyzer
        
        # Initialize analyzers
        contract_analyzer = ContractAnalyzer(w3)
        liquidity_analyzer = LiquidityAnalyzer(w3)
        
        # Run parallel analysis
        vulnerability_task = asyncio.create_task(
            contract_analyzer.analyze_vulnerabilities(request.contract_address)
        )
        liquidity_task = asyncio.create_task(
            liquidity_analyzer.analyze_pancake_liquidity(request.contract_address)
        )
        holder_task = asyncio.create_task(
            contract_analyzer.analyze_holder_distribution(request.contract_address)
        )
        
        # Gather results
        vulnerability_flags = await vulnerability_task
        liquidity_data = await liquidity_task
        holder_analysis = await holder_task
        
        # Calculate risk score (simplified algorithm)
        risk_score = calculate_risk_score(vulnerability_flags, liquidity_data, holder_analysis)
        
        return AnalysisResponse(
            contract_address=request.contract_address,
            risk_score=risk_score,
            vulnerability_flags=vulnerability_flags,
            liquidity_data=liquidity_data,
            holder_analysis=holder_analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def calculate_risk_score(vuln_flags, liquidity_data, holder_data):
    """Simple risk scoring algorithm"""
    score = 50  # Base score
    
    # Vulnerability penalties
    score += len(vuln_flags) * 15
    
    # Liquidity concentration penalty
    if liquidity_data.get('concentration_risk', False):
        score += 20
    
    # Holder concentration penalty
    if holder_data.get('top_10_percentage', 0) > 70:
        score += 25
    
    return min(100, max(0, score))

if __name__ == "__main__":
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    reload = os.getenv('API_RELOAD', 'true').lower() == 'true'
    
    print(f"Starting RiskRobo API server on {host}:{port}")
    print(f"Debug mode: {reload}")
    
    if reload:
        # For development with reload, use import string
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    else:
        # For production, use app object directly
        uvicorn.run(
            app,
            host=host,
            port=port,
            workers=int(os.getenv('API_WORKERS', 1)),
            log_level="info"
        )
