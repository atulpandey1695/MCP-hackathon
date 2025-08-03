#!/usr/bin/env python3
"""
Startup script for MCP Server
Ensures required directories exist and starts the server
"""
import os
import sys
from pathlib import Path

def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        "logs",
        "data"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Ensured directory exists: {directory}")

def main():
    """Main startup function"""
    print("Starting MCP Server...")
    
    # Ensure required directories exist
    ensure_directories()
    
    # Import and start server
    try:
        from server import app
        import uvicorn
        
        print("✓ Server imported successfully")
        print("Starting server on http://0.0.0.0:8000")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 