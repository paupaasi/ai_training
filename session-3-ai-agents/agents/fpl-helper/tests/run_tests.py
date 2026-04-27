#!/usr/bin/env python3
"""Main test runner for FPL Helper agent."""

import subprocess
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).parent.parent


def run_test_file(name):
    """Run a single test file."""
    result = subprocess.run(
        ["python", str(AGENT_DIR / "tests" / f"{name}.py")],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.returncode, result.stdout, result.stderr


def main():
    print("=" * 70)
    print("FPL HELPER AGENT - TEST SUITE")
    print("=" * 70)
    print()

    test_files = [
        "test_memory",
        "test_fpl_fetcher",
        "test_player_lookup",
        "test_fixture_difficulty",
        "test_integration",
    ]

    total_tests = 0
    passed = 0
    failed = 0
    errors = 0

    for test_file in test_files:
        print(f"Running {test_file}...")
        print("-" * 50)
        
        ret, stdout, stderr = run_test_file(test_file)
        
        if ret == 0:
            for line in stdout.split("\n"):
                if "[PASS]" in line or "[FAIL]" in line or "[ERROR]" in line or "Summary:" in line:
                    print(line)
                    if "[PASS]" in line:
                        passed += 1
                    elif "[FAIL]" in line:
                        failed += 1
                    elif "[ERROR]" in line:
                        errors += 1
        else:
            print(f"[ERROR] {test_file}: Test execution failed")
            print(stderr[:500] if stderr else "No output")
            errors += 1
        
        print()

    print("=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    
    results = []
    
    results.append(f"Total test groups: {len(test_files)}")
    results.append(f"Passed: {passed}")
    results.append(f"Failed: {failed}")
    results.append(f"Errors: {errors}")
    
    for r in results:
        print(r)
    
    print()
    
    if failed == 0 and errors == 0:
        print("All tests PASSED")
        return 0
    else:
        print("Some tests FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())