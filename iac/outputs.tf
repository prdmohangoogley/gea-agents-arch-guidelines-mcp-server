output "spanner_instance" {
  description = "Spanner instance name"
  value       = module.spanner.instance_id
}

output "spanner_database" {
  description = "Spanner database name"
  value       = module.spanner.database_name
}

output "spanner_graph" {
  description = "Spanner property graph name"
  value       = module.spanner.graph_name
}

output "bigquery_dataset" {
  description = "BigQuery dataset ID"
  value       = module.bigquery.dataset_id
}

output "gcs_bucket" {
  description = "GCS bucket name"
  value       = module.gcs.bucket_name
}
