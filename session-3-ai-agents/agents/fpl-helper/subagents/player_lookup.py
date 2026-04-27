#!/usr/bin/env python3
"""Player Lookup - Search and analyze specific FPL players."""

import argparse
import json
import sys
import urllib.request
from typing import Any, Dict, List, Optional

FPL_API_BASE = "https://fantasy.premierleague.com/api"


def fetch_bootstrap() -> Dict[str, Any]:
    """Fetch bootstrap data."""
    url = f"{FPL_API_BASE}/bootstrap-static/"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return {"error": str(e)}


def search_players(query: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search players by name."""
    query_lower = query.lower()
    players = data.get("elements", [])

    matches = []
    for p in players:
        full_name = f"{p.get('first_name', '')} {p.get('second_name', '')} {p.get('web_name', '')}".lower()
        if query_lower in full_name:
            matches.append(p)

    return matches


def get_player_details(player_id: int) -> Optional[Dict[str, Any]]:
    """Get detailed player info from element-summary."""
    url = f"{FPL_API_BASE}/element-summary/{player_id}/"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def analyze_player(player: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze player and produce recommendation metrics."""
    price = player.get("now_cost", 0) / 10.0
    total_pts = player.get("total_points", 0)
    form = float(player.get("form", 0))
    goals = player.get("goals_scored", 0)
    assists = player.get("assists", 0)
    bps = player.get("bonus", 0)

    pts_per_million = total_pts / price if price > 0 else 0

    return {
        "id": player.get("id"),
        "name": player.get("web_name"),
        "team": player.get("team"),
        "position": player.get("element_type"),
        "price": price,
        "total_points": total_pts,
        "form": form,
        "goals": goals,
        "assists": assists,
        "bonus_points": bps,
        "points_per_million": round(pts_per_million, 2),
        "selected_by": player.get("selected_by_percent", 0),
        "transfers_in": player.get("transfers_in", 0),
        "transfers_out": player.get("transfers_out", 0),
        "minutes": player.get("minutes", 0),
        "clean_sheets": player.get("clean_sheets", 0),
        "ICT": player.get("ICT_index", "0.0")
    }


def main():
    parser = argparse.ArgumentParser(description="FPL Player Lookup")
    parser.add_argument(
        "--name",
        help="Player name to search"
    )
    parser.add_argument(
        "--id",
        type=int,
        help="Player ID"
    )
    parser.add_argument(
        "--team",
        help="Filter by team name"
    )
    parser.add_argument(
        "--position",
        choices=["GK", "DEF", "MID", "FWD"],
        help="Filter by position"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Max results"
    )

    args = parser.parse_args()

    data = fetch_bootstrap()
    if "error" in data:
        print(json.dumps({"error": data["error"]}))
        sys.exit(1)

    players = data.get("elements", [])
    teams = {t["id"]: t["name"] for t in data.get("teams", [])}

    if args.id:
        for p in players:
            if p.get("id") == args.id:
                details = analyze_player(p)
                details["team_name"] = teams.get(p.get("team"), "Unknown")
                print(json.dumps(details, indent=2))
                sys.exit(0)
        print(json.dumps({"error": f"Player {args.id} not found"}))
        sys.exit(1)

    if args.name:
        matches = search_players(args.name, data)
    else:
        matches = players[:args.limit]

    if args.team:
        team_id = None
        for tid, name in teams.items():
            if args.team.lower() in name.lower():
                team_id = tid
                break
        if team_id is not None:
            matches = [p for p in matches if p.get("team") == team_id]

    if args.position:
        pos_map = {"GK": 1, "DEF": 2, "MID": 3, "FWD": 4}
        pos_id = pos_map.get(args.position)
        if pos_id:
            matches = [p for p in matches if p.get("element_type") == pos_id]

    results = []
    for p in matches[:args.limit]:
        details = analyze_player(p)
        details["team_name"] = teams.get(p.get("team"), "Unknown")
        results.append(details)

    print(json.dumps({"count": len(results), "players": results}, indent=2))


if __name__ == "__main__":
    main()