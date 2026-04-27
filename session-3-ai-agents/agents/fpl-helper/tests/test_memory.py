#!/usr/bin/env python3
"""Tests for Memory module."""

import json
import os
import sys
import tempfile
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent


def test_fpl_memory():
    """Test memory operations."""
    import sys
    sys.path.insert(0, str(AGENT_DIR / "memory"))
    from memory import FPLMemory

    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = AGENT_DIR / "memory" / "data"
        original_dir.mkdir(exist_ok=True)

        memory = FPLMemory()

        test_squad = {"players": ["Salah", "Haaland", "Saka"]}
        result = memory.save_squad(test_squad)
        assert result.get("status") == "success", "Failed to save squad"

        loaded = memory.get_squad()
        assert len(loaded.get("players", [])) == 3, "Wrong player count"
        assert "Salah" in loaded.get("players", []), "Missing player"

        prefs = memory.get_preferences()
        memory.save_preferences({"budget": 2.0})
        prefs_loaded = memory.get_preferences()
        assert prefs_loaded.get("budget") == 2.0, "Wrong budget"

        print("[PASS] test_fpl_memory")


def test_fpl_cache():
    """Test FPL data caching."""
    import sys
    sys.path.insert(0, str(AGENT_DIR / "memory"))
    from memory import FPLMemory

    memory = FPLMemory()

    test_data = {"players": [{"id": 1, "name": "Test"}], "teams": []}
    result = memory.cache_fpl_data(test_data)
    assert result == True, "Failed to cache"

    cached = memory.get_fpl_cache()
    assert len(cached.get("players", [])) > 0, "Cache corrupted"

    print("[PASS] test_fpl_cache")


def main():
    print("Running Memory tests...")
    print("=" * 50)

    tests = [
        test_fpl_memory,
        test_fpl_cache,
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