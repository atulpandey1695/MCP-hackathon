# MCP Server AWS Infrastructure

This Terraform configuration deploys a cost-optimized, scalable AWS infrastructure for the MCP (Model Context Protocol) Development Assistant Server.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Internet      │    │   ALB           │    │   EC2 Instance  │
│                 │────│   (Load         │────│   (t2.micro)    │
│                 │    │   Balancer)     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │   RDS           │
                                              │   PostgreSQL    │
                                              │   (db.t2.micro) │
                                              └─────────────────┘
```

## 📋 Infrastructure Components

### Compute
- **EC2 Instance**: `t2.micro` (1 vCPU, 1GB RAM, 20GB EBS)
- **AMI**: Amazon Linux 2023 ARM64
- **Auto-scaling**: Manual scaling capability

### Database
- **RDS PostgreSQL**: `db.t2.micro` (1 vCPU, 1GB RAM, 10GB storage)
- **Backup**: 7-day retention
- **Encryption**: Enabled

### Storage
- **S3 Bucket**: `minds-constructing-products-mcp-data`
- **ECR Repository**: `minds-constructing-products/mcp-server`

### Networking
- **Load Balancer**: Application Load Balancer
- **Security Groups**: Restricted access
- **VPC**: Default VPC in ap-south-1

### Monitoring
- **CloudWatch Logs**: `/aws/mcp-server`
- **Health Checks**: Application-level monitoring

## 🚀 Quick Start

### Prerequisites
1. AWS CLI configured
2. Terraform installed
3. SSH key pair (auto-generated)

### Deployment Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd MCP-hackathon/terraform

# 2. Run deployment script
chmod +x deploy.sh
./deploy.sh
```

### Manual Deployment

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply
```

## 🔧 Configuration

### Environment Variables
- `AWS_REGION`: ap-south-1
- `TEAM_NAME`: Minds-Constructing-Products
- `INSTANCE_TYPE`: t2.micro
- `RDS_INSTANCE_CLASS`: db.t2.micro

### Customization
Edit `variables.tf` to modify:
- Instance types
- Storage sizes
- Region settings
- Team name

## 📊 Monitoring & Logging

### Application URLs
- **REST API**: `http://<alb-dns-name>`
- **WebSocket**: `ws://<alb-dns-name>/mcp`
- **Health Check**: `http://<alb-dns-name>/`

### Log Locations
- **Application Logs**: `/opt/mcp-server/logs/`
- **System Logs**: `sudo journalctl -u mcp-server.service`
- **CloudWatch**: `/aws/mcp-server`

## 🔒 Security

### Security Groups
- **EC2**: Port 8000 (HTTP), 22 (SSH)
- **RDS**: Port 5432 (PostgreSQL) from EC2 only
- **ALB**: Port 80 (HTTP)

### IAM Roles
- **EC2 Role**: S3, ECR, CloudWatch access
- **RDS**: Encrypted storage

## 🛠️ Maintenance

### Scaling
```bash
# Scale EC2 instance
aws ec2 modify-instance-attribute --instance-id <id> --instance-type "t3.micro"

# Scale RDS instance
aws rds modify-db-instance --db-instance-identifier <id> --db-instance-class "db.t3.micro"
```

### Backup
- **RDS**: Automated daily backups (7-day retention)
- **S3**: Versioning enabled
- **EC2**: EBS snapshots recommended

### Updates
```bash
# Update application
ssh -i ssh/mcp-server-key ec2-user@<public-ip>
cd /opt/mcp-server
git pull
docker-compose up -d --build
```

## 🚨 Troubleshooting

### Common Issues

1. **Application not starting**
   ```bash
   ssh -i ssh/mcp-server-key ec2-user@<public-ip>
   sudo journalctl -u mcp-server.service -f
   ```

2. **Database connection issues**
   ```bash
   # Check RDS status
   aws rds describe-db-instances --db-instance-identifier mcp-postgres
   ```

3. **Load balancer health checks failing**
   ```bash
   # Check target group health
   aws elbv2 describe-target-health --target-group-arn <target-group-arn>
   ```

### Health Checks
- **Application**: `curl http://localhost:8000/`
- **Database**: `psql -h <rds-endpoint> -U mcp_admin -d mcp_assistant`
- **Redis**: `redis-cli ping`

## 📈 Performance Optimization

### Recommendations
1. **Enable RDS Performance Insights** for database monitoring
2. **Use CloudFront** for global content delivery
3. **Implement caching** with Redis
4. **Monitor with CloudWatch** for auto-scaling

### Resource Limits
- **EC2**: 1 vCPU, 1GB RAM
- **RDS**: 1 vCPU, 1GB RAM, 10GB storage
- **S3**: Unlimited storage
- **ALB**: 1000 requests/second

## 🧹 Cleanup

```bash
# Destroy infrastructure
terraform destroy

# Remove SSH keys
rm -rf ssh/
```

## 📞 Support

For issues or questions:
1. Check CloudWatch logs
2. Review application logs
3. Verify security group rules
4. Test connectivity to RDS

---

**Team**: Minds-Constructing-Products  
**Region**: ap-south-1  
**Environment**: Production  
**Last Updated**: $(date) 