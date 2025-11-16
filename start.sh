#!/bin/bash
# Railway start script for FastAPI backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
# Railway provides $PORT environment variable automatically
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
