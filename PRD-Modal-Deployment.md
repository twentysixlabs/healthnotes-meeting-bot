# PRD: Modal Cloud Meeting Bot Deployment Architecture

## Executive Summary

This PRD outlines the implementation of a simple meeting bot deployment system using Modal Cloud. The solution focuses on spinning up containers on-demand to join meetings using a base image + sandbox architecture.

## Product Overview

### Current State
- Meeting bot application (`meeting-bot`) with Node.js/TypeScript codebase
- Production Dockerfile with system dependencies (Chrome, ffmpeg, audio/video libs)
- Express API server listening on port 4000
- Application accepts parameters via API to join meetings
- Manual container deployment and management

### Target Architecture
- **Base Image Layer**: Pre-built, cached Modal image with all dependencies installed
- **Sandbox Layer**: On-demand container instances spawned from base image
- **API Gateway**: Request routing and container orchestration

## Technical Architecture

### 1. Base Image Strategy

**Components:**
- Ubuntu base with Node.js 18
- System dependencies: Chrome, ffmpeg, audio/video libraries, X11 support
- NPM dependencies pre-installed (`npm ci`)
- TypeScript build artifacts (`npm run build`)
- Playwright browser binaries

**Modal Implementation:**
```python
# Base image definition (no implementation, just structure)
@app.function(
    image=Image.from_dockerfile("Dockerfile.production")
        .pip_install(["modal"]),
    keep_warm=1,  # Keep base image warm
    timeout=3600  # 1 hour max per meeting
)
```

### 2. Sandbox Architecture

**Container Lifecycle:**
1. API request received with meeting parameters
2. Modal spins up sandbox from cached base image
3. Meeting parameters forwarded to containerized Express app
4. Bot joins meeting
5. Container terminated after meeting completion

**Request Flow:**
```text
User Request → Modal API Gateway → Container Sandbox → Meeting Bot App
```

**Endpoints:**
- `POST /bot/join` - Spin up new meeting bot instance

## Implementation Requirements

### Phase 1: Base Infrastructure
1. **Modal Environment Setup**
   - Modal account and project configuration
   - Convert `Dockerfile.production` to Modal image spec

2. **Sandbox Framework**
   - Container lifecycle management
   - Parameter injection mechanism

### Phase 2: API Integration
1. **Request Routing**
   - API gateway implementation
   - Dynamic container spawning

## Technical Specifications

### Container Resource Requirements
- **CPU**: 2-4 vCPUs per instance
- **Memory**: 4-8 GB RAM (Chrome + video processing)
- **Storage**: 2 GB ephemeral (temporary video files)

## Timeline

### Phase 1 (Weeks 1-2)
- Modal environment setup
- Base image conversion and testing
- Basic sandbox framework

### Phase 2 (Weeks 3-4)
- API gateway implementation
- Container orchestration logic

### Dependencies
- Modal Cloud account and credits allocation
- Meeting platform API access and credentials