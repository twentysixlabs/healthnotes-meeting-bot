# Modal Cloud Meeting Bot Deployment

This directory contains the Modal Cloud deployment implementation for the meeting bot, following the architecture outlined in the PRD.

## Architecture Overview

```
User Request → Modal Gateway (FastAPI) → Container Sandbox → Meeting Bot App
```

## Files

- `app.py` - Core Modal application with base image and bot function
- `gateway.py` - FastAPI gateway for API endpoints and request routing
- `bot_manager.py` - Bot instance lifecycle management
- `deploy.py` - Deployment and local development script
- `requirements.txt` - Python dependencies for Modal deployment

## Quick Start

1. **Install Modal and authenticate:**
   ```bash
   pip install modal
   modal token new
   ```

2. **Deploy to Modal:**
   ```bash
   cd src/deploy/modal
   python deploy.py deploy
   ```

3. **For local development:**
   ```bash
   python deploy.py serve
   ```

## API Usage

Once deployed, you can use the API to spin up meeting bots:

### Join a Meeting
```bash
curl -X POST "https://your-modal-app-url/bot/join" \
  -H "Content-Type: application/json" \
  -d '{
    "meeting_url": "https://meet.google.com/abc-def-ghi",
    "bot_name": "My Bot",
    "recording_enabled": true,
    "duration_minutes": 60
  }'
```

Response:
```json
{
  "instance_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "starting",
  "message": "Meeting bot is being started"
}
```

### Check Bot Status
```bash
curl "https://your-modal-app-url/bot/550e8400-e29b-41d4-a716-446655440000/status"
```

### List All Instances
```bash
curl "https://your-modal-app-url/bot/instances"
```

## How It Works

1. **Base Image**: Built from `Dockerfile.production` with all dependencies pre-installed
2. **On-Demand Containers**: Modal spins up sandbox containers from the cached base image
3. **Parameter Injection**: Meeting parameters are passed as environment variables to the container
4. **Request Forwarding**: The bot parameters are forwarded to the Express app running inside the container
5. **Lifecycle Management**: Bot instances are tracked and automatically cleaned up after completion

## Configuration

The deployment uses the following resource specifications:
- **CPU**: 4 vCPUs per bot instance
- **Memory**: 8GB RAM
- **Timeout**: 1 hour maximum per meeting
- **Keep Warm**: 1 instance kept warm for faster cold starts

## Deployment Commands

```bash
# Check Modal authentication
python deploy.py check

# Deploy to Modal cloud
python deploy.py deploy

# Start local development server
python deploy.py serve
```

## Environment Variables

The bot application receives meeting parameters as environment variables with `BOT_` prefix:
- `BOT_MEETING_URL`
- `BOT_BOT_NAME`
- `BOT_RECORDING_ENABLED`
- `BOT_DURATION_MINUTES`

## Next Steps

1. Test the deployment with a real meeting URL
2. Monitor container startup times and optimize as needed
3. Add error handling and retry logic for failed meetings
4. Implement webhook notifications for meeting completion