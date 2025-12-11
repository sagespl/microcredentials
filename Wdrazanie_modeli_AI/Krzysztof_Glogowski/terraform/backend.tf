terraform {
  backend "gcs" {
    bucket = "document-classification-terraform-state"
  }
}