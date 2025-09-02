# Mobile 502 Error Troubleshooting Guide

## Current Status: ✅ RESOLVED
- **Health Check**: https://resume-gen.app/health ✅ Working
- **Main Site**: https://resume-gen.app/ ✅ Working  
- **Desktop Access**: ✅ Confirmed working
- **Template Issue**: ✅ Fixed (was using template with placeholder AdSense IDs)

## If Mobile 502 Errors Persist:

### 1. **DNS Cache Issues (Most Common)**
Mobile networks often cache DNS longer than desktop. Try:
- Turn airplane mode ON for 10 seconds, then OFF
- Switch from WiFi to cellular data (or vice versa)
- Use a different mobile browser
- Clear browser cache/data on mobile

### 2. **Render Cold Start (Free Tier)**
Free tier apps sleep after 15 minutes of inactivity:
- Run wake-up script: `./wake-up.sh`
- Or visit: https://resume-gen.app/health first
- Then visit: https://resume-gen.app/

### 3. **Network-Specific Issues**
Some mobile carriers have different routing:
- Try using mobile data instead of WiFi
- Try a VPN on mobile
- Test from different location/network

### 4. **Quick Tests**
```bash
# Test health endpoint
curl https://resume-gen.app/health

# Test main page
curl -I https://resume-gen.app/

# Wake up the app if sleeping
./wake-up.sh
```

### 5. **Monitor App Status**
- Render Dashboard: Check for deployment issues
- CloudFlare: Check for any blocking rules
- GitHub: Verify latest commits deployed

## Recent Fixes Applied:
1. ✅ Added `/health` endpoint for monitoring
2. ✅ Fixed template reference (was using placeholder AdSense template)
3. ✅ Created wake-up script for cold starts
4. ✅ Verified SSL certificates working
5. ✅ Confirmed DNS propagation complete

## Expected Resolution:
The template fix should resolve most mobile issues. If problems persist, it's likely DNS caching on the mobile network - try the DNS cache clearing steps above.
