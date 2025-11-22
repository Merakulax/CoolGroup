resource "google_project_service" "aiplatform" {
  service = "aiplatform.googleapis.com"
  project = var.gcp_project_id
  disable_on_destroy = false
}
