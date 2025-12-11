# General Variables
variable "region" {
  description = "GCP region"
  type        = string
  nullable    = false
}

variable "zone" {
  description = "GCP zone"
  type        = string
  nullable    = false
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
  nullable    = false
}

# Artifact Registry
variable "repository_id" {
  description = "GCP Artifact Registry repository ID"
  type        = string
  nullable    = false
}

# GKE Cluster
variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  nullable    = false
}
variable "node_count" {
  description = "Number of nodes in the GKE cluster"
  type        = string
  nullable    = false
}
variable "machine_type" {
  description = "Machine type for the GKE nodes"
  type        = string
  nullable    = false
}