variable "project_id" {
  description = "GCP project ID"
  type        = string
  default     = "pyne-dog-breeds-488122"
}

variable "region" {
  description = "GCP region / BigQuery location"
  type        = string
  default     = "EU"
}
