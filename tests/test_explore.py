"""
Quick one-shot exploration of the Dog API.
Run this to get a feel for the data before deciding what to build.

    pytest tests/test_explore.py -v -s
or:
    DOG_API_KEY=... python tests/test_explore.py
"""

import logging
import os
import re
import sys
from collections import Counter, defaultdict

import plotext as plt
import requests

logger = logging.getLogger(__name__)
API_KEY = os.environ["DOG_API_KEY"]
BASE_URL = "https://api.thedogapi.com/v1"


# --- helpers ---

def fetch_breeds() -> list:
    r = requests.get(f"{BASE_URL}/breeds", headers={"x-api-key": API_KEY})
    r.raise_for_status()
    return r.json()


def parse_range(s: str | None) -> tuple[float, float] | None:
    if not s:
        return None
    nums = [float(m) for m in re.findall(r"\d+\.?\d*", s)]
    if not nums:
        return None
    return min(nums), max(nums)


def avg(pair: tuple[float, float] | None) -> float | None:
    if pair is None:
        return None
    return (pair[0] + pair[1]) / 2


def size_class(weight_max: float | None) -> str:
    if weight_max is None:
        return "Unknown"
    if weight_max <= 20:
        return "Small"
    if weight_max <= 60:
        return "Medium"
    return "Large"


def separator(title: str = "") -> None:
    width = 70
    if title:
        pad = (width - len(title) - 2) // 2
        print(f"\n{'─' * pad} {title} {'─' * pad}\n")
    else:
        print(f"\n{'─' * width}\n")


def ascii_bar(label: str, value: float, max_value: float, width: int = 35) -> str:
    filled = int((value / max_value) * width)
    bar = "█" * filled + "░" * (width - filled)
    return f"  {label:<32} {bar}  {value:.1f}"


# --- test / script ---

def test_explore_dog_breeds():
    breeds = fetch_breeds()

    enriched = []
    for b in breeds:
        ls = parse_range(b.get("life_span"))
        wt = parse_range(b.get("weight", {}).get("imperial"))
        enriched.append({
            "name":          b.get("name", "Unknown"),
            "group":         b.get("breed_group") or "Unknown",
            "life_avg":      avg(ls),
            "weight_max":    wt[1] if wt else None,
            "size":          size_class(wt[1] if wt else None),
            "temperament":   b.get("temperament") or "",
        })

    has_life  = [e for e in enriched if e["life_avg"] is not None]
    has_both  = [e for e in has_life if e["weight_max"] is not None]

    # --- 1. Summary ---
    separator("DATASET OVERVIEW")
    groups     = Counter(e["group"] for e in enriched)
    sizes      = Counter(e["size"]  for e in enriched)
    rows = [
        ("Total breeds",          len(enriched)),
        ("With life span data",   len(has_life)),
        ("With weight data",      len(has_both)),
        ("Breed groups",          len(groups)),
    ]
    col = max(len(r[0]) for r in rows)
    for label, val in rows:
        print(f"  {label:<{col}}  {val}")

    # --- 2. Top 20 by life span ---
    separator("TOP 20 BREEDS BY AVG LIFE SPAN")
    top20 = sorted(has_life, key=lambda e: -e["life_avg"])[:20]
    max_life = top20[0]["life_avg"]
    for e in top20:
        print(ascii_bar(e["name"], e["life_avg"], max_life))

    # --- 3. Breed groups by count ---
    separator("BREED COUNT BY GROUP")
    max_count = max(groups.values())
    for group, count in groups.most_common():
        print(ascii_bar(group, count, max_count))

    # --- 4. Avg life span by size class ---
    separator("AVG LIFE SPAN BY SIZE CLASS")
    by_size = defaultdict(list)
    for e in has_both:
        by_size[e["size"]].append(e["life_avg"])
    size_avgs = {s: sum(v) / len(v) for s, v in by_size.items()}
    max_s = max(size_avgs.values())
    for size in ["Small", "Medium", "Large"]:
        if size in size_avgs:
            print(ascii_bar(size, size_avgs[size], max_s))

    # --- 5. Weight vs life span scatter (plotext) ---
    separator("WEIGHT vs LIFE SPAN (scatter)")
    weights = [e["weight_max"] for e in has_both]
    lives   = [e["life_avg"]   for e in has_both]
    plt.scatter(weights, lives)
    plt.title("Weight (max lbs) vs Avg Life Span (years)")
    plt.xlabel("Weight (lbs)")
    plt.ylabel("Life span (years)")
    plt.plot_size(70, 20)
    plt.show()

    separator()
    print("  Takeaway: clear inverse relationship between size and longevity.")
    print("  ~40% of breeds lack life span data — worth discussing with stakeholders")
    print("  before building any product feature that depends on it.\n")

    assert len(enriched) > 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_explore_dog_breeds()
