#!/usr/bin/env python3
"""
Retrieve Activities Tool

Query and retrieve activities from the database.

Usage:
  python retrieve_activities.py --all
  python retrieve_activities.py --id activity_123
  python retrieve_activities.py --city Helsinki
  python retrieve_activities.py --city Helsinki --category playground
  python retrieve_activities.py --city Helsinki --toddler-friendly
  python retrieve_activities.py --status enriched --limit 20
  python retrieve_activities.py --indoor-outdoor indoor
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Try PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "")
SQLITE_PATH = Path(__file__).parent.parent / "memory" / "data" / "activities.db"


class ActivityRetrieval:
    """Activity retrieval with PostgreSQL and SQLite support."""
    
    def __init__(self):
        self.use_postgres = bool(DATABASE_URL) and POSTGRES_AVAILABLE
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Connect to database."""
        if self.use_postgres:
            self.conn = psycopg2.connect(DATABASE_URL)
        else:
            if not SQLITE_PATH.exists():
                raise FileNotFoundError(f"Database not found: {SQLITE_PATH}")
            self.conn = sqlite3.connect(str(SQLITE_PATH))
            self.conn.row_factory = sqlite3.Row
    
    def _parse_row(self, row: Any) -> Dict[str, Any]:
        """Parse a database row into an activity dict."""
        if self.use_postgres:
            return dict(row)
        else:
            activity = dict(row)
            # Parse JSON fields
            for field in ["cost_info", "opening_hours", "age_suitability", "child_facilities", "raw_data"]:
                if activity.get(field):
                    try:
                        activity[field] = json.loads(activity[field])
                    except (json.JSONDecodeError, TypeError):
                        pass
            # Convert boolean fields
            if "stroller_friendly" in activity:
                activity["stroller_friendly"] = bool(activity["stroller_friendly"])
            return activity
    
    def _get_cursor(self):
        """Get a cursor appropriate for the database type."""
        if self.use_postgres:
            return self.conn.cursor(cursor_factory=RealDictCursor)
        return self.conn.cursor()
    
    def get_by_id(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """Get an activity by ID."""
        cursor = self._get_cursor()
        sql = "SELECT * FROM activities WHERE id = %s" if self.use_postgres else "SELECT * FROM activities WHERE id = ?"
        cursor.execute(sql, (activity_id,))
        row = cursor.fetchone()
        return self._parse_row(row) if row else None
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all activities with pagination."""
        cursor = self._get_cursor()
        sql = ("SELECT * FROM activities ORDER BY updated_at DESC LIMIT %s OFFSET %s" if self.use_postgres 
               else "SELECT * FROM activities ORDER BY updated_at DESC LIMIT ? OFFSET ?")
        cursor.execute(sql, (limit, offset))
        return [self._parse_row(row) for row in cursor.fetchall()]
    
    def query(
        self,
        city: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        indoor_outdoor: Optional[str] = None,
        toddler_friendly: Optional[bool] = None,
        min_rating: Optional[float] = None,
        stroller_friendly: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Query activities with filters."""
        cursor = self._get_cursor()
        
        conditions = []
        params = []
        
        if city:
            conditions.append("city = %s" if self.use_postgres else "city = ?")
            params.append(city)
        
        if category:
            conditions.append("category = %s" if self.use_postgres else "category = ?")
            params.append(category)
        
        if status:
            conditions.append("status = %s" if self.use_postgres else "status = ?")
            params.append(status)
        
        if indoor_outdoor:
            conditions.append("indoor_outdoor = %s" if self.use_postgres else "indoor_outdoor = ?")
            params.append(indoor_outdoor)
        
        if toddler_friendly is not None:
            # Check in age_suitability JSON - this is simplified for SQLite
            # For proper JSON query, use PostgreSQL with JSONB operators
            if self.use_postgres:
                conditions.append("(age_suitability->>'toddler_friendly')::boolean = %s")
            else:
                conditions.append("age_suitability LIKE '%toddler_friendly%'")
            params.append(toddler_friendly)
        
        if min_rating is not None:
            conditions.append("rating >= %s" if self.use_postgres else "rating >= ?")
            params.append(min_rating)
        
        if stroller_friendly is not None:
            conditions.append("stroller_friendly = %s" if self.use_postgres else "stroller_friendly = ?")
            params.append(1 if stroller_friendly else 0)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        placeholder = "%s" if self.use_postgres else "?"
        
        sql = f"""
            SELECT * FROM activities 
            WHERE {where_clause}
            ORDER BY updated_at DESC
            LIMIT {placeholder} OFFSET {placeholder}
        """
        
        cursor.execute(sql, params + [limit, offset])
        return [self._parse_row(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """CLI for retrieving activities."""
    parser = argparse.ArgumentParser(description="Retrieve activities")
    parser.add_argument("--all", action="store_true", help="Get all activities")
    parser.add_argument("--id", help="Get activity by ID")
    parser.add_argument("--city", help="Filter by city")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--status", help="Filter by status (new, enriched, visited, favorite, skipped)")
    parser.add_argument("--indoor-outdoor", choices=["indoor", "outdoor", "both"], help="Filter by indoor/outdoor")
    parser.add_argument("--toddler-friendly", action="store_true", help="Filter for toddler-friendly only")
    parser.add_argument("--stroller-friendly", action="store_true", help="Filter for stroller-friendly only")
    parser.add_argument("--min-rating", type=float, help="Filter by minimum rating")
    parser.add_argument("--limit", type=int, default=100, help="Limit results (default: 100)")
    parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    retrieval = ActivityRetrieval()
    
    try:
        if args.id:
            activity = retrieval.get_by_id(args.id)
            if activity:
                print(json.dumps(activity, indent=2 if args.pretty else None))
            else:
                print(json.dumps({"error": "Activity not found"}), file=sys.stderr)
                sys.exit(1)
        elif args.all:
            activities = retrieval.get_all(limit=args.limit, offset=args.offset)
            print(json.dumps(activities, indent=2 if args.pretty else None))
        else:
            activities = retrieval.query(
                city=args.city,
                category=args.category,
                status=args.status,
                indoor_outdoor=args.indoor_outdoor,
                toddler_friendly=args.toddler_friendly if args.toddler_friendly else None,
                stroller_friendly=args.stroller_friendly if args.stroller_friendly else None,
                min_rating=args.min_rating,
                limit=args.limit,
                offset=args.offset
            )
            print(json.dumps(activities, indent=2 if args.pretty else None))
    
    finally:
        retrieval.close()


if __name__ == "__main__":
    main()
