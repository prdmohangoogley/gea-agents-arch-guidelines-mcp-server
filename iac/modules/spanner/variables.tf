variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "instance_id" {
  description = "Spanner instance ID"
  type        = string
  default     = "gea-arch-guidelines-spanner"
}

variable "config" {
  description = "Spanner configuration (region)"
  type        = string
  default     = "regional-us-central1"
}

variable "display_name" {
  description = "Spanner instance display name"
  type        = string
  default     = "Enterprise Agents Architectural Guidelines Spanner"
}

variable "processing_units" {
  description = "Spanner processing units"
  type        = number
  default     = 100
}

variable "database_name" {
  description = "Spanner database name"
  type        = string
  default     = "arch_guidelines_graph"
}
