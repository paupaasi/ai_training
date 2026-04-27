#!/usr/bin/env python3
"""Integration tests for FPL Helper agent."""

import json
import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent


def test_agent_help():
    """Test agent displays help."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "fpl_helper.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Help failed: {result.stderr}"
    assert "FPL Helper" in result.stdout, "Missing help text"
    print("[PASS] test_agent_help")


def test_agent_chat_mode():
    """Test agent enters chat mode."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "fpl_helper.py"), "--chat"],
        input="exit\n",
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Chat mode failed: {result.stderr}"
    print("[PASS] test_agent_chat_mode")


def main():
    print("Running Integration tests...")
    print("=" * 50)

    tests = [
        test_agent_help,
        test_agent_chat_mode,
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