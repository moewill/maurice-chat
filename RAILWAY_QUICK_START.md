# Railway Quick Start - Maurice Voice Chatbot

## ⚡ 5-Minute Deployment

### 1. Get API Keys
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com) → API Keys
- **Deepgram**: [console.deepgram.com](https://console.deepgram.com) → API Keys

### 2. Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. **"Login"** → **"Continue with GitHub"**
3. **"New Project"** → **"Deploy from GitHub repo"**
4. Select **"moewill/maurice-chat"**
5. **"Deploy Now"**

### 3. Add Environment Variables
In Railway dashboard → **"Variables"** tab:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here
WEBSOCKET_HOST=0.0.0.0
```
**Note**: Railway automatically sets the `PORT` environment variable - don't set `WEBSOCKET_PORT`

### 4. Get Your URL
- **"Settings"** → **"Networking"** → **"Generate Domain"**
- Copy the URL: `https://your-app-name.up.railway.app`

### 5. Test Your Deployment
```bash
curl https://your-app-name.up.railway.app/health
```

### 6. Update Your Website
```javascript
// In your website's chatbot code
const config = {
  params: {
    baseUrl: 'https://your-app-name.up.railway.app',
    endpoints: { connect: '/connect' }
  }
};
```

## 🎯 That's It!
Your voice chatbot is now live with:
- ✅ **Secure API keys** (hidden on server)
- ✅ **Real-time voice chat** (<500ms latency)
- ✅ **Auto-scaling** (handles 50+ users)
- ✅ **Free SSL** (HTTPS enabled)
- ✅ **Auto-deployments** (updates on git push)

## 💰 Pricing
- **Free tier**: 500 hours/month
- **Pro tier**: $5/month + usage
- **Typical cost**: $10-20/month for voice chat

## 🔧 Common Commands

### Monitor Your App
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# View logs
railway logs --follow

# Check status
railway status
```

### Test Endpoints
```bash
# Health check
curl https://your-app.up.railway.app/health

# WebSocket test
curl -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     https://your-app.up.railway.app/ws
```

### Update Your App
```bash
# Any git push triggers auto-deployment
git add .
git commit -m "Update voice chatbot"
git push origin main
# Railway automatically deploys!
```

## 🚨 Troubleshooting

### Build Fails
- Check **"Deployments"** → **"View Logs"**
- Verify Dockerfile is in root directory
- Ensure all dependencies are in requirements.txt

### Environment Variables Missing
- Go to **"Variables"** tab
- Ensure all required variables are set
- Restart deployment after adding variables

### WebSocket Connection Issues
- Check if using `wss://` (not `ws://`) for HTTPS
- Verify CORS settings in your backend
- Test with curl command above

### Voice Chat Not Working
- Check browser console for errors
- Verify microphone permissions
- Test on different browsers (Chrome works best)

## 🎉 Success!
Your professional voice chatbot is now running on Railway! 

**Cost**: ~$5-15/month
**Performance**: Sub-second response times
**Scalability**: Handles 50+ concurrent users
**Reliability**: Auto-restart on failures

Perfect for your professional services website! 🎤