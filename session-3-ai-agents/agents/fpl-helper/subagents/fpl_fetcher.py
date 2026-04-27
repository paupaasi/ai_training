#!/usr/bin/env python3
"""FPL Data Fetcher - Fetches data from official FPL API."""

import argparse
import json
import sys
import urllib.request
from typing import Any, Dict, List

FPL_API_BASE = "https://fantasy.premierleague.com/api"


def fetch_bootstrap() -> Dict[str, Any]:
    """Fetch bootstrap-static data (players, teams, events)."""
    url = f"{FPL_API_BASE}/bootstrap-static/"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"error": str(e)}


def fetch_fixtures(event_id: int = 0) -> List[Dict[str, Any]]:
    """Fetch fixtures for a specific gameweek."""
    url = f"{FPL_API_BASE}/fixtures/"
    if event_id:
        url += f"?event={event_id}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data if isinstance(data, list) else data.get("fixtures", [])
    except Exception:
        return []


def fetch_event(event_id: int) -> Dict[str, Any]:
    """Fetch event (gameweek) data."""
    url = f"{FPL_API_BASE}/event/{event_id}/"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {"error": str(e)}


def fetch_player_summary(player_id: int) -> Dict[str, Any]:
    """Fetch detailed player summary."""
    url = f"{FPL_API_BASE}/element-summary/{player_id}/"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="FPL Data Fetcher")
    parser.add_argument(
        "--data-type",
        default="all",
        choices=["players", "teams", "fixtures", "events", "all"],
        help="Type of data to fetch"
    )
    parser.add_argument(
        "--player-id",
        type=int,
        help="Specific player ID for detailed data"
    )
    parser.add_argument(
        "--event",
        type=int,
        help="Gameweek number for fixtures"
    )

    args = parser.parse_args()

    if args.player_id:
        result = fetch_player_summary(args.player_id)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    if args.event is not None:
        result = fetch_fixtures(args.event)
        print(json.dumps(result, indent=2))
        sys.exit(0)

    if args.data_type == "teams":
        data = fetch_bootstrap()
        print(json.dumps(data.get("teams", []), indent=2))
        sys.exit(0)

    if args.data_type == "events":
        data = fetch_bootstrap()
        print(json.dumps(data.get("events", []), indent=2))
        sys.exit(0)

    if args.data_type == "fixtures":
        fixtures = fetch_fixtures()
        print(json.dumps(fixtures, indent=2))
        sys.exit(0)

    if args.data_type == "players":
        data = fetch_bootstrap()
        print(json.dumps(data.get("elements", []), indent=2))
        sys.exit(0)

    data = fetch_bootstrap()
    print(json.dumps({
        "teams": data.get("teams", []),
        "events": data.get("events", []),
        "player_count": len(data.get("elements", []))
    }, indent=2))


if __name__ == "__main__":
    main()