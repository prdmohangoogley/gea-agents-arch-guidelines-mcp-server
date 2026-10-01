output "service_name" {
  description = "Cloud Run service name"
  value       = google_cloud_run_v2_service.mcp_server.name
}

output "service_uri" {
  description = "Cloud Run service URI"
  value       = google_cloud_run_v2_service.mcp_server.uri
}

output "service_account_email" {
  description = "Cloud Run runtime service account email"
  value       = google_service_account.mcp_runner.email
}
