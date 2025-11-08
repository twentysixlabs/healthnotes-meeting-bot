#!/usr/bin/env python3
"""
Deployment script for the meeting bot Modal application.
This script handles the deployment and management of the Modal app.
"""

import subprocess
import sys
import os
from pathlib import Path

def deploy_app():
    """Deploy the Modal application"""
    print("Deploying meeting bot Modal application...")
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    
    try:
        # Deploy the app
        result = subprocess.run(
            ["modal", "deploy", str(script_dir / "gateway.py")],
            cwd=script_dir.parent.parent.parent,  # Go back to project root
            check=True
        )
        
        print("✓ Modal application deployed successfully")
        print("\nTo view your deployed app:")
        print("1. Run 'modal app list' to see all apps")
        print("2. Run 'modal serve gateway.py' for local development")
        print("3. Check Modal dashboard for the web endpoint URL")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Deployment failed: {e}")
        return False

def serve_locally():
    """Serve the app locally for development"""
    print("Starting local development server...")
    
    script_dir = Path(__file__).parent
    
    try:
        subprocess.run(
            ["modal", "serve", str(script_dir / "gateway.py")],
            cwd=script_dir.parent.parent.parent,
            check=True
        )
    except KeyboardInterrupt:
        print("\n✓ Development server stopped")
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to start development server: {e}")

def main():
    """Main deployment function"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python deploy.py deploy    - Deploy to Modal cloud")
        print("  python deploy.py serve     - Start local development server")
        return
    
    command = sys.argv[1]
    
    if command == "deploy":
        deploy_app()
    elif command == "serve":
        serve_locally()
    else:
        print(f"Unknown command: {command}")
        print("Available commands: deploy, serve")

if __name__ == "__main__":
    main()