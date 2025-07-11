# Oracle Cloud Quick Reference - Maurice Voice Chatbot

## 🚀 Quick Start Commands

### Connect to Your Instance
```bash
ssh -i ~/.ssh/oracle_key ubuntu@YOUR_PUBLIC_IP
```

### Run Auto-Setup Script
```bash
curl -sSL https://raw.githubusercontent.com/moewill/maurice-chat/main/scripts/oracle-cloud-setup.sh | bash
```

## 📋 Essential Commands

### Chatbot Management
```bash
# Start chatbot
chatbot-start

# Stop chatbot
chatbot-stop

# View logs
chatbot-logs

# Check status
chatbot-status

# Restart chatbot
chatbot-restart
```

### Docker Commands
```bash
# Build and start
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart specific service
docker-compose restart backend
```

### System Monitoring
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep python

# Check network connections
sudo netstat -tlnp | grep 7860
```

## 🔧 Configuration Files

### Environment Variables
```bash
# Edit API keys
nano ~/maurice-chat/.env

# Required variables:
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=7860
```

### Firewall Rules
```bash
# Check firewall status
sudo ufw status

# Add new rule
sudo ufw allow PORT_NUMBER

# Remove rule
sudo ufw delete allow PORT_NUMBER
```

## 🧪 Testing Commands

### Test Backend Health
```bash
curl http://YOUR_PUBLIC_IP:7860/health
```

### Test WebSocket Connection
```bash
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: test" \
     http://YOUR_PUBLIC_IP:7860/ws
```

### Test from Website
```javascript
// In browser console
const ws = new WebSocket('ws://YOUR_PUBLIC_IP:7860/ws');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Message:', event.data);
```

## 🛠️ Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs backend

# Check if port is in use
sudo netstat -tlnp | grep 7860

# Restart Docker
sudo systemctl restart docker
```

### Permission Errors
```bash
# Fix Docker permissions
sudo usermod -aG docker ubuntu
# Then log out and back in
```

### Memory Issues
```bash
# Check memory usage
free -h

# Check Docker container memory
docker stats
```

### Network Issues
```bash
# Check if service is listening
sudo netstat -tlnp | grep 7860

# Test local connection
curl localhost:7860/health

# Check firewall
sudo ufw status
```

## 📊 Performance Monitoring

### Resource Usage
```bash
# Real-time system monitor
htop

# Docker container stats
docker stats

# Disk usage by directory
du -sh ~/maurice-chat/*
```

### Log Analysis
```bash
# View recent logs
docker-compose logs --tail=100 backend

# Follow logs in real-time
docker-compose logs -f backend

# Search logs for errors
docker-compose logs backend | grep -i error
```

## 🔄 Updates and Maintenance

### Update Code
```bash
cd ~/maurice-chat
git pull
docker-compose build
docker-compose up -d
```

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Backup Configuration
```bash
# Backup environment file
cp ~/maurice-chat/.env ~/maurice-chat/.env.backup

# Backup entire directory
tar -czf maurice-chat-backup.tar.gz maurice-chat/
```

## 🌐 Domain Setup (Optional)

### Install Nginx
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

### Configure Domain
```bash
# Edit Nginx config
sudo nano /etc/nginx/sites-available/maurice-chat

# Enable site
sudo ln -s /etc/nginx/sites-available/maurice-chat /etc/nginx/sites-enabled/

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

## 📱 Mobile Testing

### Test on Mobile Device
1. Connect to same WiFi network
2. Open browser and go to: `http://YOUR_PUBLIC_IP:7860`
3. Test voice chat functionality

### HTTPS for Mobile (Required for voice)
- Mobile browsers require HTTPS for microphone access
- Set up domain and SSL certificate
- Or use ngrok for testing: `ngrok http 7860`

## 🆘 Emergency Commands

### Stop Everything
```bash
docker-compose down
sudo systemctl stop maurice-chat
```

### Reset Everything
```bash
cd ~/maurice-chat
docker-compose down
docker system prune -a
git reset --hard HEAD
git pull
docker-compose build
docker-compose up -d
```

### Check Service Status
```bash
sudo systemctl status maurice-chat
sudo systemctl status docker
```

## 📞 Support Resources

- **Oracle Cloud Docs**: https://docs.oracle.com/en-us/iaas/
- **Docker Docs**: https://docs.docker.com/
- **Anthropic API**: https://docs.anthropic.com/
- **Deepgram API**: https://developers.deepgram.com/

## 🎯 Performance Targets

### Expected Performance (24GB RAM instance)
- **Concurrent Users**: 50+
- **Response Time**: <300ms
- **Memory Usage**: ~1-2GB
- **CPU Usage**: <20%

### Scaling Indicators
- **Memory > 20GB**: Consider optimizing
- **CPU > 80%**: Consider vertical scaling
- **Response time > 1s**: Investigate bottlenecks