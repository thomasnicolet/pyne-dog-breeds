# Pyne Dog Breed Explorer

**GCP Project ID:** `pyne-dog-breeds-488122`
**Repo:** https://github.com/thomasnicolet/pyne-dog-breeds

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

## Findings

Dog breed data reveals a clear inverse relationship between size and longevity: small breeds (≤20 lbs) average 13–15 years while large breeds (>60 lbs) average 8–10 years. Toy and Terrier groups dominate the small/long-lived segment. For a product like a breed recommendation engine, size class and life span are the two highest-signal attributes for matching breeds to owner lifestyle — a family expecting a 15-year commitment makes a very different choice than one open to a 8-year one.

---

[![Pipeline](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/pipeline.yml/badge.svg)](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/pipeline.yml)
[![CI](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/ci.yml/badge.svg)](https://github.com/thomasnicolet/pyne-dog-breeds/actions/workflows/ci.yml)
