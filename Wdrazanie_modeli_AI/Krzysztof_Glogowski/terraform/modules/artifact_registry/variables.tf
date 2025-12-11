variable "region" {
  description = "GCP region"
  type        = string
  nullable    = false
}

variable "repository_id" {
  description = "GCP Artifact Registry repository ID"
  type        = string
  nullable    = false
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
  nullable    = false
}