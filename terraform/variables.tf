variable "project_id" {
  type        = string
  description = "The Google Cloud Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "The region to deploy services into"
}

variable "vpc_network_id" {
  type        = string
  description = "The VPC network ID to bind Cloud SQL and Memorystore"
}

variable "backend_image" {
  type        = string
  description = "The GCR/GAR Docker container image path for the backend"
}

variable "frontend_image" {
  type        = string
  description = "The GCR/GAR Docker container image path for the frontend"
}

variable "db_user" {
  type        = string
  default     = "smartspend_admin"
  description = "Postgres database admin username"
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "Postgres database admin password"
}

variable "gemini_api_key" {
  type        = string
  sensitive   = true
  description = "The Google Gemini API Key"
}

variable "secret_key" {
  type        = string
  default     = "super-secret-key-change-in-production"
  description = "Flask app secret key"
}
