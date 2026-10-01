resource "google_storage_bucket" "guidelines_bucket" {
  count                       = var.create_bucket ? 1 : 0
  name                        = var.bucket_name
  project                     = var.project_id
  location                    = var.location
  uniform_bucket_level_access = true
  force_destroy               = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 3
      with_state         = "ARCHIVED"
    }
  }
}

data "google_storage_bucket" "existing_bucket" {
  count = var.create_bucket ? 0 : 1
  name  = var.bucket_name
}
