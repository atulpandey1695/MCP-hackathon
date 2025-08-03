# MCP Server Infrastructure with Terraform

This repository contains Terraform configuration for deploying a **MCP (Model Context Protocol) Server** with **Streamlit UI** on AWS infrastructure.

## ��️ Architecture

### Infrastructure Components
- **EC2 Instance**: t3.medium running Amazon Linux 2
- **Security Group**: Configured for MCP Server (8000) and Streamlit (8501)
- **S3 Bucket**: For data storage and logs
- **ECR Repository**: For container image management
- **CloudWatch**: For centralized logging

### Application Components
- **MCP Server**: FastAPI-based server running on port 8000
- **Streamlit App**: Web UI running on port 8501
- **Docker Compose**: Orchestrates both containers

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate credentials
- Terraform >= 1.0
- SSH key pair named "Minds-Constructing-Products-key"

### Deployment Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/atulpandey1695/MCP-hackathon.git
   cd MCP-hackathon/terraform
   ```

2. **Initialize Terraform**
   ```bash
   terraform init
   ```

3. **Review the plan**
   ```bash
   terraform plan
   ```

4. **Deploy the infrastructure**
   ```bash
   terraform apply
   ```

5. **Access your applications**
   - MCP Server API: `http://<public-ip>:8000`
   - Streamlit UI: `http://<public-ip>:8501`
   - Health Check: `http://<public-ip>:8000/`

## 📋 Infrastructure Details

### Security Group Rules
| Port | Protocol | Source | Description |
|------|----------|--------|-------------|
| 22 | TCP | 0.0.0.0/0 | SSH Access |
| 80 | TCP | 0.0.0.0/0 | HTTP (Future LB) |
| 443 | TCP | 0.0.0.0/0 | HTTPS (Future LB) |
| 8000 | TCP | 0.0.0.0/0 | MCP Server API |
| 8501 | TCP | 0.0.0.0/0 | Streamlit App |

### EC2 Instance Specifications
- **Instance Type**: t3.medium (2 vCPU, 4 GB RAM)
- **Storage**: 30 GB GP3 encrypted volume
- **OS**: Amazon Linux 2
- **Region**: ap-south-1 (Mumbai)

### Container Configuration
- **MCP Server**: Python FastAPI application
- **Streamlit**: Web-based UI for tool management
- **Dependencies**: All Python packages included in requirements.txt

## �� Configuration

### Environment Variables
The deployment automatically configures:
- `SECRET_KEY`: Production secret key for the application
- Docker environment for container orchestration

### Application Structure
