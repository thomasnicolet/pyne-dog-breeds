import json
import logging
import os
from datetime import date

import dlt
from dlt.sources.helpers import requests
from google.cloud import storage

logging.getLogger("dlt").setLevel(logging.WARNING)

DOG_API_KEY = os.environ["DOG_API_KEY"]
GCS_BUCKET = os.environ.get("GCS_BUCKET", "pyne-dog-breeds-488122-raw")


def fetch_breeds() -> list:
    response = requests.get(
        "https://api.thedogapi.com/v1/breeds",
        headers={"x-api-key": DOG_API_KEY},
    )
    response.raise_for_status()
    return response.json()


def write_to_gcs(data: list, bucket_name: str) -> None:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob_path = f"raw/{date.today().isoformat()}/breeds.json"
    blob = bucket.blob(blob_path)
    blob.upload_from_string(json.dumps(data), content_type="application/json")
    print(f"Written raw JSON to gs://{bucket_name}/{blob_path}")


@dlt.resource(name="dog_api_raw", write_disposition="replace")
def dog_api_raw(data: list):
    yield from data


if __name__ == "__main__":
    breeds = fetch_breeds()

    write_to_gcs(breeds, GCS_BUCKET)

    pipeline = dlt.pipeline(
        pipeline_name="dog_breeds",
        destination="bigquery",
        dataset_name="bronze",
    )
    load_info = pipeline.run(dog_api_raw(breeds))
    print(load_info)
