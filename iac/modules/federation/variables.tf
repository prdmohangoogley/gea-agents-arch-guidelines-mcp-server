variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "connection_id" {
  description = "BigQuery Connection ID for Spanner Federation"
  type        = string
  default     = "spanner-graph-federation"
}

variable "location" {
  description = "BigQuery connection location (e.g. US)"
  type        = string
  default     = "US"
}

variable "spanner_instance_id" {
  description = "Spanner instance ID"
  type        = string
}

variable "spanner_database_name" {
  description = "Spanner database name"
  type        = string
}

variable "spanner_database_id" {
  description = "Full Spanner database ID (projects/.../instances/.../databases/...)"
  type        = string
}

variable "use_data_boost" {
  description = "Whether to use Spanner Data Boost for serverless independent compute (Enterprise Edition)"
  type        = bool
  default     = true
}
