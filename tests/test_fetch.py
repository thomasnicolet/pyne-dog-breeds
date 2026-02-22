import logging
import os
import time
from collections import Counter

import requests

logger = logging.getLogger(__name__)

API_KEY = os.environ["DOG_API_KEY"]
BASE_URL = "https://api.thedogapi.com/v1"


def test_breeds_endpoint_returns_data():
    logger.info("Fetching breeds from Dog API...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/breeds", headers={"x-api-key": API_KEY})
    elapsed = time.time() - start

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    breeds = response.json()
    assert isinstance(breeds, list)
    assert len(breeds) > 0

    groups = Counter(b.get("breed_group") or "Unknown" for b in breeds)
    missing_lifespan = sum(1 for b in breeds if not b.get("life_span"))
    missing_weight = sum(1 for b in breeds if not b.get("weight", {}).get("metric"))

    rows = [
        ("Metric",            "Value"),
        ("─" * 22,            "─" * 20),
        ("Status",            f"{response.status_code} in {elapsed:.2f}s"),
        ("Total breeds",      str(len(breeds))),
        ("Missing life span", str(missing_lifespan)),
        ("Missing weight",    str(missing_weight)),
        ("─" * 22,            "─" * 20),
        ("Breed group",       "Count"),
        ("─" * 22,            "─" * 20),
    ] + [(g, str(c)) for g, c in groups.most_common()]

    col1 = max(len(r[0]) for r in rows)
    lines = "\n".join(f"  {r[0]:<{col1}}  {r[1]}" for r in rows)
    logger.info(f"\n\n{lines}\n")
