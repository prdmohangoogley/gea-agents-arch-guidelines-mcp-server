output "instance_id" {
  description = "Spanner instance ID"
  value       = google_spanner_instance.instance.name
}

output "database_name" {
  description = "Spanner database name"
  value       = google_spanner_database.database.name
}

output "graph_name" {
  description = "Spanner property graph name"
  value       = "ArchGuidelinesGraph"
}
