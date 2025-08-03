output "mcp_server_public_ip" {
  description = "Public IP of the MCP server instance"
  value       = aws_instance.mcp_server.public_ip
}

output "mcp_server_private_ip" {
  description = "Private IP of the MCP server instance"
  value       = aws_instance.mcp_server.private_ip
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.mcp_server.repository_url
}

output "s3_bucket_name" {
  description = "S3 bucket name for data storage"
  value       = aws_s3_bucket.mcp_data.bucket
}

output "application_urls" {
  description = "Application access URLs"
  value = {
    mcp_server_api = "http://${aws_instance.mcp_server.public_ip}:8000"
    streamlit_app  = "http://${aws_instance.mcp_server.public_ip}:8501"
    websocket      = "ws://${aws_instance.mcp_server.public_ip}:8000/mcp"
    health_check   = "http://${aws_instance.mcp_server.public_ip}:8000/"
  }
}

output "ssh_connection" {
  description = "SSH connection command"
  value       = "ssh -i Minds-Constructing-Products-key.pem ec2-user@${aws_instance.mcp_server.public_ip}"
}

output "infrastructure_details" {
  description = "Infrastructure resource details"
  value = {
    ec2_instance_type = aws_instance.mcp_server.instance_type
    ec2_volume_size = aws_instance.mcp_server.root_block_device[0].volume_size
    region = aws_instance.mcp_server.availability_zone
    key_name = "Minds-Constructing-Products-key"
    containers = ["mcp-server", "streamlit"]
    ports = ["8000", "8501"]
  }
}
