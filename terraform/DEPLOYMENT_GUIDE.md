# 🚀 MCP Server Deployment Guide

## 📋 Overview

This guide provides step-by-step instructions for deploying the MCP Server infrastructure on AWS using Terraform. The infrastructure has been enhanced to address all compatibility issues with Amazon Linux 2 and t2.micro instances.

## 🏗️ Infrastructure Components

- **EC2 Instance**: t2.micro with Amazon Linux 2
- **PostgreSQL**: Local installation on EC2 (port 5432)
- **Redis**: Local installation on EC2 (port 6379)
- **Docker**: Containerized MCP Server application
- **S3 Bucket**: Data storage
- **ECR Repository**: Container image storage
- **CloudWatch Logs**: Application logging

## 🔧 Prerequisites

1. **AWS CLI configured** with appropriate permissions
2. **Terraform installed** (version >= 1.0)
3. **SSH key pair** named `Minds-Constructing-Products-key.pem`
4. **AWS Region**: ap-south-1

## 🚀 Deployment Steps

### Step 1: Verify Prerequisites

```bash
# Check Terraform version
terraform version

# Check AWS CLI
aws sts get-caller-identity

# Verify SSH key exists
ls -la Minds-Constructing-Products-key.pem
```

### Step 2: Initialize Terraform

```bash
cd terraform
terraform init
```

### Step 3: Review the Plan

```bash
terraform plan
```

**Expected Resources:**
- 1 EC2 Instance (t2.micro)
- 1 Security Group
- 1 S3 Bucket
- 1 ECR Repository
- 1 CloudWatch Log Group

### Step 4: Apply the Infrastructure

```bash
terraform apply
```

**Enter `yes` when prompted to confirm.**

### Step 5: Wait for Deployment

The deployment takes approximately 5-10 minutes. The user_data script will:
1. Install PostgreSQL and Redis
2. Setup Docker and Docker Compose
3. Clone the GitHub repository
4. Build and start the application
5. Configure SystemD services

## 🔍 Verification Steps

### Step 1: Get Connection Information

```bash
terraform output
```

### Step 2: SSH to the Instance

```bash
# Use the output from terraform
ssh -i "Minds-Constructing-Products-key.pem" ec2-user@<PUBLIC_IP>
```

### Step 3: Check Services

```bash
# Check all services
sudo systemctl status postgresql-12 redis mcp-server.service

# Check ports
sudo netstat -tulpn | grep -E ":(8000|6379|5432)"

# Check containers
cd /opt/mcp-server
docker-compose ps
```

### Step 4: Test Application

```bash
# Test main endpoint
curl http://localhost:8000/

# Test health endpoint
curl http://localhost:8000/health

# Test tools endpoint
curl http://localhost:8000/tools
```

## 🐛 Troubleshooting

### Issue: Services Not Running

```bash
# Check service status
sudo systemctl status postgresql-12 redis mcp-server.service

# Check logs
sudo journalctl -u mcp-server.service -f
sudo journalctl -u postgresql-12 -f
sudo journalctl -u redis -f
```

### Issue: Application Not Responding

```bash
# Check container status
cd /opt/mcp-server
docker-compose ps
docker-compose logs -f

# Restart service
sudo systemctl restart mcp-server.service
```

### Issue: Database Connection Failed

```bash
# Test PostgreSQL
sudo -u postgres psql -c "SELECT version();"
sudo -u postgres psql -d mcp_assistant -c "SELECT 1;"

# Test Redis
redis-cli ping
```

### Issue: Memory Issues (t2.micro)

```bash
# Check memory usage
free -h
docker stats

# Optimize memory
echo "vm.swappiness=10" >> /etc/sysctl.conf
sudo sysctl vm.swappiness=10

# Clean up Docker
docker system prune -f
```

## 📊 Monitoring Commands

### Resource Usage

```bash
# System resources
htop
df -h
free -h

# Docker resources
docker stats
docker system df
```

### Application Logs

```bash
# Application logs
tail -f /opt/mcp-server/logs/mcp-server.log

# System logs
sudo journalctl -u mcp-server.service -f
sudo journalctl -u postgresql-12 -f
```

### Health Checks

```bash
# Application health
curl http://localhost:8000/health

# Database health
sudo -u postgres psql -d mcp_assistant -c "SELECT 1;"

# Redis health
redis-cli ping
```

## 🔄 Maintenance

### Restart Services

```bash
# Restart all services
sudo systemctl restart postgresql-12 redis mcp-server.service

# Restart only application
sudo systemctl restart mcp-server.service
```

### Update Application

```bash
cd /opt/mcp-server
git pull
docker-compose down
docker-compose up -d --build
```

### Backup Database

```bash
# Backup PostgreSQL
sudo -u postgres pg_dump mcp_assistant > backup.sql

# Backup Redis
redis-cli BGSAVE
```

## 🗑️ Cleanup

### Destroy Infrastructure

```bash
terraform destroy
```

**Enter `yes` when prompted to confirm.**

### Manual Cleanup (if needed)

```bash
# Stop and remove containers
cd /opt/mcp-server
docker-compose down -v

# Remove application directory
sudo rm -rf /opt/mcp-server

# Stop services
sudo systemctl stop mcp-server.service postgresql-12 redis
sudo systemctl disable mcp-server.service postgresql-12 redis
```

## 📈 Performance Optimization

### For t2.micro Instances

1. **Memory Management**:
   - Set `vm.swappiness=10`
   - Limit Docker memory usage
   - Use Redis with memory limits

2. **Storage Optimization**:
   - Use GP3 volumes
   - Enable compression
   - Regular cleanup

3. **Application Optimization**:
   - Use lightweight base images
   - Implement health checks
   - Configure proper timeouts

## 🔐 Security Considerations

1. **SSH Access**: Use key-based authentication
2. **Firewall**: Security groups limit access
3. **Encryption**: EBS volumes are encrypted
4. **IAM**: Minimal required permissions
5. **Monitoring**: CloudWatch logs enabled

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review application logs
3. Verify service status
4. Check resource usage
5. Contact the team for assistance

---

**🎉 Your MCP Server is now deployed and ready to use!** 