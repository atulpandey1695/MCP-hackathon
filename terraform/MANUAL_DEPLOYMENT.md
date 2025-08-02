# Manual Terraform Deployment Guide

## 🚀 Step-by-Step Deployment Instructions

This guide provides manual steps to deploy the MCP Server infrastructure using Terraform CLI commands.

### **Prerequisites Check**

Before starting, ensure you have:

1. **Terraform installed** (version >= 1.0)
2. **AWS CLI installed** and configured
3. **AWS credentials** with appropriate permissions
4. **Git** for cloning the repository

### **Step 1: Setup Environment**

```bash
# Navigate to the terraform directory
cd MCP-hackathon/terraform

# Verify you're in the correct directory
ls -la
# Should show: main.tf, variables.tf, outputs.tf, etc.
```

### **Step 2: Initialize Terraform**

```bash
# Initialize Terraform and download providers
terraform init

# Expected output:
# Initializing the backend...
# Initializing provider plugins...
# Terraform has been successfully initialized!
```

### **Step 3: Review Configuration**

```bash
# Validate the configuration
terraform validate

# Expected output:
# Success! The configuration is valid.
```

### **Step 4: Plan the Deployment**

```bash
# Create a deployment plan
terraform plan

# This will show:
# - Resources to be created
# - Configuration details
```

**Expected Resources to be Created:**
- 1 EC2 Instance (t2.micro)
- 1 RDS PostgreSQL Instance (db.t2.micro)
- 1 Application Load Balancer
- 1 ECR Repository
- 1 S3 Bucket
- Security Groups and IAM Roles

### **Step 5: Apply the Infrastructure**

```bash
# Deploy the infrastructure
terraform apply

# Terraform will prompt for confirmation:
# Do you want to perform these actions?
#   Terraform will perform the actions described above.
#   Only 'yes' will be accepted to approve.
#
# Enter a value: yes
```

**Deployment Time:** ~10-15 minutes

### **Step 6: Verify Deployment**

```bash
# Get deployment outputs
terraform output

# Expected outputs:
# - mcp_server_public_ip
# - load_balancer_dns
# - rds_endpoint
# - application_urls
```

### **Step 7: Test the Application**

```bash
# Get the load balancer DNS name
terraform output -raw load_balancer_dns

# Test the health endpoint
curl http://$(terraform output -raw load_balancer_dns)

# Test WebSocket endpoint
curl http://$(terraform output -raw load_balancer_dns)/mcp
```

### **Step 8: SSH to the Server**

```bash
# Get the SSH command
terraform output -raw ssh_connection

# Or manually construct:
ssh -i ssh/mcp-server-key ec2-user@$(terraform output -raw mcp_server_public_ip)
```

## 🔧 Management Commands

### **View Current State**

```bash
# Show current infrastructure state
terraform show

# List all resources
terraform state list
```

### **Update Infrastructure**

```bash
# Plan changes
terraform plan

# Apply changes
terraform apply
```

### **Destroy Infrastructure**

```bash
# Plan destruction
terraform plan -destroy

# Destroy all resources
terraform destroy

# Confirm with 'yes' when prompted
```

## 📊 Monitoring Commands

### **Check Application Status**

```bash
# SSH to server and check service status
ssh -i ssh/mcp-server-key ec2-user@$(terraform output -raw mcp_server_public_ip)
sudo systemctl status mcp-server.service

# Check application logs
sudo journalctl -u mcp-server.service -f
```

### **Check Infrastructure Health**

```bash
# Check EC2 instance
aws ec2 describe-instances --instance-ids $(terraform output -raw mcp_server_id)

# Check RDS status
aws rds describe-db-instances --db-instance-identifier mcp-postgres

# Check ALB health
aws elbv2 describe-target-health --target-group-arn $(terraform output -raw target_group_arn)
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Terraform init fails**
   ```bash
   # Clear and reinitialize
   rm -rf .terraform
   terraform init
   ```

2. **AWS credentials error**
   ```bash
   # Reconfigure AWS credentials
   aws configure
   ```

3. **Resource creation timeout**
   ```bash
   # Check AWS console for resource status
   # Wait and retry terraform apply
   ```

4. **SSH connection issues**
   ```bash
   # Check security group rules
   # Verify SSH key permissions
   chmod 600 ssh/mcp-server-key
   ```

5. **Memory issues on t2.micro**
   ```bash
   # Check memory usage
   free -h
   
   # Check Docker container memory
   docker stats
   
   # Restart services if needed
   sudo systemctl restart mcp-server.service
   ```

### **Debug Commands**

```bash
# Enable Terraform debug logging
export TF_LOG=DEBUG
terraform apply

# Check specific resource
terraform state show aws_instance.mcp_server

# Import existing resources (if needed)
terraform import aws_instance.mcp_server i-1234567890abcdef0
```

## 📈 Scaling Operations

### **Scale EC2 Instance**

```bash
# Edit variables.tf to change instance type
# Then run:
terraform plan
terraform apply
```

### **Scale RDS Instance**

```bash
# Edit variables.tf to change RDS instance class
# Then run:
terraform plan
terraform apply
```

## 🧹 Cleanup

### **Complete Cleanup**

```bash
# Destroy all resources
terraform destroy

# Remove local files
rm -rf .terraform/
rm terraform.tfstate*
rm -rf ssh/
```

### **Partial Cleanup**

```bash
# Destroy specific resources
terraform destroy -target=aws_instance.mcp_server
terraform destroy -target=aws_db_instance.mcp_postgres
```

## 📋 Useful Commands Reference

| Command | Purpose |
|---------|---------|
| `terraform init` | Initialize Terraform |
| `terraform plan` | Preview changes |
| `terraform apply` | Deploy infrastructure |
| `terraform destroy` | Remove infrastructure |
| `terraform output` | Show outputs |
| `terraform state list` | List resources |
| `terraform show` | Show current state |
| `terraform validate` | Validate configuration |

## 🔗 Application URLs

After deployment, access your application at:

- **REST API**: `http://<alb-dns-name>`
- **WebSocket**: `ws://<alb-dns-name>/mcp`
- **Health Check**: `http://<alb-dns-name>/`

## 📊 Resource Specifications

### **EC2 Instance (t2.micro)**
- **vCPU**: 1
- **Memory**: 1 GB
- **Storage**: 20 GB EBS
- **Network**: Low to Moderate

### **RDS Instance (db.t2.micro)**
- **vCPU**: 1
- **Memory**: 1 GB
- **Storage**: 10 GB
- **Network**: Low to Moderate

### **Optimization Notes**
- Application optimized for low memory usage
- Redis configured with memory limits
- Docker containers with resource constraints
- System optimized for t2.micro specifications

---

**Team**: Minds-Constructing-Products  
**Region**: ap-south-1  
**Last Updated**: $(date) 