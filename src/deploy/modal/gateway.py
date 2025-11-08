import modal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import uuid
from datetime import datetime
from dataclasses import dataclass, asdict

# Create Modal app and define base image
app = modal.App("meeting-bot")

base_image = (
    modal.Image.from_registry("node:18")
    .apt_install([
        "python3", "python3-pip", "python3-venv",
        "ffmpeg", "libnss3", "libxss1", "libasound2", "libatk1.0-0",
        "libatk-bridge2.0-0", "libcups2", "libxkbcommon-x11-0", "libgbm-dev",
        "libgl1-mesa-dri", "libgl1-mesa-glx", "mesa-utils", "xvfb", 
        "wget", "gnupg", "xorg", "xserver-xorg", "libx11-dev", "libxext-dev",
        "dos2unix"
    ])
    .run_commands([
        # Create symlink for python
        "ln -sf /usr/bin/python3 /usr/bin/python",
        
        # Install Chrome
        "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-key.gpg",
        "echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list",
        "apt-get update && apt-get install -y google-chrome-stable",
        
        # Create directories and files
        "mkdir -p /etc/opt/chrome/policies/managed",
        "mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix",
        "echo '{}' > /etc/opt/chrome/policies/managed/auto_launch_protocols.json"
    ])
    .pip_install(["requests"])
)

# Bot instance management
@dataclass
class BotInstance:
    """Represents a running bot instance"""
    instance_id: str
    meeting_params: Dict[str, Any]
    status: str  # "starting", "running", "completed", "failed"
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

class BotManager:
    """Manages the lifecycle of meeting bot instances"""
    
    def __init__(self):
        self.instances: Dict[str, BotInstance] = {}
        
    def create_instance(self, meeting_params: Dict[str, Any]) -> str:
        """Create a new bot instance with unique ID"""
        instance_id = str(uuid.uuid4())
        
        instance = BotInstance(
            instance_id=instance_id,
            meeting_params=meeting_params,
            status="starting",
            started_at=datetime.utcnow()
        )
        
        self.instances[instance_id] = instance
        return instance_id
    
    def get_instance(self, instance_id: str) -> Optional[BotInstance]:
        """Get bot instance by ID"""
        return self.instances.get(instance_id)
    
    def update_instance_status(
        self, 
        instance_id: str, 
        status: str, 
        error_message: Optional[str] = None
    ):
        """Update the status of a bot instance"""
        if instance_id in self.instances:
            instance = self.instances[instance_id]
            instance.status = status
            
            if status in ["completed", "failed"]:
                instance.completed_at = datetime.utcnow()
                
            if error_message:
                instance.error_message = error_message
    
    def list_instances(self) -> Dict[str, Dict[str, Any]]:
        """List all bot instances"""
        return {
            instance_id: asdict(instance) 
            for instance_id, instance in self.instances.items()
        }

# Global bot manager instance
bot_manager = BotManager()

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
        print("Meeting bot is running...")
        
        # Wait for the process to complete naturally
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

# FastAPI app for the gateway
gateway_app = FastAPI(title="Meeting Bot Gateway")

class JoinMeetingRequest(BaseModel):
    """Request model for joining a meeting"""
    meeting_url: str
    bot_name: Optional[str] = "Meeting Bot"
    recording_enabled: Optional[bool] = True
    duration_minutes: Optional[int] = 60
    additional_params: Optional[Dict[str, Any]] = {}

class BotResponse(BaseModel):
    """Response model for bot operations"""
    instance_id: str
    status: str
    message: str

class BotStatusResponse(BaseModel):
    """Response model for bot status"""
    instance_id: str
    status: str
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None

@gateway_app.post("/bot/join", response_model=BotResponse)
async def join_meeting(request: JoinMeetingRequest):
    """
    Spin up a new meeting bot instance to join a meeting
    
    Args:
        request: Meeting parameters
        
    Returns:
        Bot instance information
    """
    try:
        # Prepare meeting parameters
        meeting_params = {
            "meeting_url": request.meeting_url,
            "bot_name": request.bot_name,
            "recording_enabled": request.recording_enabled,
            "duration_minutes": request.duration_minutes,
            **request.additional_params
        }
        
        # Create bot instance
        instance_id = bot_manager.create_instance(meeting_params)
        
        # Start the bot asynchronously using Modal
        asyncio.create_task(start_bot_async(instance_id, meeting_params))
        
        return BotResponse(
            instance_id=instance_id,
            status="starting",
            message="Meeting bot is being started"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@gateway_app.get("/bot/{instance_id}/status", response_model=BotStatusResponse)
async def get_bot_status(instance_id: str):
    """
    Get the status of a bot instance
    
    Args:
        instance_id: Bot instance ID
        
    Returns:
        Bot status information
    """
    instance = bot_manager.get_instance(instance_id)
    
    if not instance:
        raise HTTPException(status_code=404, detail="Bot instance not found")
    
    return BotStatusResponse(
        instance_id=instance.instance_id,
        status=instance.status,
        started_at=instance.started_at.isoformat(),
        completed_at=instance.completed_at.isoformat() if instance.completed_at else None,
        error_message=instance.error_message
    )

@gateway_app.get("/bot/instances")
async def list_bot_instances():
    """List all bot instances"""
    return bot_manager.list_instances()

@gateway_app.delete("/bot/{instance_id}")
async def terminate_bot(instance_id: str):
    """
    Terminate a bot instance (placeholder - actual termination would need Modal job management)
    
    Args:
        instance_id: Bot instance ID
    """
    instance = bot_manager.get_instance(instance_id)
    
    if not instance:
        raise HTTPException(status_code=404, detail="Bot instance not found")
    
    # In a real implementation, you'd cancel the Modal function call
    bot_manager.update_instance_status(instance_id, "terminated")
    
    return {"message": f"Bot instance {instance_id} termination requested"}

@gateway_app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "meeting-bot-gateway"}

async def start_bot_async(instance_id: str, meeting_params: Dict[str, Any]):
    """
    Start a bot instance asynchronously
    
    Args:
        instance_id: Bot instance ID
        meeting_params: Meeting parameters
    """
    try:
        # Update status to running
        bot_manager.update_instance_status(instance_id, "running")
        
        # Call the Modal function
        result = await run_meeting_bot.remote.aio(meeting_params)
        
        # Update status based on result
        if result.get("status") == "completed":
            bot_manager.update_instance_status(instance_id, "completed")
        else:
            bot_manager.update_instance_status(
                instance_id, 
                "failed", 
                result.get("message", "Unknown error")
            )
            
    except Exception as e:
        bot_manager.update_instance_status(
            instance_id, 
            "failed", 
            f"Error starting bot: {str(e)}"
        )

# Create Modal web app
@app.function()
@modal.asgi_app()
def web():
    return gateway_app