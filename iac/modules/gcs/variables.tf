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

variable "create_bucket" {
  description = "Whether to create the GCS bucket or bind to an existing bucket"
  type        = bool
  default     = false
}
