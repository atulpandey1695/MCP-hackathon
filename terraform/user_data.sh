#!/bin/bash

# MCP Server Deployment Script
# CORRECTED based on manual workaround

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

# Install PostgreSQL - CORRECTED
echo "🗄️ Installing PostgreSQL..."
yum install -y postgresql postgresql-server postgresql-contrib

# Initialize PostgreSQL - CORRECTED
echo "🗄️ Initializing PostgreSQL..."
/usr/bin/postgresql-setup initdb
systemctl enable postgresql
systemctl start postgresql

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to start..."
sleep 10

# Create PostgreSQL user and database - CORRECTED
echo "👤 Creating database user and database..."
sudo -u postgres psql -c "CREATE USER mcp_admin WITH PASSWORD 'mcp_password_123';" 2>/dev/null || echo "User might already exist"
sudo -u postgres psql -c "CREATE DATABASE mcp_assistant OWNER mcp_admin;" 2>/dev/null || echo "Database might already exist"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mcp_assistant TO mcp_admin;"

# Configure PostgreSQL - CORRECTED
echo "🔧 Configuring PostgreSQL..."
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /var/lib/pgsql/data/postgresql.conf
sed -i "s/#port = 5432/port = 5432/" /var/lib/pgsql/data/postgresql.conf

# Configure PostgreSQL authentication - CORRECTED
echo "host    mcp_assistant    mcp_admin    127.0.0.1/32            md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf
echo "host    mcp_assistant    mcp_admin    ::1/128                 md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf

# Add Docker network access - CORRECTED
echo "host    mcp_assistant    mcp_admin    172.17.0.0/16           md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf
echo "host    mcp_assistant    mcp_admin    172.18.0.0/16           md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf
echo "host    mcp_assistant    mcp_admin    172.19.0.0/16           md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf
echo "host    mcp_assistant    mcp_admin    172.20.0.0/16           md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf
echo "host    mcp_assistant    mcp_admin    172.21.0.0/16           md5" | sudo tee -a /var/lib/pgsql/data/pg_hba.conf

# Restart PostgreSQL
systemctl restart postgresql

# Stop system Redis to avoid conflicts
echo "🔴 Stopping system Redis..."
systemctl stop redis || true
systemctl disable redis || true

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/mcp-server
cd /opt/mcp-server

# Clone the repository
echo "�� Cloning MCP server repository..."
git clone https://github.com/atulpandey1695/MCP-hackathon.git .

# Navigate to the correct directory
cd MCP-hackathon

# Create Dockerfile - CORRECTED
echo "🐳 Creating Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["python", "server.py"]
EOF

# Create requirements.txt - CORRECTED
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'EOF'
fastapi
uvicorn
langchain>=0.1.47
langchain-openai
openai
requests
beautifulsoup4
pydantic
python-dotenv
mistralai
faiss-cpu
langchain-community
psycopg2-binary==2.9.7
flask==2.3.3
redis==4.6.0
EOF

# Create docker-compose.yml - CORRECTED
echo "🐳 Creating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://mcp_admin:mcp_password_123@host.docker.internal:5432/mcp_assistant
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - mcp-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

volumes:
  redis_data:

networks:
  mcp-network:
    driver: bridge
EOF

# Create logs directory
mkdir -p logs

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
After=docker.service postgresql.service
Requires=docker.service postgresql.service

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
if systemctl is-active --quiet postgresql; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL is not running"
fi

if docker-compose ps | grep -q "Up"; then
    echo "✅ Docker containers are running"
else
    echo "❌ Docker containers are not running"
fi

echo "🎉 MCP Server deployment completed!"
echo "�� Health check: curl http://localhost:8000/health"
echo "🔧 Logs: docker-compose logs -f"
