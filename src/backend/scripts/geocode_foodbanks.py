"""One-shot script: geocode all Foodbank.city values via Nominatim, write to FoodbankLocation."""

import time
import urllib.parse
import urllib.request
import json

from sqlmodel import Session, select

from src.backend.database import engine
from src.backend.models.foodbank import Foodbank, FoodbankLocation


def geocode(city: str) -> tuple[float, float] | None:
    query = urllib.parse.urlencode({
        "q": f"{city}, Netherlands",
        "format": "json",
        "limit": 1,
        "countrycodes": "nl",
    })
    url = f"https://nominatim.openstreetmap.org/search?{query}"
    req = urllib.request.Request(url, headers={"User-Agent": "klimaatkracht-geocoder/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        results = json.loads(resp.read())
    if not results:
        return None
    return float(results[0]["lat"]), float(results[0]["lon"])


def main() -> None:
    with Session(engine) as session:
        banks = session.exec(select(Foodbank)).all()
        existing_ids = {
            loc.foodbank_id
            for loc in session.exec(select(FoodbankLocation)).all()
        }
        missing = [b for b in banks if b.id not in existing_ids]
        print(f"{len(missing)} banks need geocoding (of {len(banks)} total)")

        for bank in missing:
            try:
                coords = geocode(bank.city)
                if coords:
                    lat, lng = coords
                    session.add(FoodbankLocation(foodbank_id=bank.id, lat=lat, lng=lng))
                    print(f"  ✓ {bank.name} ({bank.city}) → {lat:.4f}, {lng:.4f}")
                else:
                    print(f"  ✗ {bank.name} ({bank.city}) — no result")
            except Exception as e:
                print(f"  ✗ {bank.name} ({bank.city}) — error: {e}")
            time.sleep(1)  # Nominatim rate limit: 1 req/sec

        session.commit()
        print("Done.")


if __name__ == "__main__":
    main()
