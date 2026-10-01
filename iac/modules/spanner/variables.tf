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
  description = "Spanner configuration (region/multi-region)"
  type        = string
  default     = "nam3"
}

variable "display_name" {
  description = "Spanner instance display name"
  type        = string
  default     = "Enterprise Agents Architectural Guidelines Spanner"
}

variable "processing_units" {
  description = "Spanner processing units (min 100 for dev, 1000 = 1 node)"
  type        = number
  default     = 100
}

variable "edition" {
  description = "Spanner edition: STANDARD, ENTERPRISE, or ENTERPRISE_PLUS"
  type        = string
  default     = "ENTERPRISE"
}

variable "database_name" {
  description = "Spanner database name"
  type        = string
  default     = "arch_guidelines_graph"
}
