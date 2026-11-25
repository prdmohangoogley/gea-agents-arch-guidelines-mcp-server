terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.25"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.vertex_region
}

# 1. Enable Required GCP APIs (Zero Cloud Run)
resource "google_project_service" "required_apis" {
  for_each = toset([
    "spanner.googleapis.com",
    "bigquery.googleapis.com",
    "bigqueryconnection.googleapis.com",
    "aiplatform.googleapis.com",
    "dataplex.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com",
    "telemetry.googleapis.com",
    "cloudtrace.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "modelarmor.googleapis.com"
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}

# 2. Operational Layer: Cloud Spanner (Enterprise Edition with Spanner Graph)
module "spanner" {
  source           = "./modules/spanner"
  project_id       = var.project_id
  instance_id      = var.spanner_instance_id
  database_name    = var.spanner_database_name
  config           = var.spanner_config
  processing_units = var.spanner_processing_units
  edition          = var.spanner_edition

  depends_on = [google_project_service.required_apis]
}

# 3. Analytical Layer: BigQuery Dataset with Property Graph Overlays & Embeddings
module "bigquery" {
  source     = "./modules/bq"
  project_id = var.project_id
  dataset_id = var.bq_dataset_id
  location   = var.bq_location

  depends_on = [google_project_service.required_apis]
}

# 4. Federation Layer: Zero-ETL BigQuery to Spanner Graph Connection
module "federation" {
  source                = "./modules/federation"
  project_id            = var.project_id
  connection_id         = "spanner-graph-federation"
  location              = var.bq_location
  spanner_instance_id   = module.spanner.instance_id
  spanner_database_name = module.spanner.database_name
  spanner_database_id   = module.spanner.database_id
  use_data_boost        = true

  depends_on = [
    module.spanner,
    module.bigquery,
    google_project_service.required_apis
  ]
}

# 5. Storage Layer: GCS Bucket for Raw Guidelines & OKF Corpus
module "gcs" {
  source        = "./modules/gcs"
  project_id    = var.project_id
  bucket_name   = var.gcs_bucket_name
  location      = var.region
  create_bucket = var.create_gcs_bucket

  depends_on = [google_project_service.required_apis]
}

# 6. Runtime Layer: Vertex AI Reasoning Engine Staging Bucket & Dedicated Service Accounts (Zero Cloud Run)
resource "google_storage_bucket" "reasoning_engine_staging" {
  name                        = "${var.project_id}-reasoning-engine-staging"
  location                    = var.vertex_region
  project                     = var.project_id
  uniform_bucket_level_access = true

  depends_on = [google_project_service.required_apis]
}

resource "google_service_account" "reasoning_engine_sa" {
  account_id   = "arch-guidelines-re-sa"
  display_name = "Enterprise Architecture Guidelines Reasoning Engine SA"
  project      = var.project_id
}

resource "google_service_account" "okf_evolution_sa" {
  account_id   = "okf-evolution-agent-sa"
  display_name = "Autonomous OKF Evolution Reasoning Engine SA"
  project      = var.project_id
}

resource "google_project_iam_member" "reasoning_engine_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.reasoning_engine_sa.email}"
}

resource "google_project_iam_member" "okf_evolution_dataplex_editor" {
  project = var.project_id
  role    = "roles/dataplex.catalogEditor"
  member  = "serviceAccount:${google_service_account.okf_evolution_sa.email}"
}
