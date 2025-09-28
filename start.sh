#!/bin/bash

# EaseLi Startup Script
echo "🚀 Starting EaseLi Portfolio Dashboard..."

# Start Backend
echo "📡 Starting backend server..."
cd backend
python api.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
echo "🎨 Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ EaseLi is running!"
echo "📊 Dashboard: http://localhost:3000/dashboard"
echo "🔧 API: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait
