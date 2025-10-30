#!/bin/bash

# Build production Docker image locally for testing
set -e

echo "🏗️  Building production Docker image..."

# Build the production image
docker build -f Dockerfile.production -t meeting-bot:production .

echo "✅ Production image built successfully!"
echo ""
echo "To run the production container:"
echo "docker run -d --name meeting-bot -p 4000:4000 meeting-bot:production"
echo ""
echo "To test the container:"
echo "curl http://localhost:4000/isbusy" 