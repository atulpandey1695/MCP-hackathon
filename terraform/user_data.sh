#!/bin/bash

# Compact MCP Server Setup Script
# Downloads and executes the full setup script

set -e

echo "🚀 Starting MCP Server Setup - $(date)"

# Update system
yum update -y

# Install basic packages
yum install -y git curl wget docker

# Start Docker
systemctl start docker
systemctl enable docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /opt/mcp-server
cd /opt/mcp-server

# Download and execute the full setup script
echo "Downloading setup script..."
curl -o setup.sh https://raw.githubusercontent.com/atulpandey1695/MCP-hackathon/main/terraform/setup_script.sh
chmod +x setup.sh

# Execute the setup script
./setup.sh

echo "✅ MCP Server setup initiated" 
