import modal
import asyncio
import uuid
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

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
        """
        Create a new bot instance with unique ID
        
        Args:
            meeting_params: Parameters for the meeting bot
            
        Returns:
            Instance ID
        """
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
    
    def cleanup_old_instances(self, max_age_hours: int = 24):
        """Remove instances older than max_age_hours"""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        to_remove = [
            instance_id for instance_id, instance in self.instances.items()
            if instance.started_at.timestamp() < cutoff_time
            and instance.status in ["completed", "failed"]
        ]
        
        for instance_id in to_remove:
            del self.instances[instance_id]

# Global bot manager instance
bot_manager = BotManager()