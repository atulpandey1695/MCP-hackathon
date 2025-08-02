#!/bin/bash

# AWS ECS Deployment Script for MCP Development Assistant Server

set -e

# Configuration
AWS_REGION="us-east-1"
CLUSTER_NAME="mcp-dev-assistant"
SERVICE_NAME="mcp-server"
TASK_FAMILY="mcp-dev-assistant-task"
ECR_REPOSITORY="mcp-dev-assistant"
IMAGE_TAG="latest"

echo "Starting deployment of MCP Development Assistant Server..."

# Step 1: Build and push Docker image to ECR
echo "Building Docker image..."
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .

# Get ECR login token
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com

# Create ECR repository if it doesn't exist
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || \
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION

# Tag and push image
ECR_URI=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI
docker push $ECR_URI

# Step 2: Update ECS task definition
echo "Updating ECS task definition..."
cat > task-definition.json << EOF
{
  "family": "$TASK_FAMILY",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "mcp-server",
      "image": "$ECR_URI",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "REDIS_URL",
          "value": "redis://mcp-redis.cache.amazonaws.com:6379"
        },
        {
          "name": "POSTGRES_URL",
          "value": "postgresql://username:password@mcp-postgres.rds.amazonaws.com:5432/devassistant"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:mcp-secret-key"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):secret:openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-dev-assistant",
          "awslogs-region": "$AWS_REGION",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/ || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
EOF

# Register new task definition
NEW_REVISION=$(aws ecs register-task-definition --cli-input-json file://task-definition.json --query 'taskDefinition.revision' --output text)
echo "Registered new task definition revision: $NEW_REVISION"

# Step 3: Update ECS service
echo "Updating ECS service..."
aws ecs update-service \
  --cluster $CLUSTER_NAME \
  --service $SERVICE_NAME \
  --task-definition $TASK_FAMILY:$NEW_REVISION \
  --region $AWS_REGION

# Step 4: Wait for deployment to complete
echo "Waiting for deployment to complete..."
aws ecs wait services-stable \
  --cluster $CLUSTER_NAME \
  --services $SERVICE_NAME \
  --region $AWS_REGION

echo "Deployment completed successfully!"

# Clean up
rm task-definition.json

# Get service endpoint
LOAD_BALANCER_DNS=$(aws elbv2 describe-load-balancers \
  --names mcp-dev-assistant-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text \
  --region $AWS_REGION)

echo "Service is available at: https://$LOAD_BALANCER_DNS"
echo "MCP WebSocket endpoint: wss://$LOAD_BALANCER_DNS/mcp"
echo "REST API endpoint: https://$LOAD_BALANCER_DNS"
