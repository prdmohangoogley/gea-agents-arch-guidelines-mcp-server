resource "google_bigquery_connection" "spanner_connection" {
  connection_id = var.connection_id
  project       = var.project_id
  location      = var.location
  friendly_name = "BigQuery to Spanner Graph Zero-ETL Federation"
  description   = "Federated query connection enabling BigQuery to query Spanner Graph directly without ETL via EXTERNAL_QUERY"

  cloud_spanner {
    database        = var.spanner_database_id
    use_parallelism = true
    use_data_boost  = var.use_data_boost
  }
}

# Grant BigQuery Connection service account Spanner database reader privileges
resource "google_spanner_database_iam_member" "bq_spanner_reader" {
  project  = var.project_id
  instance = var.spanner_instance_id
  database = var.spanner_database_name
  role     = "roles/spanner.databaseReader"
  member   = "serviceAccount:${google_bigquery_connection.spanner_connection.cloud_spanner[0].service_account_id}"
}
