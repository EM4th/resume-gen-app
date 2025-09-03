#!/bin/bash

# Resume Generator Startup Script
echo "🚀 Starting Resume Generator..."

# Kill any existing processes
pkill -f "python app.py" 2>/dev/null || true
sleep 1

# Navigate to project directory
cd /Users/em4/Desktop/resume-gen

# Activate virtual environment
source venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
pip install -q flask flask-cors reportlab pdfplumber google-generativeai python-dotenv

# Start the application
echo "🎯 Starting Flask application..."
echo "🌐 Access at: http://127.0.0.1:5001"
echo "📱 Local network: http://192.168.1.51:5001"
echo "⏹️  Press Ctrl+C to stop"

python app.py
