output "data_store_id" {
  description = "Discovery Engine Data Store ID"
  value       = google_discovery_engine_data_store.okf_datastore.data_store_id
}

output "data_store_name" {
  description = "Full resource name of the Discovery Engine Data Store"
  value       = google_discovery_engine_data_store.okf_datastore.name
}

output "engine_id" {
  description = "Gemini Enterprise App / Engine ID"
  value       = google_discovery_engine_search_engine.gemini_enterprise_app.engine_id
}

output "engine_name" {
  description = "Full resource name of the Gemini Enterprise App"
  value       = google_discovery_engine_search_engine.gemini_enterprise_app.name
}
