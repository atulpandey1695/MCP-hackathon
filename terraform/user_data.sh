#!/bin/bash

# MCP Server Deployment Script - UPDATED for two containers
# MCP Server + Streamlit App

set -e  # Exit on any error

echo "🚀 Starting MCP Server deployment..."

# Update system
echo "📦 Updating system packages..."
yum update -y

# Install required packages
echo "📦 Installing required packages..."
yum install -y docker git curl wget

# Start and enable Docker
echo "🐳 Setting up Docker..."
systemctl start docker
systemctl enable docker

# Install Docker Compose
echo "📦 Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/mcp-server
cd /opt/mcp-server

# Clone the repository
echo "�� Cloning MCP server repository..."
git clone https://github.com/atulpandey1695/MCP-hackathon.git .

# Navigate to the correct directory
cd MCP-hackathon

# Create Dockerfile
echo "🐳 Creating Dockerfile..."
cat > mcp_server/Dockerfile << 'EOF'
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY mcp_server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "mcp_server/server.py"]
EOF

# Create requirements.txt with all dependencies
echo "📦 Creating requirements.txt..."
cat > mcp_server/requirements.txt << 'EOF'
fastapi>=0.104.1
uvicorn>=0.24.0
websockets>=12.0
pydantic>=2.5.0
asyncio-mqtt>=0.16.1
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
redis>=5.0.0
psycopg2-binary>=2.9.9
sqlalchemy>=2.0.23
alembic>=1.13.0
python-multipart>=0.0.6
stripe>=7.0.0
boto3>=1.34.0
docker>=6.1.3
python-dotenv>=1.0.0
httpx>=0.25.0
aiofiles>=23.2.1
click>=8.1.7
typer>=0.9.0
flask==2.3.3
streamlit>=1.35.0
langchain>=0.1.47
langchain-openai>=0.1.0
langchain-community>=0.0.20
openai>=1.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
gitpython>=3.1.0
mistralai>=0.1.0
faiss-cpu>=1.7.4
EOF

# Create docker-compose.yml for two containers
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
services:
  # MCP Server
  mcp-server:
    build:
      context: .
      dockerfile: mcp_server/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-production-secret-key-here
    volumes:
      - ./mcp_server/logs:/app/logs
      - ./mcp_server/data:/app/data
    restart: unless-stopped

  # Streamlit App
  streamlit:
    build:
      context: .
      dockerfile: mcp_server/Dockerfile
    ports:
      - "8501:8501"
    command: ["python", "-m", "streamlit", "run", "mcp_server/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
    depends_on:
      - mcp-server
    restart: unless-stopped
EOF

# Create logs and data directories
mkdir -p mcp_server/logs
mkdir -p mcp_server/data

# Build and start the application
echo "🔨 Building and starting application..."
docker-compose up -d --build

# Wait for containers to start
echo "⏳ Waiting for containers to start..."
sleep 30

# Create systemd service for auto-restart
echo "⚙️ Creating systemd service..."
cat > /etc/systemd/system/mcp-server.service << 'EOF'
[Unit]
Description=MCP Server
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/mcp-server/MCP-hackathon
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl enable mcp-server.service
systemctl start mcp-server.service

# Final verification
echo "�� Final verification..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Docker containers are running"
else
    echo "❌ Docker containers are not running"
fi

echo "🎉 MCP Server deployment completed!"
echo "🌐 MCP Server: http://localhost:8000"
echo "📊 Streamlit App: http://localhost:8501"
echo "🔧 Logs: docker-compose logs -f"
