#!/bin/bash

echo "🔍 Checking Resume Generator Status..."
echo "=================================="

# Check if server is running
if curl -s -f http://127.0.0.1:5001/health > /dev/null 2>&1; then
    echo "✅ SERVER STATUS: Running"
    echo "🌐 Main App: http://127.0.0.1:5001"
    echo "🧪 Test Page: http://127.0.0.1:5001/test"
    echo "📱 Network: http://192.168.1.51:5001"
    
    # Check recent activity
    if [ -f server.log ]; then
        echo ""
        echo "📊 Recent Activity:"
        tail -3 server.log | grep -E "(GET|POST)" | tail -2
    fi
else
    echo "❌ SERVER STATUS: Not Running"
    echo ""
    echo "🚀 To start the server:"
    echo "   cd /Users/em4/Desktop/resume-gen"
    echo "   ./start_server.sh"
    echo ""
    echo "🔧 To start in background:"
    echo "   cd /Users/em4/Desktop/resume-gen"
    echo "   source venv/bin/activate && nohup python app.py > server.log 2>&1 &"
fi

echo ""
echo "📋 Process Info:"
ps aux | grep "python app.py" | grep -v grep || echo "No Python server process found"
