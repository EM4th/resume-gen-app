#!/bin/bash

# Resume Generator Stop Script
# This script stops all resume generator processes

echo "🛑 Stopping Resume Generator..."

# Stop ngrok
echo "📡 Stopping ngrok..."
pkill -f ngrok 2>/dev/null || true

# Stop Flask app
echo "🌐 Stopping Flask application..."
pkill -f "python.*app.py" 2>/dev/null || true

# Kill any processes using port 8080
echo "🧹 Cleaning up port 8080..."
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

echo "✅ Resume Generator stopped successfully!"
echo "💡 To restart, run: ./start.sh"
