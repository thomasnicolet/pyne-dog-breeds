output "service_account_email" {
  description = "Pipeline service account email"
  value       = google_service_account.pipeline.email
}

output "raw_bucket_name" {
  description = "Cloud Storage bucket for raw JSON"
  value       = google_storage_bucket.raw.name
}
