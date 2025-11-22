variable "aws_region" {
  description = "AWS region to deploy to"
  type        = string
  default     = "eu-central-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "tamagotchi-health"
}

variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "gcp_api_key" {
  description = "API Key for Google Cloud Vertex AI"
  type        = string
  sensitive   = true
  default     = ""
}
