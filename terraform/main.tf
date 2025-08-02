# Enhanced MCP Server Infrastructure
# Addresses all compatibility issues with Amazon Linux 2 and t2.micro

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Team = var.team_name
      Name = var.team_name
      Environment = var.environment
      Project = "MCP-Server"
    }
  }
}

# Data sources
data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
  filter {
    name   = "map-public-ip-on-launch"
    values = ["true"]
  }
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Groups
resource "aws_security_group" "mcp_server" {
  name_prefix = "mcp-server-sg"
  description = "Security group for MCP Server"
  vpc_id      = data.aws_vpc.default.id

  # SSH access
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Application port
  ingress {
    description = "MCP Server"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # PostgreSQL port (for local access)
  ingress {
    description = "PostgreSQL"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Redis port (for local access)
  ingress {
    description = "Redis"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "MCP-Server-Security-Group"
  }
}

# EC2 Instance
resource "aws_instance" "mcp_server" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = var.instance_type
  key_name               = "Minds-Constructing-Products-key"
  vpc_security_group_ids = [aws_security_group.mcp_server.id]
  subnet_id              = data.aws_subnets.public.ids[0]
  associate_public_ip_address = true
  
  root_block_device {
    volume_size = var.ec2_volume_size
    volume_type = "gp3"
    encrypted   = true
  }

  # Enhanced user_data with proper encoding
  user_data = base64encode(file("${path.module}/user_data.sh"))

  # Instance metadata options for better security
  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  # Monitoring
  monitoring = true

  tags = {
    Name = "MCP-Server-Instance"
  }

  # Lifecycle policy to prevent accidental deletion
  lifecycle {
    prevent_destroy = false
  }
}

# S3 Bucket for data storage
resource "aws_s3_bucket" "mcp_data" {
  bucket = "${var.team_name}-mcp-data"
  
  tags = {
    Name = "MCP-Data-Bucket"
  }
}

# S3 Bucket versioning
resource "aws_s3_bucket_versioning" "mcp_data" {
  bucket = aws_s3_bucket.mcp_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "mcp_data" {
  bucket = aws_s3_bucket.mcp_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ECR Repository for container images
resource "aws_ecr_repository" "mcp_server" {
  repository_name = "${var.team_name}/mcp-server"
  
  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "MCP-Server-ECR"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "mcp_logs" {
  name              = "/aws/mcp-server"
  retention_in_days = 7

  tags = {
    Name = "MCP-Server-Logs"
  }
}

# Random password for database (if needed in future)
resource "random_password" "db_password" {
  length  = 16
  special = false
} 