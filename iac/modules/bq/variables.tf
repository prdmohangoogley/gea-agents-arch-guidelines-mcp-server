variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "dataset_id" {
  description = "BigQuery dataset ID"
  type        = string
  default     = "gea_arch_guidelines_analytics"
}

variable "location" {
  description = "BigQuery dataset location (e.g. US or region)"
  type        = string
  default     = "US"
}
