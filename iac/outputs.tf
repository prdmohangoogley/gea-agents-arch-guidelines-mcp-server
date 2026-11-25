output "spanner_instance" {
  description = "Cloud Spanner instance name"
  value       = module.spanner.instance_id
}

output "spanner_database" {
  description = "Cloud Spanner database name"
  value       = module.spanner.database_name
}

output "spanner_graph" {
  description = "Cloud Spanner property graph name"
  value       = module.spanner.graph_name
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID"
  value       = module.bigquery.dataset_id
}

output "bigquery_spanner_connection" {
  description = "BigQuery to Spanner Zero-ETL federation connection ID"
  value       = module.federation.connection_id
}

output "gcs_bucket" {
  description = "GCS bucket name for raw corpus"
  value       = module.gcs.bucket_name
}

output "reasoning_engine_staging_bucket" {
  description = "Vertex AI Reasoning Engine staging bucket"
  value       = google_storage_bucket.reasoning_engine_staging.name
}

output "reasoning_engine_service_account" {
  description = "Primary Reasoning Engine runtime service account"
  value       = google_service_account.reasoning_engine_sa.email
}

output "okf_evolution_service_account" {
  description = "Autonomous OKF Evolution Reasoning Engine service account"
  value       = google_service_account.okf_evolution_sa.email
}
