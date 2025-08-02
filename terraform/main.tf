terraform {
  required_version = ">= 1.0"
}

provider "aws" {
  region = "ap-south-1"
  
  default_tags {
    tags = {
      Team = "Minds-Constructing-Products"
      Name = "Minds-Constructing-Products"
      Environment = "production"
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

data "aws_availability_zones" "available" {
  state = "available"
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

# Security Groups - CORRECTED
resource "aws_security_group" "mcp_server" {
  name_prefix = "mcp-server-sg"
  vpc_id      = data.aws_vpc.default.id

  # MCP Server API
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MCP Server API"
  }

  # SSH Access
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH Access"
  }

  # PostgreSQL - INTERNAL ONLY
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
    description = "PostgreSQL Database"
  }

  # Redis - INTERNAL ONLY
  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
    description = "Redis Cache"
  }

  # HTTP for future load balancer
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP Access"
  }

  # HTTPS for future load balancer
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS Access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All Outbound Traffic"
  }

  tags = {
    Name = "MCP-Server-Security-Group"
  }
}

# EC2 Instance - CORRECTED
resource "aws_instance" "mcp_server" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t3.medium"  # UPGRADED for better performance
  key_name              = "Minds-Constructing-Products-key"
  vpc_security_group_ids = [aws_security_group.mcp_server.id]
  subnet_id              = data.aws_subnets.public.ids[0]
  associate_public_ip_address = true

  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = base64encode(file("${path.module}/user_data.sh"))

  tags = {
    Name = "MCP-Server-Instance"
  }
}

# ECR Repository
resource "aws_ecr_repository" "mcp_server" {
  name                 = "minds-constructing-products/mcp-server"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name = "MCP-Server-ECR"
  }
}

# S3 Bucket for logs and data
resource "aws_s3_bucket" "mcp_data" {
  bucket = "minds-constructing-products-mcp-data"

  tags = {
    Name = "MCP-Data-Bucket"
  }
}

resource "aws_s3_bucket_versioning" "mcp_data" {
  bucket = aws_s3_bucket.mcp_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mcp_data" {
  bucket = aws_s3_bucket.mcp_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
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

# Outputs
output "instance_public_ip" {
  description = "Public IP of the MCP server instance"
  value       = aws_instance.mcp_server.public_ip
}

output "mcp_server_url" {
  description = "URL of the MCP server"
  value       = "http://${aws_instance.mcp_server.public_ip}:8000"
}

output "health_check_url" {
  description = "Health check URL"
  value       = "http://${aws_instance.mcp_server.public_ip}:8000/health"
}
