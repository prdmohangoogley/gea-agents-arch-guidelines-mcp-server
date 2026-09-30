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
  region  = var.region
}

module "spanner" {
  source           = "./modules/spanner"
  project_id       = var.project_id
  instance_id      = var.spanner_instance_id
  database_name    = var.spanner_database_name
  config           = "regional-${var.region}"
  processing_units = 100
}

module "bigquery" {
  source     = "./modules/bq"
  project_id = var.project_id
  dataset_id = var.bq_dataset_id
  location   = "US"
}

module "gcs" {
  source      = "./modules/gcs"
  project_id  = var.project_id
  bucket_name = var.gcs_bucket_name
  location    = "US"
}
