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
  region  = var.cloud_run_region
}

# 1. Enable Required GCP APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "spanner.googleapis.com",
    "bigquery.googleapis.com",
    "bigqueryconnection.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com"
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
  source      = "./modules/gcs"
  project_id  = var.project_id
  bucket_name = var.gcs_bucket_name
  location    = var.region

  depends_on = [google_project_service.required_apis]
}

# 6. Runtime Layer: FastMCP Server on Cloud Run
module "cloud_run" {
  source                = "./modules/cloud_run"
  project_id            = var.project_id
  service_name          = var.cloud_run_service_name
  region                = var.cloud_run_region
  container_image       = var.cloud_run_container_image
  spanner_instance_id   = module.spanner.instance_id
  spanner_database_name = module.spanner.database_name
  bq_dataset_id         = module.bigquery.dataset_id
  gcs_bucket_name       = module.gcs.bucket_name
  allow_unauthenticated = false

  depends_on = [
    module.spanner,
    module.bigquery,
    module.gcs,
    google_project_service.required_apis
  ]
}
