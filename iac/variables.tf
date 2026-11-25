variable "project_id" {
  description = "The Google Cloud Project ID (parameterized, do not hardcode)"
  type        = string
}

variable "region" {
  description = "Google Cloud multi-region location for BigQuery and Storage (e.g. US)"
  type        = string
  default     = "US"
}

variable "vertex_region" {
  description = "Google Cloud region for Vertex AI Reasoning Engine (e.g. us-central1)"
  type        = string
  default     = "us-central1"
}

variable "spanner_instance_id" {
  description = "Cloud Spanner instance ID"
  type        = string
  default     = "gea-arch-guidelines-spanner"
}

variable "spanner_config" {
  description = "Spanner configuration (e.g. nam3 for US multi-region or regional-us-central1)"
  type        = string
  default     = "nam3"
}

variable "spanner_database_name" {
  description = "Spanner database name with Property Graph enabled"
  type        = string
  default     = "arch_guidelines_graph"
}

variable "spanner_processing_units" {
  description = "Spanner compute processing units (100 for dev, 1000 = 1 node)"
  type        = number
  default     = 100
}

variable "spanner_edition" {
  description = "Spanner edition: STANDARD, ENTERPRISE, or ENTERPRISE_PLUS"
  type        = string
  default     = "ENTERPRISE"
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID for analytics and Graph overlays"
  type        = string
  default     = "gea_arch_guidelines_analytics"
}

variable "bq_location" {
  description = "BigQuery dataset location (US multi-region)"
  type        = string
  default     = "US"
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for raw architectural corpus and OKF checkpoints"
  type        = string
  default     = "gea_agent_development_architectural_best_practices_1790796607"
}

variable "create_gcs_bucket" {
  description = "Whether to create the GCS bucket (false if connecting to existing OKF bucket)"
  type        = bool
  default     = false
}

variable "reasoning_engine_display_name" {
  description = "Display name for Vertex AI Reasoning Engine deployment"
  type        = string
  default     = "gea-agents-arch-guidelines-mcp-server"
}
