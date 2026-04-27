#!/usr/bin/env python3
"""Injury News Fetcher - Get current Premier League injuries and suspensions."""

import argparse
import json
import sys
import urllib.request
from typing import Any, Dict, List

PREMIER_LEAGUE_API = "https://www.premierleague.com"


def fetch_injuries() -> List[Dict[str, Any]]:
    """Fetch injury data from Premier League."""
    url = f"{PREMIER_LEAGUE_API}/api/pcl/competitions/PL/teams"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data
    except Exception:
        return [{"error": str(e)}]


def parse_injury_html() -> List[Dict[str, Any]]:
    """Parse Premier League injury page."""
    url = f"{PREMIER_LEAGUE_API}/api/pcl/competitions/PL/clubs"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return []


def get_injury_news() -> Dict[str, Any]:
    """Get structured injury information."""
    clubs = parse_injury_html()

    injuries = []

    for club in clubs[:5]:
        club_name = club.get("name", "Unknown")
        players = club.get("players", [])

        for player in players:
            status = player.get("injuryStatus") or player.get("status", "Available")

            if status.lower() not in ["available", "fit"]:
                injuries.append({
                    "player": player.get("name", ""),
                    "club": club_name,
                    "status": status,
                    "type": player.get("injuryType", "Unknown"),
                    "return": player.get("expectedReturn", "TBC")
                })

    if not injuries:
        return {
            "injuries": [],
            "message": "No injuries found. Check Premier League website for updates.",
            "source": "premierleague.com"
        }

    return {
        "injuries": injuries,
        "count": len(injuries),
        "source": "premierleague.com"
    }


def main():
    parser = argparse.ArgumentParser(description="FPL Injury News")
    parser.add_argument(
        "--team",
        help="Filter by team"
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Raw API response"
    )

    args = parser.parse_args()

    if args.raw:
        clubs = parse_injury_html()
        print(json.dumps(clubs[:3], indent=2))
        sys.exit(0)

    result = get_injury_news()

    if args.team:
        team = args.team.lower()
        result["injuries"] = [
            i for i in result.get("injuries", [])
            if team in i.get("club", "").lower()
        ]
        result["count"] = len(result["injuries"])

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()