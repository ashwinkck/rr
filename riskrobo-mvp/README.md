# RiskRobo MVP - DeFi Risk Analysis Platform

A comprehensive DeFi risk analysis platform for the Binance Smart Chain (BSC) that helps users identify potential scams, honeypots, and risky tokens.

## 🏗️ Project Structure

```
riskrobo-mvp/
├── contracts/           # Smart contracts (Solidity)
│   ├── RiskScanner.sol  # Main risk analysis contract
│   ├── hardhat.config.ts
│   └── package.json
├── backend/             # FastAPI backend services
│   ├── main.py         # Main API server
│   ├── services/       # Analysis services
│   │   ├── contract_analyzer.py
│   │   ├── liquidity_analyzer.py
│   │   └── mempool_monitor.py
│   ├── daemon_manager.py
│   └── requirements.txt
├── scripts/            # Deployment and testing scripts
│   ├── deploy_contracts.py
│   └── test_api.py
└── tests/              # Test files
```

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- BSC RPC access
- BscScan API key

### 1. Setup Smart Contracts

```bash
cd contracts
npm install
npx hardhat compile
```

### 2. Setup Backend

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `backend/env.example` to `backend/.env` and fill in your values:

```bash
cp backend/env.example backend/.env
```

Required environment variables:
- `BSC_MAINNET_RPC_1`, `BSC_MAINNET_RPC_2` - BSC RPC endpoints
- `BSCSCAN_API_KEY` - 
- `PRIVATE_KEY` - For contract deployment (optional)

### 4. Deploy Contracts

```bash
cd scripts
python deploy_contracts.py
```

### 5. Start Backend API

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`

## 📊 API Endpoints

### Analyze Contract
```bash
POST /analyze/contract
{
  "contract_address": "0x...",
  "network": "bsc"
}
```

### Health Check
```bash
GET /
```

## 🔍 Features

### Smart Contract Analysis
- Vulnerability detection (reentrancy, access control, etc.)
- Contract age analysis
- Code size verification

### Liquidity Analysis
- PancakeSwap liquidity pool analysis
- LP token holder concentration
- Liquidity lock detection

### Mempool Monitoring
- Real-time transaction monitoring
- Risk pattern detection
- Alert system for suspicious activities

### Risk Scoring
- Comprehensive risk scoring algorithm (0-100)
- Multiple risk factors consideration
- Real-time updates

## 🛠️ Development

### Running Tests
```bash
cd contracts
npx hardhat test

cd backend
python -m pytest tests/
```

### Code Quality
```bash
# Solidity
npx hardhat lint

# Python
pip install black flake8
black backend/
flake8 backend/
```

## 🔧 Configuration

### Hardhat Configuration
The `hardhat.config.ts` supports:
- BSC Mainnet and Testnet
- Multiple RPC endpoints for failover
- BscScan API integration

### Backend Configuration
- Multiple RPC endpoint support
- Configurable risk thresholds
- WebSocket connection for mempool monitoring

## 🚨 Known Issues & Fixes

### TypeScript Configuration Error
**Issue**: `Option 'moduleResolution' must be set to 'NodeNext'`
**Fix**: Added `tsconfig.json` with proper module resolution

### Missing Dependencies
**Issue**: OpenZeppelin contracts not installed
**Fix**: Added `@openzeppelin/contracts` to package.json

### Environment Variables
**Issue**: Missing environment configuration
**Fix**: Created `env.example` template

## 📈 Roadmap

- [ ] Frontend web interface
- [ ] Advanced honeypot detection
- [ ] Multi-chain support
- [ ] Machine learning risk models
- [ ] Real-time price feeds
- [ ] User alert system
- [ ] Mobile app

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always do your own research before investing in any DeFi project. The risk analysis provided is not financial advice. 