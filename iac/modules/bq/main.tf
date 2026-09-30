resource "google_bigquery_dataset" "dataset" {
  dataset_id  = var.dataset_id
  project     = var.project_id
  location    = var.location
  description = "BigQuery dataset for Enterprise Agent Architecture Guidelines analytics and embeddings"
}

resource "google_bigquery_table" "guideline_embeddings" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "guideline_embeddings"
  project    = var.project_id

  schema = jsonencode([
    { name = "guideline_id", type = "STRING", mode = "REQUIRED" },
    { name = "title", type = "STRING", mode = "REQUIRED" },
    { name = "category", type = "STRING", mode = "NULLABLE" },
    { name = "chunk_index", type = "INTEGER", mode = "REQUIRED" },
    { name = "chunk_text", type = "STRING", mode = "REQUIRED" },
    { name = "embedding", type = "FLOAT64", mode = "REPEATED" },
    { name = "updated_at", type = "TIMESTAMP", mode = "REQUIRED" }
  ])

  deletion_protection = false
}

resource "google_bigquery_table" "mcp_query_audit_logs" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "mcp_query_audit_logs"
  project    = var.project_id

  schema = jsonencode([
    { name = "query_id", type = "STRING", mode = "REQUIRED" },
    { name = "client_id", type = "STRING", mode = "NULLABLE" },
    { name = "tool_name", type = "STRING", mode = "REQUIRED" },
    { name = "query_text", type = "STRING", mode = "NULLABLE" },
    { name = "latency_ms", type = "FLOAT64", mode = "REQUIRED" },
    { name = "timestamp", type = "TIMESTAMP", mode = "REQUIRED" }
  ])

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }

  deletion_protection = false
}
