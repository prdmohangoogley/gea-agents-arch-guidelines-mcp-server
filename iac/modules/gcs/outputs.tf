output "bucket_name" {
  description = "GCS bucket name"
  value       = google_storage_bucket.guidelines_bucket.name
}

output "bucket_url" {
  description = "GCS bucket URL"
  value       = google_storage_bucket.guidelines_bucket.url
}
