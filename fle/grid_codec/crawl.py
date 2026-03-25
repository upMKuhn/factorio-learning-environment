"""
Crawl factorioprints.com blueprints via Firebase REST API + CDN.

Usage:
    python -m fle.grid_codec.crawl --output blueprints/ --limit 1000

Pipeline:
    1. Paginate Firebase /blueprintSummaries to get blueprint keys
    2. Fetch full blueprint JSON from CDN
    3. Decode blueprint string → entities
    4. Save as JSON: {label, description, tags, favorites, entities: [{name, x, y, direction}]}
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path

import requests

from fle.grid_codec.blueprint import from_cdn_json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

FIREBASE_URL = "https://facorio-blueprints.firebaseio.com"
CDN_BASE = "https://factorio-blueprint-firebase-cdn.pages.dev"


def get_cdn_url(key: str) -> str:
    """Convert blueprint key to CDN URL."""
    prefix = key[:3]
    suffix = key[3:]
    return f"{CDN_BASE}/{prefix}/{suffix}.json"


def fetch_summary_keys(
    limit: int = 1000,
    order_by: str = "numberOfFavorites",
    page_size: int = 100,
) -> list[tuple[str, dict]]:
    """
    Fetch blueprint summary keys from Firebase, ordered by favorites (most popular first).

    Returns list of (key, summary_dict) tuples.
    """
    keys: list[tuple[str, dict]] = []
    last_key = None
    last_value = None

    while len(keys) < limit:
        batch = min(page_size, limit - len(keys))

        params = {
            "orderBy": f'"{order_by}"',
            "limitToLast": str(batch + (1 if last_key else 0)),
            "print": "pretty",
        }
        if last_key and last_value is not None:
            params["endAt"] = f'{last_value},"{last_key}"'

        resp = requests.get(f"{FIREBASE_URL}/blueprintSummaries.json", params=params)
        if resp.status_code != 200:
            log.error(f"Firebase returned {resp.status_code}: {resp.text[:200]}")
            break

        data = resp.json()
        if not data:
            break

        # Sort descending by the order field
        items = sorted(data.items(), key=lambda kv: kv[1].get(order_by, 0), reverse=True)

        # Skip the overlap item from pagination
        if last_key:
            items = [(k, v) for k, v in items if k != last_key]

        if not items:
            break

        keys.extend(items)

        # Set up next page
        last_item = items[-1]
        last_key = last_item[0]
        last_value = last_item[1].get(order_by, 0)

        log.info(f"Fetched {len(keys)} summary keys so far...")

        if len(items) < batch:
            break

        time.sleep(1.0)  # rate limit: 1 request per second

    return keys[:limit]


def fetch_and_decode(key: str, summary: dict) -> list[dict] | None:
    """Fetch a blueprint from CDN and decode it. Returns serializable dicts or None."""
    url = get_cdn_url(key)
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        cdn_data = resp.json()
    except Exception as e:
        log.warning(f"Failed to fetch {key}: {e}")
        return None

    try:
        blueprints = from_cdn_json(cdn_data, source_key=key)
    except Exception as e:
        log.warning(f"Failed to decode {key}: {e}")
        return None

    if not blueprints:
        return None

    results = []
    for bp in blueprints:
        results.append({
            "source_key": bp.source_key,
            "label": bp.label,
            "description": bp.description,
            "tags": bp.tags,
            "favorites": bp.favorites,
            "entity_count": bp.entity_count,
            "entities": [
                {"name": e.name, "x": e.x, "y": e.y, "direction": e.direction}
                for e in bp.entities
            ],
        })

    return results


def crawl(output_dir: str, limit: int = 1000, skip_existing: bool = True):
    """Main crawl loop."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    # Also accumulate into a single JSONL file for easy loading
    jsonl_path = out / "blueprints.jsonl"

    log.info(f"Fetching up to {limit} blueprint keys from Firebase...")
    keys = fetch_summary_keys(limit=limit)
    log.info(f"Got {len(keys)} keys. Fetching from CDN...")

    total = 0
    skipped = 0
    failed = 0

    with open(jsonl_path, "a") as jsonl:
        for i, (key, summary) in enumerate(keys):
            # Per-blueprint JSON file
            bp_file = out / f"{key}.json"
            if skip_existing and bp_file.exists():
                skipped += 1
                continue

            results = fetch_and_decode(key, summary)
            if results is None:
                failed += 1
                continue

            # Save individual file
            with open(bp_file, "w") as f:
                json.dump(results, f)

            # Append to JSONL
            for bp_dict in results:
                jsonl.write(json.dumps(bp_dict) + "\n")

            total += len(results)

            if (i + 1) % 10 == 0:
                log.info(f"  [{i+1}/{len(keys)}] decoded {total} blueprints, {failed} failed, {skipped} skipped")

            time.sleep(1.0)  # rate limit: 1 request per second

    log.info(f"Done. {total} blueprints saved to {out}/")
    log.info(f"  JSONL: {jsonl_path}")
    log.info(f"  Failed: {failed}, Skipped: {skipped}")


def main():
    parser = argparse.ArgumentParser(description="Crawl factorioprints.com blueprints")
    parser.add_argument("--output", "-o", default="blueprints", help="Output directory")
    parser.add_argument("--limit", "-n", type=int, default=1000, help="Max blueprints to fetch")
    parser.add_argument("--no-skip", action="store_true", help="Re-fetch existing blueprints")
    args = parser.parse_args()

    crawl(output_dir=args.output, limit=args.limit, skip_existing=not args.no_skip)


if __name__ == "__main__":
    main()
