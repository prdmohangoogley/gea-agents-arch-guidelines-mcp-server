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

output "bigquery_federation_sa" {
  description = "BigQuery Connection service account with Spanner reader permissions"
  value       = module.federation.service_account_id
}

output "gcs_bucket" {
  description = "GCS bucket name for raw corpus"
  value       = module.gcs.bucket_name
}

output "cloud_run_service" {
  description = "Cloud Run FastMCP service name"
  value       = module.cloud_run.service_name
}

output "cloud_run_service_uri" {
  description = "Cloud Run FastMCP service URI"
  value       = module.cloud_run.service_uri
}

output "cloud_run_service_account" {
  description = "FastMCP runtime service account"
  value       = module.cloud_run.service_account_email
}
