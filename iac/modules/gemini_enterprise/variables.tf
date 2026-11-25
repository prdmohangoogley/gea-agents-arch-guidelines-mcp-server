variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "location" {
  description = "Discovery Engine / Gemini Enterprise location (global, us, or eu)"
  type        = string
  default     = "global"
}

variable "data_store_id" {
  description = "Discovery Engine data store ID for the OKF Architecture Guidelines corpus"
  type        = string
  default     = "geap-architecture-okf-ds"
}

variable "data_store_display_name" {
  description = "Display name for the OKF data store"
  type        = string
  default     = "GEA Architecture Best Practices OKF Data Store"
}

variable "engine_id" {
  description = "Gemini Enterprise (Agentspace) app / engine ID"
  type        = string
  default     = "geap-architecture-guidelines-app"
}

variable "engine_display_name" {
  description = "Display name for the Gemini Enterprise app"
  type        = string
  default     = "Enterprise Architecture Guidelines App"
}

variable "company_name" {
  description = "Organization / company display name for the Gemini Enterprise app"
  type        = string
  default     = "Enterprise Architecture"
}
