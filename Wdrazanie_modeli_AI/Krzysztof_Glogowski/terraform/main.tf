module "artifact_registry" {
  source        = "./modules/artifact_registry"
  project_id    = var.project_id
  region        = var.region
  repository_id = var.repository_id
}

module "gke" {
  source       = "./modules/gke"
  cluster_name = var.cluster_name
  machine_type = var.machine_type
  node_count   = var.node_count
  region       = var.zone
}