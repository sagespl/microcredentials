variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  nullable    = false
}

variable "machine_type" {
  description = "Machine type for the GKE nodes"
  type        = string
  nullable    = false
}

variable "node_count" {
  description = "Number of nodes in the GKE cluster"
  type        = string
  nullable    = false
}

variable "region" {
  description = "GCP region"
  type        = string
  nullable    = false
}

