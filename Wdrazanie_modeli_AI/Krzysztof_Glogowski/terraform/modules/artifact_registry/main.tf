resource "google_artifact_registry_repository" "repo" {
  description   = "Artifact Registry for Docker images"
  format        = "DOCKER"
  location      = var.region
  repository_id = var.repository_id
}