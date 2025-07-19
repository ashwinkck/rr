#!/usr/bin/env python3
"""
RiskRobo API Server Startup Script
This script properly starts the FastAPI server with correct uvicorn configuration.
"""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_server():
    """Start the RiskRobo API server"""
    
    # Get configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 8000))
    reload = os.getenv('API_RELOAD', 'true').lower() == 'true'
    
    print("🚀 Starting RiskRobo API Server")
    print("=" * 40)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload mode: {reload}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print("=" * 40)
    
    try:
        if reload:
            # Development mode with auto-reload
            print("🔧 Development mode enabled (auto-reload on)")
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                reload=True,
                log_level="info"
            )
        else:
            # Production mode
            print("🏭 Production mode enabled")
            uvicorn.run(
                "main:app",
                host=host,
                port=port,
                workers=int(os.getenv('API_WORKERS', 1)),
                log_level="info"
            )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you have:")
        print("   1. Activated virtual environment")
        print("   2. Installed dependencies: pip install -r requirements.txt")
        print("   3. Configured .env file properly")

if __name__ == "__main__":
    start_server() 