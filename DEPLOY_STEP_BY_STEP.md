# 🚀 **STEP-BY-STEP: Deploy resume-gen.app on Render**

## **METHOD 1: Manual Setup (Recommended for Control)**

### **Step 1: Render.com Setup**
1. Go to **[render.com](https://render.com)**
2. Click **"Get Started for Free"**
3. **Sign up with GitHub** (easier repository access)

### **Step 2: Create Web Service**
1. In Render dashboard, click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"**

### **Step 3: Connect GitHub Repository**
1. If not connected, click **"Connect GitHub"**
2. Authorize Render to access your repositories
3. Search for: **`resume-gen-app`**
4. Click **"Connect"** next to `EM4th/resume-gen-app`

### **Step 4: Configure Service Settings**

**Basic Info:**
```
Name: resume-gen-app
Region: Oregon (US West) - or closest to your users
Branch: main
Runtime: Python 3
```

**Build & Deploy:**
```
Root Directory: (leave blank)
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

**Advanced Settings:**
```
Auto-Deploy: Yes
Health Check Path: /health
```

### **Step 5: Environment Variables**
In the **"Environment"** section, click **"Add Environment Variable"**:

```
Name: GOOGLE_API_KEY
Value: your_google_api_key_here
```

Click **"Add Environment Variable"** again:
```
Name: FLASK_ENV  
Value: production
```

### **Step 6: Deploy**
1. Click **"Create Web Service"**
2. Wait for build (2-5 minutes)
3. You'll get a URL like: `https://resume-gen-app.onrender.com`
4. Test it works before adding custom domain

### **Step 7: Add Custom Domain**
1. In your service dashboard, go to **"Settings"**
2. Scroll to **"Custom Domains"**
3. Click **"Add Custom Domain"**
4. Enter: `resume-gen.app`
5. Click **"Save"**

### **Step 8: Configure DNS**
At your domain registrar (where you bought resume-gen.app):

```
Record Type: CNAME
Name: @ (or resume-gen.app)
Value: resume-gen-app.onrender.com
TTL: 300 seconds
```

**Save the DNS record and wait 5-30 minutes for propagation.**

### **Step 9: Verify SSL**
1. Render automatically provisions SSL certificates
2. Wait 5-10 minutes after DNS propagation
3. Visit `https://resume-gen.app` (should be secure)

---

## **METHOD 2: One-Click Deploy**

### **Option A: Deploy Button (If Available)**
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/EM4th/resume-gen-app)

### **Option B: render.yaml Auto-Deploy**
1. The repository already contains `render.yaml`
2. Go to Render.com
3. Click "New +" → "Web Service"
4. Connect the repo
5. Render will auto-detect the YAML config
6. Just add the `GOOGLE_API_KEY` environment variable
7. Add custom domain in settings

---

## **VERIFICATION CHECKLIST**

After deployment, test these URLs:

### ✅ **Basic Functionality**
```bash
# Health check
curl https://resume-gen.app/health

# Should return JSON with status: "healthy"
```

### ✅ **AdSense Verification**
```bash
# ads.txt file
curl https://resume-gen.app/ads.txt

# Should return: google.com, pub-7524647518323966, DIRECT, f08c47fec0942fa0
```

### ✅ **Main Application**
- Visit: `https://resume-gen.app`
- Upload a test PDF resume
- Enter a job description
- Generate and download enhanced resume

### ✅ **SSL Certificate**
- URL should show `https://` with lock icon
- No security warnings

---

## **TROUBLESHOOTING**

### **Build Fails:**
- Check build logs in Render dashboard
- Ensure `requirements.txt` is present
- Verify Python version compatibility

### **App Won't Start:**
- Check if `GOOGLE_API_KEY` is set correctly
- Verify `gunicorn` is in requirements.txt
- Check application logs

### **Domain Not Working:**
- Verify DNS settings at registrar
- Wait for DNS propagation (up to 48 hours)
- Check CNAME record points to correct Render URL

### **SSL Issues:**
- Wait 10-15 minutes after DNS propagation
- Contact Render support if SSL doesn't auto-provision

---

## **FINAL RESULT**

Once complete, you'll have:
- ✅ **https://resume-gen.app** - Fully functional
- ✅ **Professional AI resume enhancement**
- ✅ **Google AdSense monetization ready**
- ✅ **SSL secured and production ready**
- ✅ **Auto-scaling and reliable hosting**

**Your resume generator will be live and earning revenue! 🚀💰**
