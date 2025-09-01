#!/bin/bash

# Resume Generator Startup Script
# This script sets up and starts the resume generator application

echo "🚀 Starting Resume Generator..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Please create one with your GOOGLE_API_KEY"
    echo "   You can copy .env.example to .env and add your API key"
    echo "   Get your API key from: https://aistudio.google.com/app/apikey"
    exit 1
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f ngrok 2>/dev/null || true
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

sleep 2

# Start Flask app in background
echo "🌐 Starting Flask application..."
./venv/bin/python app.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Check if Flask is running
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/ | grep -q "200"; then
    echo "✅ Flask app is running on http://localhost:8080"
else
    echo "❌ Flask app failed to start"
    kill $FLASK_PID 2>/dev/null || true
    exit 1
fi

# Start ngrok tunnel
echo "🌍 Starting ngrok tunnel..."
ngrok http 8080 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 3

# Get ngrok URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o '"public_url":"https://[^"]*"' | head -1 | cut -d'"' -f4)

if [ -n "$NGROK_URL" ]; then
    echo "🎉 Resume Generator is ready!"
    echo "📱 Local URL: http://localhost:8080"
    echo "🌐 Public URL: $NGROK_URL"
    echo ""
    echo "💡 Features available:"
    echo "   • AI-powered resume transformations"
    echo "   • Detailed explanation boxes"
    echo "   • Professional PDF generation"
    echo "   • Job description matching"
    echo ""
    echo "🛑 To stop: Press Ctrl+C or run 'pkill -f ngrok && pkill -f \"python.*app.py\"'"
else
    echo "⚠️  Ngrok tunnel may not be ready yet. Check http://127.0.0.1:4040 for the public URL"
fi

# Keep script running
wait
