resource "google_container_cluster" "gke" {
  description        = "Google Kubernetes Engine cluster"
  name               = var.cluster_name
  location           = var.region
  initial_node_count = var.node_count

  node_config {
    machine_type = var.machine_type
  }
}