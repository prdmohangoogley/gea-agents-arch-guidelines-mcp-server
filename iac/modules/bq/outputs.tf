output "dataset_id" {
  description = "BigQuery dataset ID"
  value       = google_bigquery_dataset.dataset.dataset_id
}

output "embeddings_table_id" {
  description = "BigQuery embeddings table ID"
  value       = google_bigquery_table.guideline_embeddings.table_id
}

output "audit_logs_table_id" {
  description = "BigQuery audit logs table ID"
  value       = google_bigquery_table.mcp_query_audit_logs.table_id
}

output "graph_overlay_routine_id" {
  description = "Routine ID to initialize BigQuery property graph overlay"
  value       = google_bigquery_routine.init_property_graph_overlay.routine_id
}
