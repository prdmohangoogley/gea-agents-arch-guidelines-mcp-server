# Dedicated Service Account for FastMCP Server Runtime
resource "google_service_account" "mcp_runner" {
  account_id   = "mcp-server-runner"
  display_name = "FastMCP Architectural Guidelines Server Runner"
  description  = "Least-privilege runtime identity for FastMCP Cloud Run service"
  project      = var.project_id
}

# IAM: Spanner Database User
resource "google_spanner_database_iam_member" "spanner_user" {
  project  = var.project_id
  instance = var.spanner_instance_id
  database = var.spanner_database_name
  role     = "roles/spanner.databaseUser"
  member   = "serviceAccount:${google_service_account.mcp_runner.email}"
}

# IAM: BigQuery Data Viewer on dataset
resource "google_bigquery_dataset_iam_member" "bq_viewer" {
  project    = var.project_id
  dataset_id = var.bq_dataset_id
  role       = "roles/bigquery.dataViewer"
  member     = "serviceAccount:${google_service_account.mcp_runner.email}"
}

# IAM: BigQuery Job User on project (required to execute analytical queries)
resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.mcp_runner.email}"
}

# IAM: GCS Object Viewer on corpus bucket
resource "google_storage_bucket_iam_member" "gcs_viewer" {
  bucket = var.gcs_bucket_name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.mcp_runner.email}"
}

# IAM: Cloud Trace Agent (Required to push spans to Cloud Trace)
resource "google_project_iam_member" "trace_agent" {
  project = var.project_id
  role    = "roles/cloudtrace.agent"
  member  = "serviceAccount:${google_service_account.mcp_runner.email}"
}

# IAM: Telemetry Writer (Required for OpenTelemetry ingestion endpoint)
resource "google_project_iam_member" "telemetry_writer" {
  project = var.project_id
  role    = "roles/telemetry.writer"
  member  = "serviceAccount:${google_service_account.mcp_runner.email}"
}

# IAM: Monitoring Metric Writer (Required for metrics pushing)
resource "google_project_iam_member" "metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.mcp_runner.email}"
}

# Cloud Run v2 Service Definition
resource "google_cloud_run_v2_service" "mcp_server" {
  name     = var.service_name
  location = var.region
  project  = var.project_id
  ingress  = var.ingress

  template {
    service_account = google_service_account.mcp_runner.email

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    containers {
      image = var.container_image

      ports {
        container_port = 8080
      }

      env {
        name  = "MCP_TRANSPORT"
        value = "sse"
      }
      env {
        name  = "MCP_HOST"
        value = "0.0.0.0"
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "SPANNER_INSTANCE"
        value = var.spanner_instance_id
      }
      env {
        name  = "SPANNER_DATABASE"
        value = var.spanner_database_name
      }
      env {
        name  = "BQ_DATASET"
        value = var.bq_dataset_id
      }
      env {
        name  = "GCS_BUCKET"
        value = var.gcs_bucket_name
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }
  }

  depends_on = [
    google_spanner_database_iam_member.spanner_user,
    google_bigquery_dataset_iam_member.bq_viewer,
    google_project_iam_member.bq_job_user,
    google_storage_bucket_iam_member.gcs_viewer
  ]
}

# Optional unauthenticated invoker binding (if enabled)
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.mcp_server.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
