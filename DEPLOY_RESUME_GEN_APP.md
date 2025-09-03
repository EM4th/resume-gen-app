# 🚀 Deployment Guide for resume-gen.app

## 🌐 Domain: resume-gen.app

### Quick Deploy Options

#### Option 1: Render.com (Recommended)
1. **Connect Repository**
   ```
   - Go to render.com
   - Connect GitHub repo: EM4th/resume-gen-app
   - Service: Web Service
   ```

2. **Configuration**
   ```
   Name: resume-gen-app
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

3. **Environment Variables**
   ```
   GOOGLE_API_KEY="your_google_api_key_here"
   FLASK_ENV=production
   ```

4. **Custom Domain**
   ```
   - Add custom domain: resume-gen.app
   - Configure DNS to point to Render
   - SSL automatically provisioned
   ```

#### Option 2: Heroku
```bash
# Install Heroku CLI first
heroku create resume-gen-app
heroku config:set GOOGLE_API_KEY="your_google_api_key_here"
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Add custom domain
heroku domains:add resume-gen.app
```

#### Option 3: Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Add domain
vercel --prod
```

### DNS Configuration
Point your domain to the deployment platform:

**For Render:**
```
Type: CNAME
Name: resume-gen.app
Value: your-app.onrender.com
```

**For Heroku:**
```
Type: CNAME  
Name: resume-gen.app
Value: your-app.herokuapp.com
```

### Post-Deployment Checklist

#### ✅ Test Core Functionality
- [ ] Upload resume (PDF)
- [ ] Generate with job description text
- [ ] Generate with job URL
- [ ] Download enhanced resume
- [ ] Check PDF formatting quality

#### ✅ Verify Monetization
- [ ] Google AdSense ads loading
- [ ] ads.txt accessible at resume-gen.app/ads.txt
- [ ] Ad placements working correctly

#### ✅ Performance & SEO
- [ ] SSL certificate active (https://)
- [ ] Page load speed < 3 seconds
- [ ] Mobile responsive design
- [ ] Meta tags for social sharing
- [ ] Google Analytics (optional)

#### ✅ Monitoring
- [ ] Health check: resume-gen.app/health
- [ ] Error logging working
- [ ] Analytics tracking: resume-gen.app/analytics

### Production Environment Variables

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
FLASK_ENV=production
PORT=5000
```

### Domain Verification for AdSense

1. **Verify ads.txt**
   ```
   curl https://resume-gen.app/ads.txt
   # Should return: google.com, pub-7524647518323966, DIRECT, f08c47fec0942fa0
   ```

2. **Add site to AdSense**
   - Add resume-gen.app to your AdSense account
   - Verify domain ownership
   - Enable auto ads

### Maintenance Commands

```bash
# Check application health
curl https://resume-gen.app/health

# View basic analytics
curl https://resume-gen.app/analytics

# Test resume generation
curl -X POST https://resume-gen.app/generate_resume \
  -F "job_description=Test job description" \
  -F "resume_file=@test.pdf" \
  -F "format=pdf"
```

### Scaling Considerations

For high traffic:
- Enable CDN (Cloudflare)
- Add Redis for caching
- Implement rate limiting
- Add database for user analytics
- Consider multiple server instances

---

## 🎉 READY FOR LAUNCH!

Your resume generator is now ready for deployment at **resume-gen.app** with:
- ✅ Professional AI-powered resume enhancement
- ✅ URL job posting analysis
- ✅ Perfect PDF formatting
- ✅ Google AdSense monetization
- ✅ Mobile-responsive design
- ✅ Production-ready configuration

Deploy to resume-gen.app and start generating revenue! 🚀
