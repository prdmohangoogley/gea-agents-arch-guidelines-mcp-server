resource "google_bigquery_dataset" "dataset" {
  dataset_id  = var.dataset_id
  project     = var.project_id
  location    = var.location
  description = "BigQuery dataset for Enterprise Agent Architecture Guidelines analytics, vector embeddings, and Property Graph overlays"
}

# Node Table: Guidelines
resource "google_bigquery_table" "guidelines" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "guidelines"
  project    = var.project_id

  schema = jsonencode([
    { name = "guideline_id", type = "STRING", mode = "REQUIRED", description = "Unique guideline ID" },
    { name = "title", type = "STRING", mode = "REQUIRED", description = "Guideline title" },
    { name = "category", type = "STRING", mode = "REQUIRED", description = "Domain category" },
    { name = "summary", type = "STRING", mode = "NULLABLE", description = "Executive summary" },
    { name = "source_url", type = "STRING", mode = "NULLABLE", description = "Documentation reference" },
    { name = "created_at", type = "TIMESTAMP", mode = "REQUIRED", description = "Creation timestamp" }
  ])

  deletion_protection = false
}

# Node Table: Patterns
resource "google_bigquery_table" "patterns" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "patterns"
  project    = var.project_id

  schema = jsonencode([
    { name = "pattern_id", type = "STRING", mode = "REQUIRED", description = "Pattern ID" },
    { name = "name", type = "STRING", mode = "REQUIRED", description = "Pattern name" },
    { name = "category", type = "STRING", mode = "REQUIRED", description = "Domain category" },
    { name = "description", type = "STRING", mode = "NULLABLE", description = "Pattern details" },
    { name = "created_at", type = "TIMESTAMP", mode = "REQUIRED", description = "Creation timestamp" }
  ])

  deletion_protection = false
}

# Node Table: Antipatterns
resource "google_bigquery_table" "antipatterns" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "antipatterns"
  project    = var.project_id

  schema = jsonencode([
    { name = "antipattern_id", type = "STRING", mode = "REQUIRED", description = "Antipattern ID" },
    { name = "name", type = "STRING", mode = "REQUIRED", description = "Antipattern name" },
    { name = "hazard", type = "STRING", mode = "REQUIRED", description = "Risk or hazard description" },
    { name = "remedy", type = "STRING", mode = "NULLABLE", description = "Mitigation remedy" },
    { name = "created_at", type = "TIMESTAMP", mode = "REQUIRED", description = "Creation timestamp" }
  ])

  deletion_protection = false
}

# Node Table: Tradeoffs
resource "google_bigquery_table" "tradeoffs" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "tradeoffs"
  project    = var.project_id

  schema = jsonencode([
    { name = "tradeoff_id", type = "STRING", mode = "REQUIRED", description = "Tradeoff ID" },
    { name = "dimension", type = "STRING", mode = "REQUIRED", description = "Tradeoff dimension" },
    { name = "option_a", type = "STRING", mode = "REQUIRED", description = "First option" },
    { name = "option_b", type = "STRING", mode = "REQUIRED", description = "Second option" },
    { name = "analysis", type = "STRING", mode = "NULLABLE", description = "Comparative analysis" },
    { name = "created_at", type = "TIMESTAMP", mode = "REQUIRED", description = "Creation timestamp" }
  ])

  deletion_protection = false
}

# Edge Table: PatternMitigatesAntipattern
resource "google_bigquery_table" "pattern_mitigates_antipattern" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "pattern_mitigates_antipattern"
  project    = var.project_id

  schema = jsonencode([
    { name = "pattern_id", type = "STRING", mode = "REQUIRED", description = "Source pattern ID" },
    { name = "antipattern_id", type = "STRING", mode = "REQUIRED", description = "Target antipattern ID" },
    { name = "rationale", type = "STRING", mode = "NULLABLE", description = "Mitigation rationale" }
  ])

  deletion_protection = false
}

# Edge Table: GuidelineImplementsPattern
resource "google_bigquery_table" "guideline_implements_pattern" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "guideline_implements_pattern"
  project    = var.project_id

  schema = jsonencode([
    { name = "guideline_id", type = "STRING", mode = "REQUIRED", description = "Source guideline ID" },
    { name = "pattern_id", type = "STRING", mode = "REQUIRED", description = "Target pattern ID" },
    { name = "notes", type = "STRING", mode = "NULLABLE", description = "Implementation notes" }
  ])

  deletion_protection = false
}

# Vector Embeddings for Hybrid GraphRAG
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

# Audit Logs for FastMCP Query Observability
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

# BigQuery Stored Procedure to initialize the Property Graph Overlay
resource "google_bigquery_routine" "init_property_graph_overlay" {
  dataset_id   = google_bigquery_dataset.dataset.dataset_id
  routine_id   = "init_property_graph_overlay"
  routine_type = "PROCEDURE"
  language     = "SQL"
  project      = var.project_id

  definition_body = <<-EOT
    EXECUTE IMMEDIATE """
    CREATE OR REPLACE PROPERTY GRAPH `${var.project_id}.${var.dataset_id}.ArchGuidelinesAnalyticalGraph`
      NODE TABLES (
        `${var.project_id}.${var.dataset_id}.guidelines`
          LABEL Guideline
          PROPERTIES (guideline_id, title, category, summary),
        `${var.project_id}.${var.dataset_id}.patterns`
          LABEL Pattern
          PROPERTIES (pattern_id, name, category, description),
        `${var.project_id}.${var.dataset_id}.antipatterns`
          LABEL Antipattern
          PROPERTIES (antipattern_id, name, hazard, remedy),
        `${var.project_id}.${var.dataset_id}.tradeoffs`
          LABEL Tradeoff
          PROPERTIES (tradeoff_id, dimension, option_a, option_b, analysis)
      )
      EDGE TABLES (
        `${var.project_id}.${var.dataset_id}.pattern_mitigates_antipattern`
          SOURCE KEY (pattern_id) REFERENCES `${var.project_id}.${var.dataset_id}.patterns` (pattern_id)
          DESTINATION KEY (antipattern_id) REFERENCES `${var.project_id}.${var.dataset_id}.antipatterns` (antipattern_id)
          LABEL MITIGATES
          PROPERTIES (rationale),
        `${var.project_id}.${var.dataset_id}.guideline_implements_pattern`
          SOURCE KEY (guideline_id) REFERENCES `${var.project_id}.${var.dataset_id}.guidelines` (guideline_id)
          DESTINATION KEY (pattern_id) REFERENCES `${var.project_id}.${var.dataset_id}.patterns` (pattern_id)
          LABEL IMPLEMENTS
          PROPERTIES (notes)
      )
    """;
  EOT

  depends_on = [
    google_bigquery_table.guidelines,
    google_bigquery_table.patterns,
    google_bigquery_table.antipatterns,
    google_bigquery_table.tradeoffs,
    google_bigquery_table.pattern_mitigates_antipattern,
    google_bigquery_table.guideline_implements_pattern
  ]
}
