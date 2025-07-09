provider "aws" {
  region = var.AWS_REGION
  
}

# Create the App Runner service
# This service will use an ECR image as the source
resource "aws_apprunner_service" "app-service" {
  service_name = "text-to-image-service"
  
  source_configuration {
    authentication_configuration {
        access_role_arn = aws_iam_role.apprunner_ecr_access_role.arn
        }
    image_repository {
      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          AWS_DEFAULT_REGION = var.AWS_REGION
        }
      }
      image_identifier      = var.image_uri
      image_repository_type = "ECR"
      }
      auto_deployments_enabled = true
    }
        

      instance_configuration {
      cpu    = "0.25 vCPU"
      memory = "0.5 GB"
      instance_role_arn = aws_iam_role.apprunner_instance_role.arn
   }
  
    health_check_configuration {
      healthy_threshold   = 1
      interval           = 10
      path              = "/health"
      protocol          = "HTTP"
      timeout           = 5
      unhealthy_threshold = 5
     }  
  }



# IAM role for App Runner ECR access
resource "aws_iam_role" "apprunner_ecr_access_role" {
  name = "apprunner-ecr-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "build.apprunner.amazonaws.com"
        }
      }
    ]
  })

}

# Attach the AWSAppRunnerServicePolicyForECRAccess policy to the App Runner ECR access role
resource "aws_iam_role_policy_attachment" "apprunner_ecr_access" {
  role       = aws_iam_role.apprunner_ecr_access_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

# IAM role for App Runner instance
resource "aws_iam_role" "apprunner_instance_role" {
  name = "apprunner-instance-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "tasks.apprunner.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Bedrock access
resource "aws_iam_role_policy" "bedrock_access" {
  name = "bedrock-access"
  role = aws_iam_role.apprunner_instance_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "arn:aws:bedrock:*::foundation-model/stability.stable-diffusion-xl-v1"
      }
    ]
  })
}