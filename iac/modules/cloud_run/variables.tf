variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "service_name" {
  description = "Cloud Run service name for FastMCP server"
  type        = string
  default     = "gea-agents-arch-guidelines-mcp-server"
}

variable "region" {
  description = "Cloud Run deployment region"
  type        = string
  default     = "us-central1"
}

variable "container_image" {
  description = "Container image URI for MCP server (placeholder default)"
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "ingress" {
  description = "Cloud Run ingress traffic setting conforming to org policies"
  type        = string
  default     = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"
}

variable "spanner_instance_id" {
  description = "Spanner instance ID"
  type        = string
}

variable "spanner_database_name" {
  description = "Spanner database name"
  type        = string
}

variable "bq_dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
}

variable "gcs_bucket_name" {
  description = "GCS bucket name for architectural corpus"
  type        = string
}

variable "allow_unauthenticated" {
  description = "Whether to allow unauthenticated invocations (recommended false for enterprise ZAA)"
  type        = bool
  default     = false
}
