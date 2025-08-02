#!/bin/bash

# MCP Server AWS Infrastructure Setup Guide
# Team: Minds-Constructing-Products
# Manual Terraform Deployment Guide

set -e

echo "🚀 MCP Server AWS Infrastructure Setup Guide"
echo "Team: Minds-Constructing-Products"
echo "Region: ap-south-1"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform is not installed. Please install Terraform first."
    echo "Installation guide: https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install AWS CLI first."
    echo "Installation guide: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    echo "Configuration guide: https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html"
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Check for manually created key pair
echo "🔑 Checking for manually created key pair..."
if [ -f "Minds-Constructing-Products-key.pem" ]; then
    echo "✅ Key pair file found: Minds-Constructing-Products-key.pem"
    echo "✅ Key pair already created manually"
else
    echo "⚠️  Key pair file not found!"
    echo "Please create the key pair manually using:"
    echo "aws ec2 create-key-pair \\"
    echo "  --key-name Minds-Constructing-Products-key \\"
    echo "  --query 'KeyMaterial' \\"
    echo "  --output text \\"
    echo "  --tag-specifications 'ResourceType=key-pair,Tags=[{Key=Team,Value=Minds-Constructing-Products},{Key=Name,Value=Minds-Constructing-Products}]' \\"
    echo "  > Minds-Constructing-Products-key.pem"
    echo ""
    echo "Then set permissions:"
    echo "chmod 400 Minds-Constructing-Products-key.pem"
    exit 1
fi

echo ""
echo "🔧 Manual Terraform Deployment Steps:"
echo "====================================="
echo ""
echo "Step 1: Initialize Terraform"
echo "----------------------------"
echo "terraform init"
echo ""
echo "Step 2: Review the deployment plan"
echo "---------------------------------"
echo "terraform plan"
echo ""
echo "Step 3: Apply the infrastructure"
echo "-------------------------------"
echo "terraform apply"
echo ""
echo "Step 4: Get deployment outputs"
echo "-----------------------------"
echo "terraform output"
echo ""
echo "Step 5: Destroy infrastructure (when needed)"
echo "-------------------------------------------"
echo "terraform destroy"
echo ""

echo "⚠️  Infrastructure Details:"
echo "=========================="
echo "   - EC2 Instance (t2.micro) with 20GB EBS"
echo "   - RDS PostgreSQL (db.t2.micro) with 10GB storage (no encryption)"
echo "   - Application Load Balancer (single subnet)"
echo "   - ECR Repository"
echo "   - S3 Bucket"
echo "   - Security Groups and IAM Roles"
echo "   - Key Pair: Minds-Constructing-Products-key (manually created)"
echo ""

echo "🔧 Recent Fixes Applied:"
echo "======================="
echo "✅ RDS encryption disabled (t2.micro limitation)"
echo "✅ Load balancer uses single subnet (AZ conflict fix)"
echo "✅ Using manually created key pair (permission fix)"
echo "✅ Simplified IAM policies (permission fixes)"
echo ""

echo "🔗 After deployment, you can access:"
echo "==================================="
echo "REST API: http://<alb-dns-name>"
echo "WebSocket: ws://<alb-dns-name>/mcp"
echo "Health Check: http://<alb-dns-name>/"
echo ""

echo "🔧 Post-deployment steps:"
echo "========================"
echo "1. SSH to the server: ssh -i Minds-Constructing-Products-key.pem ec2-user@<public-ip>"
echo "2. Check application logs: sudo journalctl -u mcp-server.service -f"
echo "3. Monitor the application: curl http://<alb-dns-name>/"
echo "4. View CloudWatch logs: /aws/mcp-server"
echo ""

echo "📚 Additional Resources:"
echo "======================="
echo "- Terraform Documentation: https://www.terraform.io/docs"
echo "- AWS Provider Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs"
echo "- MCP Server Documentation: README.md"
echo ""

echo "🎉 Ready to deploy! Run the terraform commands manually as shown above." 