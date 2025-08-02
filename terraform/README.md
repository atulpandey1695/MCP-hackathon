# 🚀 MCP Server AWS Infrastructure

This directory contains the Terraform configuration for deploying the MCP Server on AWS infrastructure.

## 📋 Overview

The infrastructure deploys a complete MCP Server environment with the following components:

- **EC2 Instance**: t2.micro with Amazon Linux 2
- **PostgreSQL**: Local installation on EC2 (port 5432)
- **Redis**: Local installation on EC2 (port 6379)
- **Docker**: Containerized MCP Server application
- **S3 Bucket**: Data storage
- **ECR Repository**: Container image storage
- **CloudWatch Logs**: Application logging

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        AWS Cloud                          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ap-south-1 Region                     │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │           Default VPC                      │   │   │
│  │  │  ┌─────────────────────────────────────┐   │   │   │
│  │  │  │         Public Subnet              │   │   │   │
│  │  │  │  ┌─────────────────────────────┐   │   │   │   │
│  │  │  │  │      EC2 Instance           │   │   │   │   │
│  │  │  │  │  ┌─────────────────────┐   │   │   │   │   │
│  │  │  │  │  │   MCP Server App    │   │   │   │   │   │
│  │  │  │  │  │   (Port 8000)       │   │   │   │   │   │
│  │  │  │  │  └─────────────────────┘   │   │   │   │   │
│  │  │  │  │  ┌─────────────────────┐   │   │   │   │   │
│  │  │  │  │  │   PostgreSQL        │   │   │   │   │   │
│  │  │  │  │  │   (Port 5432)       │   │   │   │   │   │
│  │  │  │  │  └─────────────────────┘   │   │   │   │   │
│  │  │  │  │  ┌─────────────────────┐   │   │   │   │   │
│  │  │  │  │  │   Redis             │   │   │   │   │   │
│  │  │  │  │  │   (Port 6379)       │   │   │   │   │   │
│  │  │  │  │  └─────────────────────┘   │   │   │   │   │
│  │  │  │  └─────────────────────────────┘   │   │   │   │
│  │  │  └─────────────────────────────────────┘   │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │              S3 Bucket                     │   │   │
│  │  │        (Data Storage)                      │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │            ECR Repository                  │   │   │
│  │  │      (Container Images)                    │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │          CloudWatch Logs                   │   │   │
│  │  │        (Application Logs)                  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
terraform/
├── main.tf              # Main Terraform configuration
├── variables.tf         # Input variables
├── outputs.tf          # Output values
├── versions.tf         # Terraform and provider versions
├── user_data.sh        # EC2 instance setup script
├── .gitignore          # Git ignore rules
├── README.md           # This file
├── DEPLOYMENT_GUIDE.md # Detailed deployment guide
├── MANUAL_DEPLOYMENT.md # Manual deployment instructions
└── workflow.md         # Workflow documentation
```

## 🚀 Quick Start

### Prerequisites

1. **AWS CLI** configured with appropriate permissions
2. **Terraform** installed (version >= 1.0)
3. **SSH key pair** named `Minds-Constructing-Products-key.pem`
4. **AWS Region**: ap-south-1

### Deployment

```bash
# 1. Navigate to terraform directory
cd terraform

# 2. Initialize Terraform
terraform init

# 3. Review the plan
terraform plan

# 4. Apply the infrastructure
terraform apply
```

### Verification

```bash
# Get connection information
terraform output

# SSH to the instance
ssh -i "Minds-Constructing-Products-key.pem" ec2-user@<PUBLIC_IP>

# Check services
sudo systemctl status postgresql-12 redis mcp-server.service

# Test application
curl http://localhost:8000/health
```

## 🔧 Configuration

### Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `aws_region` | AWS region | `ap-south-1` |
| `team_name` | Team name for tagging | `Minds-Constructing-Products` |
| `environment` | Environment name | `production` |
| `instance_type` | EC2 instance type | `t2.micro` |
| `ec2_volume_size` | Root volume size (GB) | `30` |

### Resources Created

- **EC2 Instance**: t2.micro with 30GB GP3 volume
- **Security Group**: Ports 22, 8000, 5432, 6379
- **S3 Bucket**: Data storage with versioning and encryption
- **ECR Repository**: Container image storage
- **CloudWatch Log Group**: Application logging

## 🔍 Monitoring

### Application Endpoints

- **Main Application**: `http://<PUBLIC_IP>:8000`
- **Health Check**: `http://<PUBLIC_IP>:8000/health`
- **Tools Endpoint**: `http://<PUBLIC_IP>:8000/tools`

### Log Locations

- **Application Logs**: `/opt/mcp-server/logs/mcp-server.log`
- **System Logs**: `journalctl -u mcp-server.service`
- **Docker Logs**: `docker-compose logs -f`

## 🐛 Troubleshooting

### Common Issues

1. **Services not running**: Check `systemctl status`
2. **Application not responding**: Check `docker-compose ps`
3. **Database connection failed**: Check PostgreSQL service
4. **Memory issues**: Optimize for t2.micro

### Useful Commands

```bash
# Check all services
sudo systemctl status postgresql-12 redis mcp-server.service

# Check ports
sudo netstat -tulpn | grep -E ":(8000|6379|5432)"

# Check containers
cd /opt/mcp-server && docker-compose ps

# Check logs
tail -f /opt/mcp-server/logs/mcp-server.log

# Restart services
sudo systemctl restart mcp-server.service
```

## 🗑️ Cleanup

```bash
# Destroy infrastructure
terraform destroy
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Detailed deployment instructions
- [Manual Deployment](MANUAL_DEPLOYMENT.md) - Manual deployment steps
- [Workflow](workflow.md) - Infrastructure workflow

## 🔐 Security

- **SSH Access**: Key-based authentication only
- **Security Groups**: Minimal required ports
- **EBS Encryption**: All volumes encrypted
- **S3 Encryption**: Server-side encryption enabled
- **IAM**: Minimal required permissions

## 📈 Performance

Optimized for t2.micro instances:
- Memory management with swappiness=10
- Docker resource limits
- Redis memory limits
- Efficient container base images

---

**🎉 Ready to deploy your MCP Server infrastructure!** 