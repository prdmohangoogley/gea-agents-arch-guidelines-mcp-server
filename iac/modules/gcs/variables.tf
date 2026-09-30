variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "bucket_name" {
  description = "GCS bucket name for raw architectural guidelines and pipeline checkpoints"
  type        = string
}

variable "location" {
  description = "GCS bucket location"
  type        = string
  default     = "US"
}
