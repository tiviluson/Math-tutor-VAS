# Docker Deployment Guide

This guide explains how to deploy the AI Geometry Tutor backend using Docker.

## Quick Start

1. **Set up environment variables:**
   ```bash
   # Copy the template and fill in your API key
   copy .env.template .env
   # Edit .env and set your GOOGLE_API_KEY
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the API:**
   - API server: http://localhost:8000
   - API documentation: http://localhost:8000/docs


## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google API key for Gemini access | Required |
| `LLM_TEMPERATURE` | Temperature for LLM responses (0.0-1.0) | 0.1 |
| `MAX_OUTPUT_TOKENS` | Maximum output tokens | 2048 |