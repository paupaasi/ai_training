#!/usr/bin/env python3
"""Tests for Fixture Difficulty subagent."""

import json
import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent


def test_fetch_fixture_difficulty():
    """Test fetching fixture difficulty data."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "fixture_difficulty.py")],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Fetch failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "teams" in data or "easiest" in data, "Missing teams data"
    print("[PASS] test_fetch_fixture_difficulty")


def test_team_filter():
    """Test filtering by specific team."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "fixture_difficulty.py"), "--team", "Arsenal", "--gameweeks", "3"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Filter failed: {result.stderr}"
    data = json.loads(result.stdout)
    assert "ratings" in data, "Missing ratings"
    assert data.get("average_difficulty") != None, "Missing average"
    print("[PASS] test_team_filter")


def test_invalid_team():
    """Test handling of invalid team name."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "subagents" / "fixture_difficulty.py"), "--team", "InvalidTeamXYZ"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode != 0 or "error" in result.stdout, "Should handle invalid team"
    print("[PASS] test_invalid_team")


def main():
    print("Running Fixture Difficulty tests...")
    print("=" * 50)

    tests = [
        test_fetch_fixture_difficulty,
        test_team_filter,
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