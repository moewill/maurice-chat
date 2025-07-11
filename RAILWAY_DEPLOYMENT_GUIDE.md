# Railway Deployment Guide - Maurice Voice Chatbot

## 🚀 5-Minute Deployment to Railway

Railway is the easiest way to deploy your voice chatbot. No server management, automatic deployments, and generous free tier.

---

## Part 1: Prerequisites

### What You Need:
- GitHub account with maurice-chat repository
- Railway account (free)
- Anthropic API key
- Deepgram API key

### API Keys Setup:
1. **Anthropic API Key**: 
   - Go to [console.anthropic.com](https://console.anthropic.com)
   - Create account → Get API key
   - Starts with `sk-ant-`

2. **Deepgram API Key**:
   - Go to [console.deepgram.com](https://console.deepgram.com)
   - Create account → Get API key
   - Free tier: 45,000 minutes/month

---

## Part 2: Railway Configuration

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Click **"Login"** 
3. **"Continue with GitHub"**
4. Authorize Railway to access your repositories

### Step 2: Create New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **"moewill/maurice-chat"** repository
4. Click **"Deploy Now"**

### Step 3: Configure Environment Variables
1. In your Railway project, click **"Variables"** tab
2. Add these environment variables:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=7860
LOG_LEVEL=INFO
```

### Step 4: Configure Networking
1. Click **"Settings"** tab
2. Scroll to **"Networking"**
3. Click **"Generate Domain"**
4. Copy the generated URL (e.g., `maurice-chat-production.up.railway.app`)

---

## Part 3: Deploy Your Voice Chatbot

### Step 5: Automatic Deployment
Railway automatically detects your `Dockerfile` and deploys:

1. **Building**: Railway builds your Docker container
2. **Deploying**: Container starts running
3. **Ready**: Your chatbot is live!

### Step 6: Monitor Deployment
1. Click **"Deployments"** tab
2. Watch the build logs
3. Wait for **"Success"** status (usually 2-3 minutes)

### Step 7: Test Your Deployment
```bash
# Test health endpoint
curl https://your-app-name.up.railway.app/health

# Should return:
# {"status":"healthy","service":"maurice-chat-backend"}
```

---

## Part 4: Configure Your Website

### Step 8: Update Website Configuration
Update your website's chatbot to use Railway:

```javascript
// In your website's voice chatbot code
const config = {
  params: {
    baseUrl: 'https://your-app-name.up.railway.app',
    endpoints: {
      connect: '/connect'
    }
  },
  // ... rest of config
};
```

### Step 9: Update CORS (if needed)
If you get CORS errors, update your backend configuration:

```python
# In backend/server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://moewill.github.io", "https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Part 5: Testing & Validation

### Step 10: Test Voice Chat
1. Go to your website
2. Open the chatbot
3. Click the voice button
4. Test speaking: "Hello, how are you?"
5. Verify you get a voice response

### Step 11: Test Different Browsers
- ✅ **Chrome**: Full support
- ✅ **Safari**: Full support  
- ✅ **Edge**: Full support
- ⚠️ **Firefox**: Limited Web Speech API support

### Step 12: Test on Mobile
- Open your website on mobile
- Test voice functionality
- Note: Requires HTTPS for microphone access

---

## Part 6: Monitoring & Maintenance

### Step 13: Monitor Usage
1. **Railway Dashboard**: Check deployment status
2. **Logs**: Click "View Logs" to see real-time activity
3. **Metrics**: Monitor CPU, memory, and network usage

### Step 14: View Logs
```bash
# In Railway dashboard, click "View Logs"
# Or use Railway CLI:
railway logs --follow
```

### Step 15: Set Up Alerts (Optional)
1. Go to **"Settings"** → **"Notifications"**
2. Add webhook URL for deployment alerts
3. Get notified of failures or issues

---

## Part 7: Custom Domain (Optional)

### Step 16: Add Custom Domain
1. **Settings** → **"Domains"**
2. Click **"Add Domain"**
3. Enter your domain: `chat.yourdomain.com`
4. Add CNAME record in your DNS:
   ```
   chat.yourdomain.com → your-app-name.up.railway.app
   ```

### Step 17: SSL Certificate
Railway automatically provides SSL certificates for custom domains:
- ✅ **Free SSL**: Automatically generated
- ✅ **Auto-renewal**: No maintenance required
- ✅ **HTTPS**: Secure voice chat

---

## Part 8: Scaling & Optimization

### Step 18: Monitor Performance
**Railway provides:**
- CPU usage graphs
- Memory usage tracking
- Network traffic monitoring
- Response time metrics

### Step 19: Scale Resources
**Railway automatically scales:**
- CPU: Up to 8 vCPU
- Memory: Up to 32GB RAM
- Network: Unlimited bandwidth

**Costs scale with usage:**
- **Free tier**: $0/month (500 hours)
- **Pro plan**: $5/month base + usage
- **Typical voice chat**: $10-20/month

---

## Part 9: Advanced Configuration

### Step 20: Production Optimizations
Add these to your environment variables:

```
# Production settings
PYTHONUNBUFFERED=1
WEB_CONCURRENCY=2
LOG_LEVEL=WARNING
MAX_CONNECTIONS=50
```

### Step 21: Health Check Configuration
Railway automatically monitors your `/health` endpoint:
- **Healthy**: Returns 200 status
- **Unhealthy**: Automatically restarts
- **Downtime**: Minimal with auto-restart

---

## Part 10: Troubleshooting

### Common Issues:

**1. Build Fails:**
```bash
# Check build logs in Railway dashboard
# Common fix: Ensure Dockerfile is in root directory
```

**2. Environment Variables:**
```bash
# Verify all required variables are set:
ANTHROPIC_API_KEY=sk-ant-...
DEEPGRAM_API_KEY=...
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=7860
```

**3. CORS Errors:**
```python
# Add your website domain to CORS origins
allow_origins=["https://moewill.github.io"]
```

**4. WebSocket Connection Fails:**
```javascript
// Use wss:// for HTTPS websites
const wsUrl = 'wss://your-app.up.railway.app/ws';
```

**5. Voice Not Working:**
- Check browser console for errors
- Verify HTTPS is enabled
- Test microphone permissions

---

## Part 11: Cost Management

### Step 22: Monitor Costs
1. **Railway Dashboard** → **"Usage"**
2. Track monthly usage
3. Set up billing alerts

### Step 23: Cost Optimization
**Free tier limits:**
- 500 execution hours/month
- $5 credit included
- Perfect for moderate usage

**Typical costs:**
- **Light usage**: $0-5/month
- **Moderate usage**: $5-15/month
- **Heavy usage**: $15-30/month

---

## Part 12: Backup & Recovery

### Step 24: Environment Backup
Save your environment variables:
```bash
# Create backup file
echo "ANTHROPIC_API_KEY=your-key" > .env.backup
echo "DEEPGRAM_API_KEY=your-key" >> .env.backup
```

### Step 25: Disaster Recovery
If something goes wrong:
1. **Rollback**: Railway keeps deployment history
2. **Redeploy**: Push to GitHub triggers new deployment
3. **Fresh start**: Delete and recreate project

---

## Part 13: Performance Monitoring

### Step 26: Set Up Monitoring
Railway provides built-in monitoring:
- **Response times**: Average response latency
- **Error rates**: Failed request percentage
- **Resource usage**: CPU, memory, network

### Step 27: Performance Targets
**Expected performance:**
- **Response time**: <500ms
- **Concurrent users**: 20-50
- **Memory usage**: 1-2GB
- **CPU usage**: <50%

---

## Part 14: Security Best Practices

### Step 28: Secure Your Deployment
1. **API Keys**: Never commit to GitHub
2. **CORS**: Restrict to your domains only
3. **Rate limiting**: Implement usage limits
4. **HTTPS**: Always use SSL connections

### Step 29: Regular Updates
```bash
# Update dependencies regularly
git pull origin main
# Railway auto-deploys on push
```

---

## Summary

### ✅ What You Get:
- **5-minute deployment** from GitHub
- **Automatic builds** on every push
- **Free SSL certificates** for custom domains
- **Monitoring and logs** built-in
- **Auto-scaling** based on usage
- **$5/month** for production usage

### 🎯 Your Voice Chatbot is Now:
- **Secure**: API keys hidden on server
- **Fast**: Sub-second response times
- **Scalable**: Handles 50+ concurrent users
- **Professional**: HTTPS with custom domain
- **Reliable**: Auto-restart on failures

### 🚀 Next Steps:
1. Test your deployment thoroughly
2. Update your website configuration
3. Monitor usage and performance
4. Add custom domain if desired
5. Share your voice chatbot with the world!

**Your voice chatbot is live at**: `https://your-app-name.up.railway.app`

---

## Quick Commands Reference

```bash
# Test deployment
curl https://your-app-name.up.railway.app/health

# Test WebSocket
curl -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     https://your-app-name.up.railway.app/ws

# Monitor logs (with Railway CLI)
railway logs --follow

# Deploy updates
git push origin main
# Railway auto-deploys!
```

That's it! Your voice chatbot is now running on Railway with enterprise-grade infrastructure for just $5/month! 🎉