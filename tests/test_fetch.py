import logging
import os
import re
import time
from collections import Counter

import requests

logger = logging.getLogger(__name__)

API_KEY = os.environ["DOG_API_KEY"]
BASE_URL = "https://api.thedogapi.com/v1"


def _avg_life_years(life_span: str | None) -> float | None:
    """Parse '10 - 12 years' -> 11.0; '8 years' -> 8.0."""
    if not life_span or not life_span.strip():
        return None
    nums = [int(m) for m in re.findall(r"\d+", life_span)]
    if not nums:
        return None
    return (min(nums) + max(nums)) / 2.0


def test_breeds_endpoint_returns_data():
    logger.info("Fetching breeds from Dog API...")
    start = time.time()
    response = requests.get(f"{BASE_URL}/breeds", headers={"x-api-key": API_KEY})
    elapsed = time.time() - start

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    breeds = response.json()
    assert isinstance(breeds, list)
    assert len(breeds) > 0

    # Test transform: avg lifespan per breed (parse "10 - 12 years" -> 11.0)
    breed_avg_lifespan = [
        (b.get("name") or "Unknown", _avg_life_years(b.get("life_span")))
        for b in breeds
    ]
    breed_avg_lifespan = [(name, yrs) for name, yrs in breed_avg_lifespan if yrs is not None]
    breed_avg_lifespan.sort(key=lambda x: -x[1])  # longest first

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

    # Avg lifespan per breed (test transform), longest first
    lifespan_rows = [("Breed", "Avg life (years)"), ("─" * 22, "─" * 18)]
    lifespan_rows += [(name, f"{yrs:.1f}") for name, yrs in breed_avg_lifespan[:20]]
    col1_l = max(len(r[0]) for r in lifespan_rows)
    lifespan_lines = "\n".join(f"  {r[0]:<{col1_l}}  {r[1]}" for r in lifespan_rows)
    logger.info(f"Avg lifespan per breed (top 20):\n{lifespan_lines}\n")
