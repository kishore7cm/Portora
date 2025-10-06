#!/bin/bash

echo "🚀 Starting EaseLi Backend Server..."

# Navigate to backend directory
cd /Users/kishorecm/Documents/EaseLi/backend

# Activate virtual environment
source ../venv/bin/activate

# Kill any existing processes on port 8001
echo "🔄 Stopping any existing servers on port 8001..."
lsof -ti:8001 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

# Start the server
echo "🚀 Starting Simple Portfolio API on port 8001..."
python simple_working_api.py
