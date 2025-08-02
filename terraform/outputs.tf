# Enhanced Outputs for MCP Server Infrastructure

output "mcp_server_public_ip" {
  description = "Public IP address of the MCP server instance"
  value       = aws_instance.mcp_server.public_ip
}

output "mcp_server_private_ip" {
  description = "Private IP address of the MCP server instance"
  value       = aws_instance.mcp_server.private_ip
}

output "ecr_repository_url" {
  description = "URL of the ECR repository"
  value       = aws_ecr_repository.mcp_server.repository_url
}

output "s3_bucket_name" {
  description = "Name of the S3 bucket for data storage"
  value       = aws_s3_bucket.mcp_data.bucket
}

output "application_urls" {
  description = "Application access URLs"
  value = {
    main_application = "http://${aws_instance.mcp_server.public_ip}:8000"
    health_check     = "http://${aws_instance.mcp_server.public_ip}:8000/health"
    tools_endpoint   = "http://${aws_instance.mcp_server.public_ip}:8000/tools"
  }
}

output "ssh_connection" {
  description = "SSH connection command"
  value       = "ssh -i 'Minds-Constructing-Products-key.pem' ec2-user@${aws_instance.mcp_server.public_ip}"
}

output "infrastructure_details" {
  description = "Detailed infrastructure information"
  value = {
    instance_type     = aws_instance.mcp_server.instance_type
    instance_id       = aws_instance.mcp_server.id
    volume_size       = aws_instance.mcp_server.root_block_device[0].volume_size
    security_group_id = aws_security_group.mcp_server.id
    vpc_id           = data.aws_vpc.default.id
    subnet_id        = aws_instance.mcp_server.subnet_id
    ami_id           = aws_instance.mcp_server.ami
    postgres_location = "Local (EC2 Instance)"
    database_name    = "mcp_assistant"
    redis_location   = "Local (EC2 Instance)"
    application_port = 8000
    postgres_port    = 5432
    redis_port       = 6379
  }
}

output "deployment_status" {
  description = "Deployment status and verification commands"
  value = {
    status_check = "systemctl status mcp-server.service"
    health_check = "curl http://${aws_instance.mcp_server.public_ip}:8000/health"
    logs_check   = "tail -f /opt/mcp-server/logs/mcp-server.log"
    container_check = "docker-compose ps"
    database_check = "sudo -u postgres psql -d mcp_assistant -c 'SELECT 1;'"
    redis_check = "redis-cli ping"
  }
}

output "troubleshooting_commands" {
  description = "Useful troubleshooting commands"
  value = {
    check_services = "systemctl status postgresql-12 redis mcp-server.service"
    check_ports    = "netstat -tulpn | grep -E ':(8000|6379|5432)'"
    check_logs     = "journalctl -u mcp-server.service -f"
    restart_service = "systemctl restart mcp-server.service"
    check_containers = "cd /opt/mcp-server && docker-compose ps"
    check_resources = "free -h && df -h && docker stats"
  }
} 