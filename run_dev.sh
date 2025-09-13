#!/bin/bash

# Kill any existing processes on these ports
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔁 Starting FastAPI backend..."
uvicorn backend.api:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

echo "🌐 Starting Next.js frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

echo "✅ Services started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait
