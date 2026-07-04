output "frontend_url" {
  value       = google_cloud_run_v2_service.frontend.uri
  description = "The public URL of the SmartSpend AI frontend application"
}

output "backend_url" {
  value       = google_cloud_run_v2_service.backend.uri
  description = "The public URL of the SmartSpend AI backend API service"
}

output "redis_host" {
  value       = google_redis_instance.cache.host
  description = "IP address of the Cloud Memorystore Redis instance"
}
