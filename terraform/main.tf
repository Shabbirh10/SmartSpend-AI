terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Google Cloud Run Service for Flask Backend
resource "google_cloud_run_v2_service" "backend" {
  name     = "smartspend-backend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.backend_image
      
      env {
        name  = "DATABASE_URL"
        value = "postgresql+asyncpg://${var.db_user}:${var.db_password}@${google_sql_database_instance.postgres.private_ip_address}/${google_sql_database.db.name}"
      }
      env {
        name  = "REDIS_URL"
        value = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
      }
      env {
        name  = "GEMINI_API_KEY"
        value = var.gemini_api_key
      }
      env {
        name  = "SECRET_KEY"
        value = var.secret_key
      }
      
      ports {
        container_port = 8000
      }
    }
  }
}

# Google Cloud Run Service for Next.js Frontend
resource "google_cloud_run_v2_service" "frontend" {
  name     = "smartspend-frontend"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    containers {
      image = var.frontend_image
      
      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = "${google_cloud_run_v2_service.backend.uri}/api"
      }
      
      ports {
        container_port = 3000
      }
    }
  }
}

# Allow public access to frontend
resource "google_cloud_run_v2_service_iam_member" "public_frontend" {
  name     = google_cloud_run_v2_service.frontend.name
  location = google_cloud_run_v2_service.frontend.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}

# Allow public access to backend API
resource "google_cloud_run_v2_service_iam_member" "public_backend" {
  name     = google_cloud_run_v2_service.backend.name
  location = google_cloud_run_v2_service.backend.location
  role     = "roles/run.viewer"
  member   = "allUsers"
}
