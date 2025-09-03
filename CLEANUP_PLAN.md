# 🧹 Repository Cleanup Plan

## Files to Keep (Essential)
✅ **Core Application:**
- app.py (main application)
- requirements.txt
- runtime.txt 
- Procfile
- render.yaml
- .env (keep but not in git)
- .env.example
- .gitignore

✅ **Application Assets:**
- static/ (CSS, JS, fonts)
- templates/ (HTML templates)
- DejaVuSans.ttf (font file)
- ads.txt

✅ **Important Documentation:**
- README.md
- RESTORATION_COMPLETE.md (our success summary)

✅ **Useful Scripts:**
- start_server.sh (server startup)
- check_status.sh (status checker)

✅ **Data Directories:**
- previews/ (generated PDFs)
- uploads/ (uploaded files)
- venv/ (virtual environment)

## Files to Remove (Development Clutter)
❌ **Duplicate Apps:**
- app_clean.py
- app_with_ads.py

❌ **Test Files:**
- test_*.py (all test files)
- test_*.pdf 
- test_*.txt
- test_*.html
- debug_*.py

❌ **Development Documentation:**
- AD_MONETIZATION_GUIDE.md
- BAD_GATEWAY_FIX.md
- DEBUG_STATUS.md
- DEPLOYMENT_*.md
- DOMAIN_HOSTING_GUIDE.md
- GET_DOMAIN_LIVE.md
- INSTANT_DEPLOYMENT.md
- JAVASCRIPT_FIX_SUMMARY.md
- MOBILE_*.md
- PROJECT_STATUS*.md
- QUICK_*.md
- SUCCESS_VIEW_IMPLEMENTATION.md

❌ **Temporary/Log Files:**
- server.log
- .DS_Store

❌ **Unused Scripts:**
- check-ads.sh
- deploy_heroku.sh
- start.sh
- stop.sh
- wake-up.sh

❌ **Archive:**
- archive/ (old files)

## Result: Clean, Professional Repository
After cleanup, we'll have a clean repository with only essential files for the working application.
