output "service_url" {
  description = "The URL of the AWS App Runner service"
  value       = aws_apprunner_service.app-service.service_url
  sensitive   = false
}