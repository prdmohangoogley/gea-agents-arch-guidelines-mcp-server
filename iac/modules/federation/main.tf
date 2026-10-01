data "google_project" "project" {
  project_id = var.project_id
}

resource "google_bigquery_connection" "spanner_connection" {
  connection_id = var.connection_id
  project       = var.project_id
  location      = var.location
  friendly_name = "BigQuery to Spanner Graph Zero-ETL Federation"
  description   = "Federated query connection enabling BigQuery to query Spanner Graph directly without ETL via EXTERNAL_QUERY"

  cloud_spanner {
    database        = "projects/${var.project_id}/instances/${var.spanner_instance_id}/databases/${var.spanner_database_name}"
    use_parallelism = true
    use_data_boost  = var.use_data_boost
  }
}
