terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# --- BigQuery Datasets ---

resource "google_bigquery_dataset" "bronze" {
  dataset_id  = "bronze"
  description = "Raw data loaded by dlt"
  location    = var.region
}

resource "google_bigquery_dataset" "dev_staging" {
  dataset_id  = "dev_staging"
  description = "dbt staging models (dev)"
  location    = var.region
}

resource "google_bigquery_dataset" "dev_marts" {
  dataset_id  = "dev_marts"
  description = "dbt mart models (dev)"
  location    = var.region
}

resource "google_bigquery_dataset" "prod_staging" {
  dataset_id  = "prod_staging"
  description = "dbt staging models (prod)"
  location    = var.region
}

resource "google_bigquery_dataset" "prod_marts" {
  dataset_id  = "prod_marts"
  description = "dbt mart models (prod)"
  location    = var.region
}

# --- Cloud Storage bucket for raw JSON ---

resource "google_storage_bucket" "raw" {
  name                        = "${var.project_id}-raw"
  location                    = var.region
  uniform_bucket_level_access = true

  lifecycle_rule {
    action { type = "Delete" }
    condition { age = 90 }
  }
}

# --- Service Account ---

resource "google_service_account" "pipeline" {
  account_id   = "pipeline-sa"
  display_name = "Pipeline Service Account"
}

# --- IAM (least-privilege) ---

resource "google_project_iam_member" "bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_project_iam_member" "bq_data_editor" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}

resource "google_project_iam_member" "storage_object_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.pipeline.email}"
}
