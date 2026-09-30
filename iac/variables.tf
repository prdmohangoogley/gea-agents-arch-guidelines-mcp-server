variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud region for resources"
  type        = string
  default     = "us-central1"
}

variable "spanner_instance_id" {
  description = "Spanner instance ID"
  type        = string
  default     = "gea-arch-guidelines-spanner"
}

variable "spanner_database_name" {
  description = "Spanner database name"
  type        = string
  default     = "arch_guidelines_graph"
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "gea_arch_guidelines_analytics"
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for raw guidelines & pipeline artifacts"
  type        = string
}
