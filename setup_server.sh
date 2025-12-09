#!/bin/bash
# Server Setup Script for Ubuntu 24.04 (AWS EC2)

echo "--- Starting Server Setup ---"

# 1. Update System
echo "[1/5] Updating System..."
sudo apt update && sudo apt upgrade -y

# 2. Install Python & build tools
echo "[2/5] Installing Python..."
sudo apt install python3-pip python3-venv build-essential -y

# 3. Install Node.js (v20)
echo "[3/5] Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 4. Install PM2
echo "[4/5] Installing PM2..."
sudo npm install -g pm2

echo "--- Setup Complete! ---"
echo "Next steps:"
echo "1. Upload your code"
echo "2. Run 'npm install' in dashboard/"
echo "3. Run 'pip install -r requirements.txt'"
echo "4. Start with 'pm2 start ecosystem.config.js'"
