# Pyne Dog Breed Explorer

**GCP Project ID:** `pyne-dog-breeds-488122`

**Repo:** https://github.com/thomasnicolet/pyne-dog-breeds

**dbt Docs:** https://thomasnicolet.github.io/pyne-dog-breeds

**Dashboard:** https://lookerstudio.google.com/reporting/00c5a63b-aee8-4415-b4df-fc4070d95ba6

End-to-end data pipeline ingesting dog breed data from the [Dog API](https://thedogapi.com), transforming it with dbt, and exposing analytics via Looker Studio.

## Architecture

```
GitHub Actions (cron 02:00 UTC)
        │
        ▼
  dlt pipeline  ──► GCS: raw/YYYY-MM-DD/breeds.json
  (ingestion/)  └──────────────────────────► BigQuery: bronze.dog_api_raw
  (ingestion/)                                        │
                                                      ▼
                                             dbt staging models
                                             (dev_staging / prod_staging)
                                                      │
                                                      ▼
                                             dbt mart models
                                             (dev_marts / prod_marts)
                                                      │
                                                      ▼
                                             Looker Studio dashboard
```

**Substitution note:** Cloud Scheduler + Cloud Run are replaced by a GitHub Actions scheduled workflow. Same outcome (daily run at 02:00 UTC), simpler secrets management, fully auditable. In production, the runner would move to Cloud Run Jobs with Cloud Scheduler as the trigger.

## Stack

| Layer | Tool |
|---|---|
| Ingestion | dlt (Data Load Tool) |
| Storage | BigQuery + Cloud Storage (raw JSON) |
| Transformation | dbt Core + BigQuery adapter |
| Orchestration | GitHub Actions (cron) |
| CI/CD | GitHub Actions |
| Visualisation | Looker Studio |
| IaC | Terraform |

## Bootstrap

### Prerequisites
- GCP project with billing enabled
- `gcloud` CLI authenticated (`gcloud auth login`)
- `terraform` installed
- `uv` installed

### 1. GCP infrastructure

```bash
cd terraform
terraform init
terraform apply
```

Copy the `service_account_email` from the output.

### 2. Generate service account key

```bash
gcloud iam service-accounts keys create sa-key.json \
  --iam-account=pipeline-sa@pyne-dog-breeds-488122.iam.gserviceaccount.com
```

Add the contents of `sa-key.json` as a GitHub Actions secret named `GCP_SA_KEY`. Delete the local file after.

**Dog API key:** The [Dog API](https://thedogapi.com) requires an API key (free tier available). Add it as a GitHub Actions secret named `DOG_API_KEY` so the scheduled pipeline can run. For local runs, set `export DOG_API_KEY=your-key`.

### 3. Local development

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -e .
```

Authenticate for local dbt/dlt runs:

```bash
gcloud auth application-default login
```

Run the pipeline locally (set `DOG_API_KEY` first; get a key at https://thedogapi.com):

```bash
export DOG_API_KEY=your-key
python ingestion/pipeline.py
```

Run dbt:

```bash
cd dbt
dbt deps --profiles-dir .
dbt run --target dev --profiles-dir .
dbt test --target dev --profiles-dir .
```

### 4. CI/CD

Two workflows:

- **ci.yml** — runs `dbt run + dbt test` on every PR against dev datasets
- **pipeline.yml** — runs daily at 02:00 UTC and on every merge to `main`; runs dlt then dbt against prod datasets

## Data Model

```
bronze.dog_api_raw     (raw, loaded by dlt)
        │
        ▼
stg_breeds             (typed, parsed life_span and weight strings)
        │
        ├──► dim_breed             (breed dimension + size_class)
        └──► fact_weight_life_span (analytics-ready fact table)
```

## Findings & Business Impact

The data confirms a clear inverse relationship between size and longevity: small breeds (≤20 lbs) average 13–15 years, large breeds (>60 lbs) average 8–10 years. The Working and Herding groups dominate by count; Toy and Terrier breeds cluster at the high end of life span. About 40% of breeds have incomplete life span data — worth flagging before any downstream product decision relies on it.

That said, the most important thing I would do with this API, is go over with business what we are trying to solve. Since dog breeds are fairly static, they likely do not need a pipeline, and it is likely more sources than this API is required. Exploring dog breeds can be done with a single Python script, iterating on what is actually needed from there.

This could be expanded, e.g. with an additional model, temperament traits could be unnested and counted, to filter by characteristics like "good with children" or "low energy". Image URLs are also available in the raw data, unused for now.

The architecture is deliberately simple: replace GitHub Actions cron with Cloud Run Jobs and add a proper orchestrator (Airflow, Dagster) when the pipeline count grows beyond one. The dbt lineage and test coverage make that migration low-risk.

---

[![Pipeline](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/pipeline.yml/badge.svg)](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/pipeline.yml)
[![CI](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/ci.yml/badge.svg)](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/ci.yml)
