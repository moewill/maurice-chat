# Railway Troubleshooting Guide

## 🚨 Common Railway Deployment Issues

### **Issue 1: Healthcheck Failed - Service Unavailable**

**Symptoms:**
```
Attempt #1 failed with service unavailable. Continuing to retry...
1/1 replicas never became healthy!
Healthcheck failed!
```

**Cause:** Server not listening on the correct port or not starting properly.

**Solution:**
1. **Check Railway Logs** - Go to Railway dashboard → "View Logs"
2. **Verify Environment Variables** - Make sure these are set:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   DEEPGRAM_API_KEY=your-deepgram-key-here
   WEBSOCKET_HOST=0.0.0.0
   ```
3. **Don't Set WEBSOCKET_PORT** - Railway provides `PORT` automatically
4. **Wait for Build** - Sometimes takes 3-5 minutes for first deployment

### **Issue 2: Build Succeeds but Server Won't Start**

**Symptoms:**
- Build completes successfully
- Healthcheck fails immediately
- No response from server

**Debug Steps:**
1. **Check Logs** in Railway dashboard
2. **Look for startup errors** in the logs
3. **Verify API keys** are correctly set
4. **Check for missing dependencies**

**Common Fixes:**
- Ensure API keys don't have extra spaces
- Verify API keys are valid (test them separately)
- Check if your account has API credits/limits

### **Issue 3: Port Configuration Problems**

**Symptoms:**
```
Server starting on 0.0.0.0:7860
But Railway expects different port
```

**Solution:**
The latest code automatically uses Railway's `PORT` environment variable. If you're still having issues:

1. **Update your code** - Pull latest changes from GitHub
2. **Redeploy** - Railway will use the updated code
3. **Check logs** for port binding messages

### **Issue 4: WebSocket Connection Issues**

**Symptoms:**
- HTTP endpoints work
- WebSocket connections fail
- CORS errors

**Solution:**
1. **Use WSS (not WS)** for secure connections:
   ```javascript
   const wsUrl = 'wss://your-app.up.railway.app/ws';
   ```
2. **Check CORS settings** in your frontend
3. **Verify domain** is correct in your code

### **Issue 5: Missing Environment Variables**

**Symptoms:**
```
ANTHROPIC_API_KEY environment variable is required
DEEPGRAM_API_KEY environment variable is required
```

**Solution:**
1. Go to Railway dashboard → **"Variables"** tab
2. Add required variables:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-actual-key
   DEEPGRAM_API_KEY=your-actual-key
   ```
3. **Restart deployment** after adding variables

## 🔧 Debugging Commands

### **Check Deployment Status:**
```bash
# Test health endpoint
curl https://your-app-name.up.railway.app/health

# Test WebSocket connection
curl -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     https://your-app-name.up.railway.app/ws
```

### **Check Logs:**
1. Railway dashboard → **"View Logs"**
2. Look for startup messages
3. Check for error messages
4. Verify port binding

### **Validate Environment:**
Look for these log messages:
```
🚀 FastAPI application starting up...
📝 Environment variables loaded:
   - PORT: 8080 (or whatever Railway assigns)
   - ANTHROPIC_API_KEY: Set
   - DEEPGRAM_API_KEY: Set
Starting voice agent server on 0.0.0.0:8080
```

## 🆘 Emergency Fixes

### **Quick Fix 1: Restart Deployment**
1. Go to Railway dashboard
2. Click **"Deployments"**
3. Click **"Redeploy"** on latest deployment

### **Quick Fix 2: Check Variables**
1. **"Variables"** tab
2. Verify all required variables are set
3. No extra spaces in API keys
4. API keys start with correct prefixes

### **Quick Fix 3: Fresh Deploy**
1. Make a small change to your code
2. Push to GitHub
3. Railway will auto-deploy
4. Check logs for new deployment

## 📞 Getting Help

**If still having issues:**
1. **Check Railway logs** first
2. **Verify API keys** work independently
3. **Test locally** with Docker if possible
4. **Check Railway status** page for platform issues

**Common working configuration:**
```
Environment Variables:
- ANTHROPIC_API_KEY=sk-ant-...
- DEEPGRAM_API_KEY=...
- WEBSOCKET_HOST=0.0.0.0
- LOG_LEVEL=INFO
- PYTHONUNBUFFERED=1

Railway automatically sets:
- PORT (don't override this)
```

**Expected startup logs:**
```
🚀 FastAPI application starting up...
📝 Environment variables loaded:
Starting voice agent server on 0.0.0.0:PORT
```

**Success indicators:**
- Health check passes
- `/health` endpoint returns 200
- WebSocket connections work
- Voice chat functions properly