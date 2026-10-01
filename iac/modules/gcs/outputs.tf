output "bucket_name" {
  description = "GCS bucket name"
  value       = var.create_bucket ? google_storage_bucket.guidelines_bucket[0].name : data.google_storage_bucket.existing_bucket[0].name
}

output "bucket_url" {
  description = "GCS bucket URL"
  value       = var.create_bucket ? google_storage_bucket.guidelines_bucket[0].url : data.google_storage_bucket.existing_bucket[0].url
}
