#!/usr/bin/env python3
"""Tests for Player Lookup subagent."""

import json
import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent


def test_search_player_by_name():
    """Test searching for a player by name."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "player_lookup.py"), "--name", "Salah"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Search failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert data.get("count", 0) > 0, "No players found"
    assert data.get("players")[0].get("name") != None, "Missing player name"
    print("[PASS] test_search_player_by_name")


def test_search_player_partial():
    """Test partial name search."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "player_lookup.py"), "--name", "Har"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Search failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "players" in data, "Missing players key"
    print("[PASS] test_search_player_partial")


def test_filter_by_position():
    """Test filtering by position."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "player_lookup.py"), "--position", "FWD", "--limit", "5"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Filter failed: {result.stderr}"
    data = json.loads(result.stdout)
    for p in data.get("players", [])[:3]:
        assert p.get("position") == "FWD", f"Wrong position: {p.get('position')}"
    print("[PASS] test_filter_by_position")


def test_player_details():
    """Test player details include key metrics."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "player_lookup.py"), "--name", "Salah", "--limit", "1"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Details failed: {result.stderr}"
    data = json.loads(result.stdout)
    player = data.get("players", [{}])[0]
    assert player.get("price") != None, "Missing price"
    assert player.get("total_points") != None, "Missing total_points"
    assert player.get("form") != None, "Missing form"
    assert player.get("points_per_million") != None, "Missing PPM"
    print("[PASS] test_player_details")


def main():
    print("Running Player Lookup tests...")
    print("=" * 50)

    tests = [
        test_search_player_by_name,
        test_search_player_partial,
        test_filter_by_position,
        test_player_details,
    ]

    passed = 0
    failed = 0
    errors = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            errors += 1

    print("=" * 50)
    print(f"Summary: {passed} passed, {failed} failed, {errors} errors")
    return failed + errors


if __name__ == "__main__":
    sys.exit(main())