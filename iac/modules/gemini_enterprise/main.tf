resource "google_discovery_engine_data_store" "okf_datastore" {
  project                     = var.project_id
  location                    = var.location
  data_store_id               = var.data_store_id
  display_name                = var.data_store_display_name
  industry_vertical           = "GENERIC"
  content_config              = "CONTENT_REQUIRED"
  solution_types              = ["SOLUTION_TYPE_SEARCH"]
  create_advanced_site_search = false
}

resource "google_discovery_engine_search_engine" "gemini_enterprise_app" {
  project           = var.project_id
  engine_id         = var.engine_id
  collection_id     = "default_collection"
  location          = var.location
  display_name      = var.engine_display_name
  data_store_ids    = [google_discovery_engine_data_store.okf_datastore.data_store_id]
  industry_vertical = "GENERIC"

  search_engine_config {
    search_tier    = "SEARCH_TIER_ENTERPRISE"
    search_add_ons = ["SEARCH_ADD_ON_LLM"]
  }

  common_config {
    company_name = var.company_name
  }
}
