resource "aws_s3_bucket" "avatars" {
  bucket = "${var.project_name}-avatars-${var.environment}"
}  

resource "aws_s3_bucket_public_access_block" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_cors_configuration" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# Google Cloud Storage bucket for video assets
resource "google_storage_bucket" "video_assets" {
  name          = var.gcs_bucket_name
  project       = var.gcp_project_id
  location      = "EU"
  storage_class = "STANDARD"
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 7 // objects older than 7 days will be deleted
    }
  }
}

resource "google_storage_bucket_iam_member" "video_assets_public_read" {
  bucket = google_storage_bucket.video_assets.name
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}
