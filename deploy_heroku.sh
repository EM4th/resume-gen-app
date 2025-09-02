#!/bin/bash

# Quick Deployment Script for Heroku

echo "🚀 Deploying Resume Generator to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   brew install heroku/brew/heroku  # macOS"
    echo "   Or visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Login to Heroku (if not already logged in)
echo "🔐 Checking Heroku login..."
heroku auth:whoami || heroku login

# Create Heroku app (you can change the name)
echo "📱 Creating Heroku app..."
read -p "Enter your app name (or press Enter for auto-generated): " APP_NAME

if [ -z "$APP_NAME" ]; then
    heroku create
else
    heroku create $APP_NAME
fi

# Set environment variables
echo "🔑 Setting environment variables..."
read -p "Enter your Google AI API Key: " GOOGLE_API_KEY
heroku config:set GOOGLE_API_KEY=$GOOGLE_API_KEY

# Configure for production
heroku config:set FLASK_ENV=production

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy to Heroku"
git push heroku main

# Open the app
echo "✅ Deployment complete!"
heroku open

echo ""
echo "🎉 Your Resume Generator is now live!"
echo "💡 Next steps:"
echo "   1. Register a custom domain"
echo "   2. Set up payment processing with Stripe"
echo "   3. Add user authentication"
echo "   4. Start marketing your service!"
