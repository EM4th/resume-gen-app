#!/bin/bash
# Deploy Resume Generator App

echo "🚀 Deploying Resume Generator App..."

# Stop any existing processes
pkill -f "python app.py" 2>/dev/null || true
sleep 2

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Start the application
echo "Starting application..."
nohup python app.py > app.log 2>&1 &

# Wait a moment and check if it's running
sleep 3

# Check health
if curl -s http://127.0.0.1:5001/health > /dev/null; then
    echo "✅ Application deployed successfully!"
    echo "🌐 Access at: http://127.0.0.1:5001"
    echo "📊 Health check: http://127.0.0.1:5001/health"
    echo "📄 Logs: tail -f app.log"
else
    echo "❌ Deployment failed. Check app.log for errors."
    exit 1
fi
