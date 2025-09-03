# Production Configuration for resume-gen.app

## Domain Configuration
DOMAIN=resume-gen.app
PRODUCTION_URL=https://resume-gen.app

## Environment Variables for Production
export GOOGLE_API_KEY="your_google_api_key_here"
export FLASK_ENV=production
export PORT=5000

## Deployment Commands

# For Render.com deployment:
# 1. Connect GitHub repo
# 2. Set environment variables in Render dashboard
# 3. Deploy with build command: pip install -r requirements.txt
# 4. Start command: gunicorn app:app

# For Heroku deployment:
# heroku create resume-gen-app
# heroku config:set GOOGLE_API_KEY=your_key_here
# git push heroku main

## Production Checklist
- [x] Google AdSense configured (pub-7524647518323966)
- [x] ads.txt properly set up
- [x] SSL/HTTPS ready
- [x] Error handling implemented
- [x] Production WSGI server (gunicorn)
- [x] Environment variables configured
- [x] SEO meta tags added
- [x] Professional UI/UX
- [x] Mobile responsive design

## Domain Setup
1. Point resume-gen.app to deployment platform
2. Configure SSL certificate
3. Update DNS records
4. Test all functionality

## Monitoring
- Health check endpoint: /health
- Analytics endpoint: /analytics
- Error logging to production logs
