variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "tamagotchi-health"
}

variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "The AWS region to deploy resources."
  type        = string
  default     = "eu-central-1"
}

variable "gcp_api_key" {
  description = "The Google Cloud API Key for GenAI models"
  type        = string
  default     = "" # This should be securely managed
}

variable "gcs_bucket_name" {
  description = "The name of the Google Cloud Storage bucket for video assets."
  type        = string
  default     = "tamagotchi-health-video-assets-dev"
}