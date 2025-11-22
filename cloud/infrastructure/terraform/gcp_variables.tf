variable "gcp_project_id" {
  description = "The ID of the Google Cloud Project"
  type        = string
  default     = "hackatum25mun-1040" # Change this to your actual project ID
}

variable "gcp_region" {
  description = "The region for Google Cloud resources"
  type        = string
  default     = "europe-west3" # Frankfurt
}
