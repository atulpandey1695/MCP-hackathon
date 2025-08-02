# MCP Development Assistant Server

A Model Context Protocol (MCP) server that provides development assistance tools for teams, including codebase analysis, git conventions, JIRA patterns, and team collaboration features.

## 🚀 Features

- **Codebase Analysis**: Pattern recognition, naming conventions, folder structure analysis
- **Git Integration**: Commit convention analysis, contributor patterns
- **JIRA Integration**: Ticket pattern analysis, development insights
- **Team Collaboration**: Centralized development intelligence
- **Subscription Management**: Tiered access control with usage tracking
- **MCP Protocol**: Native VS Code Copilot integration

## 📁 Architecture

```
mcp-server/
├── server.py              # FastAPI MCP server
├── auth/                  # Authentication & subscription management
│   └── manager.py
├── core/                  # Tool registry and routing
│   └── tool_registry.py
├── config/                # Configuration management
│   └── settings.py
├── docker/                # Containerization files
├── deploy/                # Cloud deployment scripts
│   └── deploy-aws.sh
└── .env.example          # Environment configuration template
```

## 🔧 Local Development Setup

### Prerequisites

- Python 3.11+
- Redis server
- PostgreSQL (optional, SQLite used by default)
- Git

### Step 1: Clone and Setup

```bash
cd mcp-server
cp .env.example .env
```

### Step 2: Configure Environment

Edit `.env` file with your settings:

```bash
# Required
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key

# Optional (uses defaults)
REDIS_URL=redis://localhost:6379
HOST=0.0.0.0
PORT=8000
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start Redis (Required)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Or install locally
# Windows: Download from Redis website
# macOS: brew install redis && brew services start redis
# Linux: sudo apt install redis-server && sudo systemctl start redis
```

### Step 5: Run the Server

```bash
python server.py
```

Server will be available at:

- **REST API**: <http://localhost:8000>
- **MCP WebSocket**: ws://localhost:8000/mcp
- **Health Check**: <http://localhost:8000/>

## 🐳 Docker Local Deployment

### Single Container

```bash
# Build and run
docker build -t mcp-dev-assistant .
docker run -p 8000:8000 -e OPENAI_API_KEY=your-key mcp-dev-assistant
```

### Full Stack with Docker Compose

```bash
# Start all services (Redis, PostgreSQL, MCP Server)
docker-compose up -d

# View logs
docker-compose logs -f mcp-server

# Stop all services
docker-compose down
```

Services available:

- **MCP Server**: <http://localhost:8000>
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

## ☁️ Cloud Deployment

### AWS ECS/Fargate Deployment

#### Prerequisites

- AWS CLI configured
- Docker installed
- ECR repository access

#### Automated Deployment

```bash
# Make script executable
chmod +x deploy/deploy-aws.sh

# Deploy to AWS
./deploy/deploy-aws.sh
```

#### Manual AWS Setup

1. **Create ECR Repository**:

```bash
aws ecr create-repository --repository-name mcp-dev-assistant --region us-east-1
```

2. **Create ECS Cluster**:

```bash
aws ecs create-cluster --cluster-name mcp-dev-assistant
```

3. **Deploy Infrastructure** (recommended: use CloudFormation):

```bash
# Create VPC, subnets, load balancer, RDS, ElastiCache
# See deploy/cloudformation-template.yaml (create if needed)
```

4. **Deploy Application**:

```bash
./deploy/deploy-aws.sh
```

### Google Cloud Run Deployment

```bash
# Build and deploy
gcloud run deploy mcp-dev-assistant \
  --image gcr.io/PROJECT-ID/mcp-dev-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --set-env-vars OPENAI_API_KEY=your-key
```

### Azure Container Instances

```bash
# Create resource group
az group create --name mcp-dev-assistant --location eastus

# Deploy container
az container create \
  --resource-group mcp-dev-assistant \
  --name mcp-server \
  --image your-registry/mcp-dev-assistant \
  --ports 8000 \
  --environment-variables OPENAI_API_KEY=your-key
```

## 🔌 VS Code Integration

### Method 1: MCP Client Configuration

Add to VS Code settings or MCP client config:

```json
{
  "mcpServers": {
    "dev-assistant": {
      "command": "mcp",
      "args": ["--server", "ws://localhost:8000/mcp"],
      "env": {
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Method 2: REST API Integration

```javascript
// VS Code extension example
const response = await fetch('http://localhost:8000/tools/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': 'your-api-key'
  },
  body: JSON.stringify({
    tool_name: 'scan_codebase',
    arguments: { query: 'python naming conventions' }
  })
});
```

## 🎯 Usage Examples

### API Key Generation

```bash
# Generate API key for user
curl -X POST http://localhost:8000/auth/generate-key \
  -H "Content-Type: application/json" \
  -d '{"user_id": "developer@company.com"}'
```

### Execute Tools

```bash
# Scan codebase
curl -X POST http://localhost:8000/tools/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "scan_codebase",
    "arguments": {"query": "python patterns"}
  }'

# Check git conventions
curl -X POST http://localhost:8000/tools/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "check_git_conventions",
    "arguments": {"query": "commit patterns"}
  }'
```

### WebSocket (MCP Protocol)

```javascript
const ws = new WebSocket('ws://localhost:8000/mcp');

ws.send(JSON.stringify({
  method: 'tools/list',
  params: {},
  id: '1',
  apiKey: 'your-api-key'
}));
```

## 💰 Subscription Tiers

| Feature | Free | Pro | Enterprise |
|---------|------|-----|------------|
| **Queries/Month** | 100 | 1,000 | Unlimited |
| **Tools** | Basic | All | All + Custom |
| **Codebase Size** | 100MB | 500MB | 10GB+ |
| **Support** | Community | Email | Priority |
| **Custom Deployment** | ❌ | ❌ | ✅ |
| **White Label** | ❌ | ❌ | ✅ |

### Subscription Management

```bash
# Check subscription
curl -X GET http://localhost:8000/subscription \
  -H "X-API-Key: your-api-key"

# Upgrade subscription
curl -X POST http://localhost:8000/subscription/upgrade \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"tier": "pro"}'
```

## 🛠️ Development

### Adding New Tools

1. Create tool function in appropriate module
2. Update `tools.json` configuration
3. Tool registry will auto-discover and load

Example tool:

```python
def my_custom_tool(query: str) -> str:
    """Custom development tool"""
    return f"Processed: {query}"
```

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Load tests
pytest tests/load/ --verbose
```

### Monitoring

```bash
# Health check
curl http://localhost:8000/

# Metrics (if enabled)
curl http://localhost:9090/metrics
```

## 🔧 Troubleshooting

### Common Issues

**1. Redis Connection Error**

```bash
# Check Redis is running
redis-cli ping

# Should return "PONG"
```

**2. Tool Import Errors**

```bash
# Check Python path and module structure
python -c "from core.tool_registry import get_tool_registry; print('OK')"
```

**3. Authentication Issues**

```bash
# Verify API key in Redis
redis-cli get "apikey:your-api-key"
```

**4. Docker Issues**

```bash
# Check container logs
docker logs mcp-server

# Restart services
docker-compose restart
```

### Performance Optimization

**For Large Codebases:**

- Increase `MAX_CODEBASE_SIZE_MB` in config
- Use pagination for results
- Consider distributed processing

**For High Traffic:**

- Scale horizontally with load balancer
- Use Redis cluster for session storage
- Implement connection pooling

## 📚 API Documentation

Once running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: See `/docs` folder
- **Issues**: GitHub Issues
- **Enterprise Support**: Contact for priority support
- **Community**: Join our Discord/Slack
