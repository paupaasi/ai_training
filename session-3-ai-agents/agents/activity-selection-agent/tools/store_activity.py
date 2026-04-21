#!/usr/bin/env python3
"""
Store Activity Tool

Stores activity data to PostgreSQL or SQLite database.

Usage:
  python store_activity.py --file activity.json
  echo '{"name": "Playground", ...}' | python store_activity.py --stdin
  python store_activity.py --name "Helsinki Zoo" --city "Helsinki" --website "https://example.com"
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

# Try PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import Json
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "")
SQLITE_PATH = Path(__file__).parent.parent / "memory" / "data" / "activities.db"


class ActivityStorage:
    """Activity storage with PostgreSQL and SQLite support."""
    
    def __init__(self):
        self.use_postgres = bool(DATABASE_URL) and POSTGRES_AVAILABLE
        self.conn = None
        self._connect()
        self._init_schema()
    
    def _connect(self):
        """Connect to database."""
        if self.use_postgres:
            self.conn = psycopg2.connect(DATABASE_URL)
        else:
            SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(str(SQLITE_PATH))
            self.conn.row_factory = sqlite3.Row
    
    def _init_schema(self):
        """Initialize database schema."""
        if self.use_postgres:
            schema = """
            CREATE TABLE IF NOT EXISTS activities (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                city VARCHAR(255) NOT NULL,
                country VARCHAR(50),
                category VARCHAR(100),
                description TEXT,
                website VARCHAR(500),
                address TEXT,
                phone VARCHAR(50),
                google_maps_url VARCHAR(500),
                cost_info JSONB,
                opening_hours JSONB,
                age_suitability JSONB,
                indoor_outdoor VARCHAR(50),
                duration_minutes INTEGER,
                stroller_friendly BOOLEAN,
                child_facilities JSONB,
                rating DECIMAL,
                user_notes TEXT,
                visit_date DATE,
                visit_count INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'new',
                source VARCHAR(255),
                raw_data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enriched_at TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_activities_city ON activities(city);
            CREATE INDEX IF NOT EXISTS idx_activities_category ON activities(category);
            CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);
            """
        else:
            schema = """
            CREATE TABLE IF NOT EXISTS activities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT,
                category TEXT,
                description TEXT,
                website TEXT,
                address TEXT,
                phone TEXT,
                google_maps_url TEXT,
                cost_info TEXT,
                opening_hours TEXT,
                age_suitability TEXT,
                indoor_outdoor TEXT,
                duration_minutes INTEGER,
                stroller_friendly INTEGER,
                child_facilities TEXT,
                rating REAL,
                user_notes TEXT,
                visit_date TEXT,
                visit_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'new',
                source TEXT,
                raw_data TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                enriched_at TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_activities_city ON activities(city);
            CREATE INDEX IF NOT EXISTS idx_activities_category ON activities(category);
            CREATE INDEX IF NOT EXISTS idx_activities_status ON activities(status);
            """
        
        cursor = self.conn.cursor()
        for statement in schema.split(';'):
            if statement.strip():
                cursor.execute(statement)
        self.conn.commit()
    
    def store(self, activity: Dict[str, Any]) -> Dict[str, Any]:
        """Store an activity."""
        # Generate ID if missing
        if "id" not in activity:
            activity["id"] = f"activity_{uuid.uuid4().hex[:12]}"
        
        now = datetime.utcnow().isoformat()
        activity["updated_at"] = now
        if "created_at" not in activity:
            activity["created_at"] = now
        
        cursor = self.conn.cursor()
        
        if self.use_postgres:
            # PostgreSQL with JSONB
            cursor.execute("""
                INSERT INTO activities (
                    id, name, city, country, category, description, website, address, phone,
                    google_maps_url, cost_info, opening_hours, age_suitability, indoor_outdoor,
                    duration_minutes, stroller_friendly, child_facilities, rating, user_notes,
                    visit_date, visit_count, status, source, raw_data, created_at, updated_at, enriched_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    city = EXCLUDED.city,
                    country = EXCLUDED.country,
                    category = EXCLUDED.category,
                    description = EXCLUDED.description,
                    website = EXCLUDED.website,
                    address = EXCLUDED.address,
                    phone = EXCLUDED.phone,
                    google_maps_url = EXCLUDED.google_maps_url,
                    cost_info = EXCLUDED.cost_info,
                    opening_hours = EXCLUDED.opening_hours,
                    age_suitability = EXCLUDED.age_suitability,
                    indoor_outdoor = EXCLUDED.indoor_outdoor,
                    duration_minutes = EXCLUDED.duration_minutes,
                    stroller_friendly = EXCLUDED.stroller_friendly,
                    child_facilities = EXCLUDED.child_facilities,
                    rating = EXCLUDED.rating,
                    user_notes = EXCLUDED.user_notes,
                    visit_date = EXCLUDED.visit_date,
                    visit_count = EXCLUDED.visit_count,
                    status = EXCLUDED.status,
                    source = EXCLUDED.source,
                    raw_data = EXCLUDED.raw_data,
                    updated_at = EXCLUDED.updated_at,
                    enriched_at = EXCLUDED.enriched_at
            """, (
                activity.get("id"),
                activity.get("name"),
                activity.get("city"),
                activity.get("country"),
                activity.get("category"),
                activity.get("description"),
                activity.get("website"),
                activity.get("address"),
                activity.get("phone"),
                activity.get("google_maps_url"),
                Json(activity.get("cost_info")),
                Json(activity.get("opening_hours")),
                Json(activity.get("age_suitability")),
                activity.get("indoor_outdoor"),
                activity.get("duration_minutes"),
                activity.get("stroller_friendly"),
                Json(activity.get("child_facilities")),
                activity.get("rating"),
                activity.get("user_notes"),
                activity.get("visit_date"),
                activity.get("visit_count", 0),
                activity.get("status", "new"),
                activity.get("source"),
                Json(activity),
                activity.get("created_at"),
                activity.get("updated_at"),
                activity.get("enriched_at")
            ))
        else:
            # SQLite with JSON as text
            cursor.execute("""
                INSERT OR REPLACE INTO activities (
                    id, name, city, country, category, description, website, address, phone,
                    google_maps_url, cost_info, opening_hours, age_suitability, indoor_outdoor,
                    duration_minutes, stroller_friendly, child_facilities, rating, user_notes,
                    visit_date, visit_count, status, source, raw_data, created_at, updated_at, enriched_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                activity.get("id"),
                activity.get("name"),
                activity.get("city"),
                activity.get("country"),
                activity.get("category"),
                activity.get("description"),
                activity.get("website"),
                activity.get("address"),
                activity.get("phone"),
                activity.get("google_maps_url"),
                json.dumps(activity.get("cost_info")) if activity.get("cost_info") else None,
                json.dumps(activity.get("opening_hours")) if activity.get("opening_hours") else None,
                json.dumps(activity.get("age_suitability")) if activity.get("age_suitability") else None,
                activity.get("indoor_outdoor"),
                activity.get("duration_minutes"),
                1 if activity.get("stroller_friendly") else 0,
                json.dumps(activity.get("child_facilities")) if activity.get("child_facilities") else None,
                activity.get("rating"),
                activity.get("user_notes"),
                activity.get("visit_date"),
                activity.get("visit_count", 0),
                activity.get("status", "new"),
                activity.get("source"),
                json.dumps(activity),
                activity.get("created_at"),
                activity.get("updated_at"),
                activity.get("enriched_at")
            ))
        
        self.conn.commit()
        return {"status": "ok", "id": activity.get("id")}
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """CLI for storing activities."""
    parser = argparse.ArgumentParser(description="Store activities")
    parser.add_argument("--file", help="Activity JSON file to store")
    parser.add_argument("--stdin", action="store_true", help="Read activity from stdin")
    parser.add_argument("--name", help="Activity name")
    parser.add_argument("--city", help="City")
    parser.add_argument("--website", help="Website URL")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    activity = None
    
    if args.file:
        with open(args.file) as f:
            activity = json.load(f)
    elif args.stdin or (not args.file and sys.stdin and not sys.stdin.isatty()):
        activity = json.load(sys.stdin)
    elif args.name and args.city:
        activity = {
            "name": args.name,
            "city": args.city,
            "website": args.website,
            "category": "other"
        }
    else:
        print(json.dumps({"error": "No activity data provided"}), file=sys.stderr)
        sys.exit(1)
    
    storage = ActivityStorage()
    result = storage.store(activity)
    storage.close()
    
    print(json.dumps(result, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
