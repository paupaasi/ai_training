#!/usr/bin/env python3
"""Fixture Difficulty Calculator - Calculate FDR ratings for teams."""

import argparse
import json
import sys
import urllib.request
from typing import Any, Dict, List, Tuple

FPL_API_BASE = "https://fantasy.premierleague.com/api"


def fetch_bootstrap() -> Dict[str, Any]:
    """Fetch bootstrap data."""
    url = f"{FPL_API_BASE}/bootstrap-static/"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {"error": str(e)}


def fetch_fixtures(event_id: int = 0) -> List[Dict[str, Any]]:
    """Fetch fixtures."""
    url = f"{FPL_API_BASE}/fixtures/"
    if event_id:
        url += f"?event={event_id}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read().decode())
            return data if isinstance(data, list) else []
    except Exception:
        return []


def get_team_fdr(team_id: int, fixtures: List[Dict], num_gw: int = 5) -> Tuple[List[Dict[str, Any]], float]:
    """Calculate fixture difficulty ratings for a team."""
    team_fixtures = [
        f for f in fixtures
        if f.get("team_h") == team_id or f.get("team_a") == team_id
    ][:num_gw]

    ratings = []
    total_score = 0

    for f in team_fixtures:
        gw = f.get("event", 0)
        if f.get("team_h") == team_id:
            diff = f.get("difficulty_h", 3)
            opp = f.get("team_a")
            home = True
        else:
            diff = f.get("difficulty_a", 3)
            opp = f.get("team_h")
            home = False

        ratings.append({
            "gameweek": gw,
            "opponent": opp,
            "difficulty": diff,
            "home": home
        })
        total_score += diff

    avg = total_score / len(ratings) if ratings else 3.0

    return ratings, round(avg, 2)


def calculate_all_team_fdr(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate FDR for all teams."""
    teams = data.get("teams", [])
    fixtures = data.get("fixtures", [])

    if not fixtures:
        fixtures = fetch_fixtures()

    team_fdr = {}

    for team in teams:
        team_id = team.get("id")
        team_name = team.get("name")

        ratings, avg = get_team_fdr(team_id, fixtures)

        rating_label = "Easy"
        if avg > 3.5:
            rating_label = "Hard"
        elif avg > 2.5:
            rating_label = "Medium"

        team_fdr[team_name] = {
            "team_id": team_id,
            "ratings": ratings,
            "average": avg,
            "label": rating_label
        }

    return team_fdr


def main():
    parser = argparse.ArgumentParser(description="Fixture Difficulty Calculator")
    parser.add_argument(
        "--team",
        help="Team name"
    )
    parser.add_argument(
        "--gameweeks",
        type=int,
        default=5,
        help="Number of gameweeks to analyze"
    )

    args = parser.parse_args()

    data = fetch_bootstrap()
    if "error" in data:
        print(json.dumps({"error": data["error"]}))
        sys.exit(1)

    if args.team:
        team_name = args.team.lower()
        team_id = None

        teams = data.get("teams", [])
        for t in teams:
            if team_name in t.get("name", "").lower():
                team_id = t.get("id")
                team_name = t.get("name")
                break

        if team_id is None:
            print(json.dumps({"error": f"Team not found: {args.team}"}))
            sys.exit(1)

        fixtures = fetch_fixtures()
        ratings, avg = get_team_fdr(team_id, fixtures, args.gameweeks)

        print(json.dumps({
            "team": team_name,
            "gameweeks": args.gameweeks,
            "ratings": ratings,
            "average_difficulty": avg
        }, indent=2))
        sys.exit(0)

    result = calculate_all_team_fdr(data)

    sorted_teams = sorted(
        result.items(),
        key=lambda x: x[1].get("average", 3),
        reverse=False
    )

    print(json.dumps({
        "most_difficult": [t[0] for t in sorted_teams[-3:]],
        "easiest": [t[0] for t in sorted_teams[:3]],
        "teams": result
    }, indent=2))


if __name__ == "__main__":
    main()