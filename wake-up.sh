#!/bin/bash

# Resume Generator - Wake Up Script
# This script helps wake up the Render app if it's sleeping (cold start)

echo "🔥 Waking up resume-gen.app..."

# Try multiple endpoints to ensure the app starts
echo "Testing health endpoint..."
curl -f https://resume-gen.app/health || echo "Health check failed, trying main page..."

echo "Testing main page..."
curl -f https://resume-gen.app/ > /dev/null || echo "Main page failed"

echo "✅ Wake up complete. App should be responsive now."
echo "🌐 Visit: https://resume-gen.app"
