variable "AWS_REGION" {
  description = "AWS Region"
  type        = string
  default     = "us-east-1"
}

variable "image_uri" {
  description = "ECR image URI"
  type        = string
  default = "536697239284.dkr.ecr.us-east-1.amazonaws.com/text_to_image_service:latest"
}