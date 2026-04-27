#!/usr/bin/env python3
"""Tests for FPL Fetcher subagent."""

import json
import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent


def test_fetch_players():
    """Test fetching player data."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "fpl_fetcher.py"), "--data-type", "players"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Fetch failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "error" not in data or len(data) > 0, "Empty response"
    print("[PASS] test_fetch_players")


def test_fetch_teams():
    """Test fetching team data."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "fpl_fetcher.py"), "--data-type", "teams"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Fetch failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert isinstance(data, list), "Expected list of teams"
    assert len(data) > 0, "No teams returned"
    print("[PASS] test_fetch_teams")


def test_fetch_events():
    """Test fetching events/gameweeks."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "fpl_fetcher.py"), "--data-type", "events"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Fetch failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert isinstance(data, list), "Expected list of events"
    print("[PASS] test_fetch_events")


def test_fetch_all():
    """Test fetching all data."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "fpl_fetcher.py"), "--data-type", "all"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Fetch failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "player_count" in data or "teams" in data, "Missing expected keys"
    print("[PASS] test_fetch_all")


def main():
    print("Running FPL Fetcher tests...")
    print("=" * 50)

    tests = [
        test_fetch_teams,
        test_fetch_events,
        test_fetch_all,
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