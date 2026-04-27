#!/usr/bin/env python3
"""
Memory Tool CLI

Convenient wrapper for memory operations.

Usage:
  python memory_tool.py profile get
  python memory_tool.py profile set --file family_profile.json
  python memory_tool.py profile update --key home_city --value Helsinki
  python memory_tool.py activity store --file activity.json
  python memory_tool.py activity get --city Helsinki --category playground
  python memory_tool.py activity search --query "indoor activities for toddlers"
  python memory_tool.py visit record --activity-id act_123 --rating 5 --notes "Great!"
  python memory_tool.py visit list
"""

import argparse
import json
import os
import sys
from pathlib import Path

_AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT / "memory"))

from memory import MemoryStore


def main():
    """CLI for memory operations."""
    parser = argparse.ArgumentParser(description="Activity Agent Memory Operations")
    subparsers = parser.add_subparsers(dest="resource", help="Resource type")
    
    # Profile commands
    profile_parser = subparsers.add_parser("profile", help="Family profile operations")
    profile_subparsers = profile_parser.add_subparsers(dest="action", help="Action")
    
    profile_get = profile_subparsers.add_parser("get", help="Get family profile")
    profile_get.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    profile_set = profile_subparsers.add_parser("set", help="Set family profile from file")
    profile_set.add_argument("--file", required=True, help="Profile JSON file")
    profile_set.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    profile_update = profile_subparsers.add_parser("update", help="Update profile field")
    profile_update.add_argument("--key", required=True, help="Field key")
    profile_update.add_argument("--value", required=True, help="Field value (JSON or string)")
    profile_update.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    # Activity commands
    activity_parser = subparsers.add_parser("activity", help="Activity operations")
    activity_subparsers = activity_parser.add_subparsers(dest="action", help="Action")
    
    activity_store = activity_subparsers.add_parser("store", help="Store activity")
    activity_store.add_argument("--file", required=True, help="Activity JSON file")
    activity_store.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    activity_get = activity_subparsers.add_parser("get", help="Get activities")
    activity_get.add_argument("--city", help="Filter by city")
    activity_get.add_argument("--category", help="Filter by category")
    activity_get.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    activity_search = activity_subparsers.add_parser("search", help="Search activities")
    activity_search.add_argument("--query", required=True, help="Search query")
    activity_search.add_argument("--limit", type=int, default=10, help="Max results")
    activity_search.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    # Visit commands
    visit_parser = subparsers.add_parser("visit", help="Visit history operations")
    visit_subparsers = visit_parser.add_subparsers(dest="action", help="Action")
    
    visit_record = visit_subparsers.add_parser("record", help="Record activity visit")
    visit_record.add_argument("--activity-id", required=True, help="Activity ID")
    visit_record.add_argument("--rating", type=int, help="Rating (0-5)")
    visit_record.add_argument("--notes", help="Visit notes")
    visit_record.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    visit_list = visit_subparsers.add_parser("list", help="List visit history")
    visit_list.add_argument("--limit", type=int, default=50, help="Max results")
    visit_list.add_argument("--pretty", action="store_true", help="Pretty-print output")
    
    args = parser.parse_args()
    
    store = MemoryStore()
    result = None
    
    if args.resource == "profile":
        if args.action == "get":
            result = store.get_family_profile()
        elif args.action == "set":
            with open(args.file) as f:
                profile = json.load(f)
            store.set_family_profile(profile)
            result = {"status": "ok"}
        elif args.action == "update":
            profile = store.get_family_profile()
            try:
                value = json.loads(args.value)
            except json.JSONDecodeError:
                value = args.value
            profile[args.key] = value
            store.set_family_profile(profile)
            result = {"status": "ok"}
    
    elif args.resource == "activity":
        if args.action == "store":
            with open(args.file) as f:
                activity = json.load(f)
            store.store_activity(activity)
            result = {"status": "ok", "id": activity.get("id")}
        elif args.action == "get":
            result = store.get_activities(city=args.city, category=args.category)
        elif args.action == "search":
            result = store.search_activities(args.query, limit=args.limit)
    
    elif args.resource == "visit":
        if args.action == "record":
            store.record_visit(args.activity_id, args.rating, args.notes)
            result = {"status": "ok"}
        elif args.action == "list":
            result = store.get_visit_history(limit=args.limit)
    
    if result is not None:
        indent = 2 if (args.pretty if hasattr(args, "pretty") else False) else None
        print(json.dumps(result, indent=indent, default=str))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
