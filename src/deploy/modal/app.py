import modal
import json
import asyncio
from typing import Dict, Any, Optional

# Create Modal app
app = modal.App("meeting-bot")

# Define base image from our production Dockerfile
base_image = (
    modal.Image.from_dockerfile("Dockerfile.production")
    .pip_install(["modal", "requests"])
)

# Define the meeting bot function
@app.function(
    image=base_image,
    keep_warm=1,  # Keep one instance warm
    timeout=3600,  # 1 hour max per meeting
    cpu=4.0,      # 4 vCPUs
    memory=8192,  # 8GB RAM
)
def run_meeting_bot(meeting_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a meeting bot instance with the provided parameters.
    
    Args:
        meeting_params: Dictionary containing meeting parameters
        
    Returns:
        Dictionary with bot execution results
    """
    import subprocess
    import os
    import json
    import time
    import signal
    import requests
    
    # Write meeting parameters to environment or config file
    env = os.environ.copy()
    for key, value in meeting_params.items():
        env[f"BOT_{key.upper()}"] = str(value)
    
    try:
        # Start the meeting bot application
        print(f"Starting meeting bot with params: {meeting_params}")
        
        # Start the Node.js application in background
        process = subprocess.Popen(
            ["node", "dist/index.js"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/usr/src/app"
        )
        
        # Wait for the application to start (check health endpoint)
        max_retries = 30
        for _ in range(max_retries):
            try:
                response = requests.get("http://localhost:4000/health", timeout=5)
                if response.status_code == 200:
                    print("Meeting bot application started successfully")
                    break
            except requests.exceptions.RequestException:
                time.sleep(1)
        else:
            raise Exception("Failed to start meeting bot application")
        
        # Forward the meeting parameters to the bot API
        api_response = requests.post(
            "http://localhost:4000/api/join-meeting",
            json=meeting_params,
            timeout=30
        )
        
        if api_response.status_code != 200:
            raise Exception(f"Failed to join meeting: {api_response.text}")
        
        # Wait for the meeting to complete or timeout
        # In a real implementation, you'd monitor the meeting status
        print("Meeting bot is running...")
        
        # For now, we'll wait for the process to complete naturally
        # or until timeout (handled by Modal's timeout parameter)
        stdout, stderr = process.communicate()
        
        return {
            "status": "completed",
            "message": "Meeting bot finished successfully",
            "stdout": stdout.decode('utf-8')[-1000:],  # Last 1000 chars
            "stderr": stderr.decode('utf-8')[-1000:] if stderr else None
        }
        
    except Exception as e:
        print(f"Error running meeting bot: {str(e)}")
        # Try to terminate the process if it's still running
        try:
            if 'process' in locals() and process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
        except:
            pass
            
        return {
            "status": "error",
            "message": f"Meeting bot failed: {str(e)}"
        }

# Health check function for the Modal app
@app.function(
    image=modal.Image.debian_slim().pip_install(["modal"])
)
def health_check() -> Dict[str, str]:
    """Simple health check endpoint"""
    return {"status": "healthy", "service": "meeting-bot-modal"}