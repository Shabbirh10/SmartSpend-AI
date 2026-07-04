# Google Cloud SQL (PostgreSQL) Instance
resource "google_sql_database_instance" "postgres" {
  name             = "smartspend-postgres"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = "db-f1-micro" # Small/cheap tier for portfolio demonstration
    
    ip_configuration {
      ipv4_enabled    = true
      private_network = var.vpc_network_id
    }
  }
  
  deletion_protection = false
}

# Database definition
resource "google_sql_database" "db" {
  name     = "smartspend"
  instance = google_sql_database_instance.postgres.name
}

# Database User
resource "google_sql_user" "db_user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Google Cloud Memorystore (Redis) for Caching and Celery broker
resource "google_redis_instance" "cache" {
  name           = "smartspend-redis"
  tier           = "BASIC"
  memory_size_gb = 1
  region         = var.region
  
  authorized_network = var.vpc_network_id

  redis_version = "REDIS_6_X"
  display_name  = "SmartSpend AI Redis Cache"
}
