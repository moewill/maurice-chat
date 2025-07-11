# Oracle Cloud Deployment Guide - Maurice Voice Chatbot

## Overview
Deploy your voice chatbot to Oracle Cloud's Always Free tier with 24GB RAM - perfect for production workloads at zero cost.

## Prerequisites
- GitHub account with maurice-chat repository
- Valid email address
- Credit card (for verification - won't be charged)
- Basic command line knowledge

---

## Part 1: Oracle Cloud Account Setup

### Step 1: Create Oracle Cloud Account
1. Go to [oracle.com/cloud/free](https://oracle.com/cloud/free)
2. Click **"Start for free"**
3. Fill out the registration form:
   - **Country/Territory**: Your location
   - **Name**: Your full name
   - **Email**: Valid email address
   - **Phone**: Your phone number
4. Click **"Verify my email"**
5. Check your email and click the verification link

### Step 2: Complete Account Verification
1. **Address Information**: Fill out your address
2. **Payment Method**: Add credit card (for verification only)
   - Oracle won't charge for Always Free resources
   - You'll get $300 credit for 30 days
3. **Verify Phone**: Enter SMS code
4. **Review and Complete**: Accept terms and create account

### Step 3: Initial Setup
1. **Choose Home Region**: Select closest region to your users
   - US East (Ashburn) - Good for North America
   - UK South (London) - Good for Europe
   - Asia Pacific (Mumbai) - Good for Asia
2. **Skip the guided tour** (we'll do manual setup)

---

## Part 2: Create VM Instance

### Step 4: Launch Compute Instance
1. In Oracle Cloud Console, click **"Create a VM instance"**
2. **Basic Information**:
   - **Name**: `maurice-voice-chatbot`
   - **Compartment**: Leave as default (root)

### Step 5: Configure Instance
1. **Placement**:
   - **Availability Domain**: Leave default
   - **Fault Domain**: Leave default

2. **Image and Shape**:
   - **Image**: Click **"Change Image"**
     - Select **"Canonical Ubuntu"** (22.04)
     - Click **"Select Image"**
   
   - **Shape**: Click **"Change Shape"**
     - **Instance Type**: Select **"Ampere"** (ARM-based)
     - **Shape**: Select **"VM.Standard.A1.Flex"**
     - **OCPU Count**: 4 (maximum for free tier)
     - **Memory (GB)**: 24 (maximum for free tier)
     - Click **"Select Shape"**

3. **Networking**:
   - **Primary Network**: Leave default (creates new VCN)
   - **Subnet**: Leave default (creates new subnet)
   - **Public IP**: Select **"Assign a public IPv4 address"**

4. **SSH Keys**:
   - **Generate SSH Key Pair**: Click this option
   - **Save Private Key**: Download and save the private key file
   - **Save Public Key**: Download and save the public key file
   - ⚠️ **Important**: Keep these files safe - you'll need them to access your server

### Step 6: Create Instance
1. Click **"Create"** button
2. Wait 2-3 minutes for instance to provision
3. Status will change to **"Running"** when ready
4. **Copy the Public IP Address** - you'll need this

---

## Part 3: Configure Network Security

### Step 7: Open Required Ports
1. Click on your instance name to open details
2. Click **"Subnet"** link (under Primary VNIC)
3. Click **"Default Security List"**
4. Click **"Add Ingress Rules"**

**Add these rules one by one:**

**Rule 1 - HTTP:**
- **Source CIDR**: `0.0.0.0/0`
- **IP Protocol**: `TCP`
- **Destination Port Range**: `80`
- **Description**: `HTTP for web access`
- Click **"Add Ingress Rules"**

**Rule 2 - HTTPS:**
- **Source CIDR**: `0.0.0.0/0`
- **IP Protocol**: `TCP`
- **Destination Port Range**: `443`
- **Description**: `HTTPS for secure web access`
- Click **"Add Ingress Rules"**

**Rule 3 - Voice Chat Backend:**
- **Source CIDR**: `0.0.0.0/0`
- **IP Protocol**: `TCP`
- **Destination Port Range**: `7860`
- **Description**: `Voice chat backend`
- Click **"Add Ingress Rules"**

---

## Part 4: Connect to Your Instance

### Step 8: SSH Connection
1. **Move your private key to a secure location**:
   ```bash
   # On Mac/Linux
   mv ~/Downloads/ssh-key-*.key ~/.ssh/oracle_key
   chmod 600 ~/.ssh/oracle_key
   
   # On Windows (use Git Bash or WSL)
   mv /c/Users/YourName/Downloads/ssh-key-*.key ~/.ssh/oracle_key
   chmod 600 ~/.ssh/oracle_key
   ```

2. **Connect to your instance**:
   ```bash
   # Replace YOUR_PUBLIC_IP with the actual IP address
   ssh -i ~/.ssh/oracle_key ubuntu@YOUR_PUBLIC_IP
   ```

3. **If successful, you should see**:
   ```
   Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.0-1044-oracle aarch64)
   ubuntu@maurice-voice-chatbot:~$ 
   ```

### Step 9: Update System
```bash
# Update package list
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential tools
sudo apt install -y curl wget git htop nano
```

---

## Part 5: Install Docker

### Step 10: Install Docker
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Log out and back in to apply group changes
exit
```

### Step 11: Reconnect and Test Docker
```bash
# Reconnect to your instance
ssh -i ~/.ssh/oracle_key ubuntu@YOUR_PUBLIC_IP

# Test Docker installation
docker --version
docker run hello-world
```

---

## Part 6: Deploy Your Voice Chatbot

### Step 12: Clone Your Repository
```bash
# Clone your maurice-chat repository
git clone https://github.com/moewill/maurice-chat.git
cd maurice-chat
```

### Step 13: Set Up Environment Variables
```bash
# Create environment file
nano .env

# Add these variables (replace with your actual API keys):
ANTHROPIC_API_KEY=sk-ant-your-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here
WEBSOCKET_HOST=0.0.0.0
WEBSOCKET_PORT=7860

# Save and exit (Ctrl+X, Y, Enter)
```

### Step 14: Configure Firewall
```bash
# Configure Ubuntu firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 7860
```

### Step 15: Build and Run with Docker
```bash
# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d

# Check if it's running
docker-compose ps
docker-compose logs -f
```

---

## Part 7: Test Your Deployment

### Step 16: Test Backend Connection
```bash
# Test health endpoint
curl http://YOUR_PUBLIC_IP:7860/health

# Should return:
# {"status":"healthy","service":"maurice-chat-backend"}
```

### Step 17: Test WebSocket Connection
```bash
# Test WebSocket connection (optional)
curl -H "Host: YOUR_PUBLIC_IP:7860" \
     -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: test" \
     http://YOUR_PUBLIC_IP:7860/ws
```

---

## Part 8: Update Your Website

### Step 18: Update Website Configuration
Update your website's voice chatbot to use your new Oracle Cloud backend:

```javascript
// In your website's voice chatbot code
const config = {
  params: {
    baseUrl: 'http://YOUR_PUBLIC_IP:7860',  // Replace with your Oracle Cloud IP
    endpoints: {
      connect: '/connect'
    }
  },
  // ... rest of your config
};
```

---

## Part 9: Domain and SSL (Optional)

### Step 19: Set Up Domain (Optional)
If you want to use a custom domain:

1. **Point your domain to the Oracle Cloud IP**:
   - Create an A record: `chat.yourdomain.com` → `YOUR_PUBLIC_IP`

2. **Install Nginx and Certbot**:
   ```bash
   sudo apt install -y nginx certbot python3-certbot-nginx
   
   # Configure Nginx
   sudo nano /etc/nginx/sites-available/maurice-chat
   ```

3. **Nginx Configuration**:
   ```nginx
   server {
       listen 80;
       server_name chat.yourdomain.com;
       
       location / {
           proxy_pass http://localhost:7860;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

4. **Enable site and get SSL**:
   ```bash
   sudo ln -s /etc/nginx/sites-available/maurice-chat /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   
   # Get SSL certificate
   sudo certbot --nginx -d chat.yourdomain.com
   ```

---

## Part 10: Monitoring and Maintenance

### Step 20: Set Up Monitoring
```bash
# Check system resources
htop

# Check Docker logs
docker-compose logs -f

# Check disk usage
df -h

# Monitor service
sudo systemctl status docker
```

### Step 21: Set Up Auto-Restart
```bash
# Create systemd service for auto-restart
sudo nano /etc/systemd/system/maurice-chat.service
```

Add this content:
```ini
[Unit]
Description=Maurice Chat Voice Bot
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ubuntu/maurice-chat
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Enable the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable maurice-chat
sudo systemctl start maurice-chat
```

---

## Troubleshooting

### Common Issues:

**1. Can't connect to instance:**
- Check security group rules
- Verify public IP is correct
- Ensure SSH key permissions are 600

**2. Docker permission denied:**
- Make sure you logged out and back in after adding user to docker group
- Or use `sudo docker` commands

**3. Service won't start:**
- Check logs: `docker-compose logs`
- Verify environment variables are set
- Check if ports are available: `sudo netstat -tlnp | grep 7860`

**4. WebSocket connection fails:**
- Verify firewall rules
- Check if service is running on correct port
- Test with curl commands above

**5. ARM compatibility issues:**
- Some Docker images might not support ARM architecture
- Use multi-arch images or rebuild for ARM64

---

## Cost Monitoring

### Always Free Resources Used:
- ✅ **VM.Standard.A1.Flex**: 4 OCPU, 24GB RAM (Always Free)
- ✅ **Block Storage**: 200GB (Always Free)
- ✅ **Network**: 10TB outbound/month (Always Free)

### To Monitor Usage:
1. Go to Oracle Cloud Console
2. **Governance & Administration** → **Account Management** → **Usage**
3. Monitor your Always Free usage to stay within limits

---

## Security Best Practices

### Secure Your Instance:
1. **Change default SSH port** (optional but recommended)
2. **Set up fail2ban** for SSH protection
3. **Regular security updates**: `sudo apt update && sudo apt upgrade`
4. **Monitor logs**: `sudo tail -f /var/log/auth.log`
5. **Use strong passwords** for any additional services

### Backup Strategy:
1. **Create boot volume backups** in Oracle Cloud Console
2. **Backup your environment files** and configurations
3. **Document your setup** for disaster recovery

---

## Conclusion

Your voice chatbot is now deployed on Oracle Cloud with:
- ✅ **24GB RAM** - handles 50+ concurrent users
- ✅ **Always Free** - no ongoing costs
- ✅ **Production-ready** - enterprise-grade infrastructure
- ✅ **Scalable** - easy to upgrade if needed

**Your voice chatbot is accessible at**: `http://YOUR_PUBLIC_IP:7860`

**Next Steps**:
1. Test the voice chat functionality
2. Update your website to use the new backend
3. Set up monitoring and alerts
4. Consider adding a custom domain and SSL

**Need help?** Check the troubleshooting section or refer to Oracle Cloud documentation.