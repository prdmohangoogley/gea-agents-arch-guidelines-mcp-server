output "connection_id" {
  description = "BigQuery Connection ID"
  value       = google_bigquery_connection.spanner_connection.connection_id
}

output "connection_name" {
  description = "BigQuery Connection full resource name"
  value       = google_bigquery_connection.spanner_connection.name
}

output "service_account_id" {
  description = "Service account associated with the BigQuery Spanner connection"
  value       = google_bigquery_connection.spanner_connection.cloud_spanner[0].service_account_id
}
