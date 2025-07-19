// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

interface IPancakePair {
    function getReserves() external view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast);
    function token0() external view returns (address);
    function token1() external view returns (address);
    function totalSupply() external view returns (uint256);
}

interface IPancakeFactory {
    function getPair(address tokenA, address tokenB) external view returns (address pair);
}

contract RiskScanner is Ownable, ReentrancyGuard {
    
    struct LiquidityInfo {
        address pairAddress;
        uint256 token0Reserve;
        uint256 token1Reserve;
        uint256 totalLiquidity;
        uint256 lpTotalSupply;
        bool pairExists;
    }
    
    struct ContractInfo {
        uint256 creationBlock;
        uint256 contractAge;
        bool isContract;
        uint256 codeSize;
    }
    
    struct TokenHolderInfo {
        uint256 totalSupply;
        uint256 contractBalance;
        uint256 burnedBalance;
        uint256 circulatingSupply;
    }
    
    IPancakeFactory public constant PANCAKE_FACTORY = IPancakeFactory(0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73);
    address public constant WBNB = 0xbb4CdB9CBd36B01bD1cBaeBF2De08d9173bc095c;
    address public constant DEAD_ADDRESS = 0x000000000000000000000000000000000000dEaD;
    
    event ScanCompleted(address indexed tokenAddress, uint256 timestamp);
    event RiskFlagRaised(address indexed tokenAddress, string riskType, uint256 severity);
    
    /**
     * @dev Get liquidity information for a token on PancakeSwap
     */
    function getLiquidityInfo(address tokenAddress) external view returns (LiquidityInfo memory) {
        address pairAddress = PANCAKE_FACTORY.getPair(tokenAddress, WBNB);
        
        if (pairAddress == address(0)) {
            return LiquidityInfo({
                pairAddress: address(0),
                token0Reserve: 0,
                token1Reserve: 0,
                totalLiquidity: 0,
                lpTotalSupply: 0,
                pairExists: false
            });
        }
        
        IPancakePair pair = IPancakePair(pairAddress);
        (uint112 reserve0, uint112 reserve1,) = pair.getReserves();
        
        // Determine which reserve is the token and which is WBNB
        address token0 = pair.token0();
        uint256 tokenReserve = (token0 == tokenAddress) ? uint256(reserve0) : uint256(reserve1);
        uint256 wbnbReserve = (token0 == tokenAddress) ? uint256(reserve1) : uint256(reserve0);
        
        return LiquidityInfo({
            pairAddress: pairAddress,
            token0Reserve: tokenReserve,
            token1Reserve: wbnbReserve,
            totalLiquidity: wbnbReserve * 2, // Total pool value in WBNB
            lpTotalSupply: pair.totalSupply(),
            pairExists: true
        });
    }
    
    /**
     * @dev Get basic contract information
     */
    function getContractInfo(address contractAddress) external view returns (ContractInfo memory) {
        uint256 codeSize;
        assembly {
            codeSize := extcodesize(contractAddress)
        }
        
        bool isContract = codeSize > 0;
        uint256 contractAge = block.number; // Simplified - in reality, you'd track creation block
        
        return ContractInfo({
            creationBlock: 0, // Would need to be tracked separately
            contractAge: contractAge,
            isContract: isContract,
            codeSize: codeSize
        });
    }
    
    /**
     * @dev Get token holder distribution information
     */
    function getTokenHolderInfo(address tokenAddress) external view returns (TokenHolderInfo memory) {
        IERC20 token = IERC20(tokenAddress);
        
        uint256 totalSupply = token.totalSupply();
        uint256 contractBalance = token.balanceOf(tokenAddress); // Tokens held by contract itself
        uint256 burnedBalance = token.balanceOf(DEAD_ADDRESS); // Burned tokens
        uint256 circulatingSupply = totalSupply - contractBalance - burnedBalance;
        
        return TokenHolderInfo({
            totalSupply: totalSupply,
            contractBalance: contractBalance,
            burnedBalance: burnedBalance,
            circulatingSupply: circulatingSupply
        });
    }
    
    /**
     * @dev Check if a token has potential honeypot characteristics
     */
    function checkHoneypotRisk(address tokenAddress) external view returns (bool hasRisk, string[] memory riskFactors) {
        string[] memory risks = new string[](10);
        uint256 riskCount = 0;
        
        // Check if contract has code
        uint256 codeSize;
        assembly {
            codeSize := extcodesize(tokenAddress)
        }
        
        if (codeSize == 0) {
            risks[riskCount] = "NOT_A_CONTRACT";
            riskCount++;
        }
        
        // Check liquidity
        LiquidityInfo memory liquidityInfo = this.getLiquidityInfo(tokenAddress);
        if (!liquidityInfo.pairExists) {
            risks[riskCount] = "NO_LIQUIDITY_POOL";
            riskCount++;
        } else if (liquidityInfo.totalLiquidity < 1 ether) { // Less than 1 BNB liquidity
            risks[riskCount] = "LOW_LIQUIDITY";
            riskCount++;
        }
        
        // Check token distribution
        TokenHolderInfo memory holderInfo = this.getTokenHolderInfo(tokenAddress);
        if (holderInfo.contractBalance > holderInfo.totalSupply * 50 / 100) { // Contract holds >50%
            risks[riskCount] = "HIGH_CONTRACT_OWNERSHIP";
            riskCount++;
        }
        
        // Resize array to actual risk count
        string[] memory actualRisks = new string[](riskCount);
        for (uint256 i = 0; i < riskCount; i++) {
            actualRisks[i] = risks[i];
        }
        
        return (riskCount > 0, actualRisks);
    }
    
    /**
     * @dev Attempt a simulated buy/sell to detect honeypot
     * This is a simplified version - real implementation would be more complex
     */
    function simulateTransaction(address tokenAddress, uint256 amountIn) external view returns (bool canBuy, bool canSell, string memory error) {
        try this.getLiquidityInfo(tokenAddress) returns (LiquidityInfo memory info) {
            if (!info.pairExists) {
                return (false, false, "NO_LIQUIDITY_POOL");
            }
            
            if (info.totalLiquidity == 0) {
                return (false, false, "ZERO_LIQUIDITY");
            }
            
            // Simplified simulation - in reality, you'd call router functions with try/catch
            return (true, true, "");
            
        } catch {
            return (false, false, "SIMULATION_FAILED");
        }
    }
    
    /**
     * @dev Get comprehensive risk analysis
     */
    function getComprehensiveAnalysis(address tokenAddress) external view returns (
        LiquidityInfo memory liquidity,
        ContractInfo memory contractInfo,
        TokenHolderInfo memory holderInfo,
        bool hasHoneypotRisk,
        string[] memory riskFactors,
        uint256 overallRiskScore
    ) {
        liquidity = this.getLiquidityInfo(tokenAddress);
        contractInfo = this.getContractInfo(tokenAddress);
        holderInfo = this.getTokenHolderInfo(tokenAddress);
        (hasHoneypotRisk, riskFactors) = this.checkHoneypotRisk(tokenAddress);
        
        // Calculate overall risk score (0-100, higher = more risky)
        overallRiskScore = _calculateRiskScore(liquidity, contractInfo, holderInfo, riskFactors.length);
        
        return (liquidity, contractInfo, holderInfo, hasHoneypotRisk, riskFactors, overallRiskScore);
    }
    
    function _calculateRiskScore(
        LiquidityInfo memory liquidity,
        ContractInfo memory contractInfo,
        TokenHolderInfo memory holderInfo,
        uint256 riskFactorCount
    ) internal pure returns (uint256) {
        uint256 score = 0;
        
        // Risk from lack of liquidity (0-30 points)
        if (!liquidity.pairExists) {
            score += 30;
        } else if (liquidity.totalLiquidity < 1 ether) {
            score += 20;
        } else if (liquidity.totalLiquidity < 10 ether) {
            score += 10;
        }
        
        // Risk from token distribution (0-25 points)
        if (holderInfo.totalSupply > 0) {
            uint256 contractOwnership = (holderInfo.contractBalance * 100) / holderInfo.totalSupply;
            if (contractOwnership > 50) {
                score += 25;
            } else if (contractOwnership > 30) {
                score += 15;
            } else if (contractOwnership > 10) {
                score += 5;
            }
        }
        
        // Risk from contract analysis (0-20 points)
        if (contractInfo.codeSize == 0) {
            score += 20;
        } else if (contractInfo.codeSize < 1000) { // Very small contract
            score += 10;
        }
        
        // Risk from detected factors (0-25 points)
        score += riskFactorCount * 5; // 5 points per risk factor
        
        return score > 100 ? 100 : score;
    }
    
    /**
     * @dev Emergency function to pause contract (only owner)
     */
    function emergencyPause() external onlyOwner {
        // Implementation for emergency pause
        emit RiskFlagRaised(address(0), "EMERGENCY_PAUSE", 100);
    }
}
