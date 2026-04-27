#!/usr/bin/env python3
"""
Memory Store — ChromaDB-based memory for the Activity Selection Agent

Provides persistent storage for:
- Family profile and preferences
- Activities discovered and enriched
- Visit history and ratings
- Learned preferences from user interactions

Usage:
  from memory import MemoryStore
  store = MemoryStore()
  
  # Family profile
  profile = store.get_family_profile()
  store.set_family_profile(profile)
  
  # Activities
  store.store_activity(activity)
  activities = store.get_activities(city="Helsinki", category="playground")
  
  # Visit history
  store.record_visit(activity_id="act_123", rating=5, notes="Great!")
  visits = store.get_visit_history()
  
  # Search
  results = store.search_activities("indoor activities for toddlers")
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

_AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))
from agent_env import load_agent_environment

load_agent_environment()

# Try to import chromadb, fall back to file-based storage
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

# Try to import numpy for embeddings
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Try to import Gemini for embeddings
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# Configuration
MEMORY_DIR = Path(__file__).parent / "data"
CHROMA_HOST = os.environ.get("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.environ.get("CHROMA_PORT", "8000"))
EMBEDDING_MODEL = "models/gemini-embedding-001"
EMBEDDING_DIMENSION = 768


class MemoryStore:
    """ChromaDB-based memory store with file fallback."""
    
    def __init__(self, use_server: bool = False, use_chroma: bool = False):
        self.memory_dir = MEMORY_DIR
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = None
        self.collections: Dict[str, Any] = {}
        
        # Only use ChromaDB if explicitly requested and available
        if use_chroma and CHROMA_AVAILABLE:
            try:
                if use_server:
                    self.client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
                else:
                    chroma_path = self.memory_dir / "chroma"
                    chroma_path.mkdir(parents=True, exist_ok=True)
                    self.client = chromadb.PersistentClient(path=str(chroma_path))
                self._init_collections()
            except Exception as e:
                print(f"Warning: ChromaDB initialization failed: {e}", file=sys.stderr)
                print("Falling back to file-based storage", file=sys.stderr)
                self.client = None
    
    def _init_collections(self):
        """Initialize ChromaDB collections."""
        if not self.client:
            return
        
        collection_names = ["family_profile", "activities", "visit_history", "preferences"]
        for name in collection_names:
            try:
                self.collections[name] = self.client.get_or_create_collection(
                    name=f"activity_{name}",
                    metadata={"description": f"Activity agent {name} storage"}
                )
            except Exception as e:
                print(f"Warning: Failed to create collection {name}: {e}", file=sys.stderr)
    
    def _get_collection(self, name: str):
        """Get or create a collection by name."""
        if not self.client:
            return None
        
        if name not in self.collections:
            try:
                self.collections[name] = self.client.get_or_create_collection(
                    name=f"activity_{name}",
                    metadata={"description": f"Activity agent {name} storage"}
                )
            except Exception as e:
                print(f"Warning: Failed to create collection {name}: {e}", file=sys.stderr)
                return None
        
        return self.collections.get(name)
    
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding using Gemini."""
        if not GEMINI_AVAILABLE:
            # Return zero vector if Gemini not available
            return [0.0] * EMBEDDING_DIMENSION
        
        try:
            api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_STUDIO_KEY")
            if not api_key:
                return [0.0] * EMBEDDING_DIMENSION
            
            client = genai.Client(api_key=api_key)
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    output_dimensionality=EMBEDDING_DIMENSION
                )
            )
            
            values = result.embeddings[0].values
            
            # Normalize if using reduced dimensions
            if NUMPY_AVAILABLE and EMBEDDING_DIMENSION != 3072:
                arr = np.array(values)
                norm = np.linalg.norm(arr)
                if norm > 0:
                    values = (arr / norm).tolist()
            
            return values
        except Exception as e:
            print(f"Warning: Embedding generation failed: {e}", file=sys.stderr)
            return [0.0] * EMBEDDING_DIMENSION
    
    def _file_path(self, collection: str) -> Path:
        """Get file path for file-based storage."""
        return self.memory_dir / f"{collection}.json"
    
    def _load_file(self, collection: str) -> Dict[str, Any]:
        """Load data from file."""
        path = self._file_path(collection)
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return {}
    
    def _save_file(self, collection: str, data: Dict[str, Any]):
        """Save data to file."""
        path = self._file_path(collection)
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    
    # Family Profile Operations
    
    def get_family_profile(self) -> Optional[Dict[str, Any]]:
        """Get current family profile."""
        if self.client and "family_profile" in self.collections:
            try:
                results = self.collections["family_profile"].get(ids=["current_profile"])
                if results["documents"]:
                    return json.loads(results["documents"][0])
            except Exception:
                pass
        
        # Fallback to file - check root level first, then nested current_profile for backwards compatibility
        data = self._load_file("family_profile")
        # If root level has family_members, return entire root (new format)
        if data.get("family_members"):
            # Filter out the nested current_profile to avoid confusion
            return {k: v for k, v in data.items() if k != "current_profile"}
        # Otherwise return nested (old format)
        return data.get("current_profile")
    
    def set_family_profile(self, profile: Dict[str, Any]) -> bool:
        """Set family profile."""
        profile["updated_at"] = datetime.utcnow().isoformat()
        if "created_at" not in profile:
            profile["created_at"] = profile["updated_at"]
        
        profile_json = json.dumps(profile)
        
        # Try ChromaDB
        if self.client and "family_profile" in self.collections:
            try:
                embedding = self._get_embedding(profile.get("name", "family profile"))
                self.collections["family_profile"].upsert(
                    ids=["current_profile"],
                    documents=[profile_json],
                    embeddings=[embedding],
                    metadatas=[{"type": "family_profile"}]
                )
                return True
            except Exception as e:
                print(f"Warning: ChromaDB upsert failed: {e}", file=sys.stderr)
        
        # Fallback to file
        data = self._load_file("family_profile")
        data["current_profile"] = profile
        self._save_file("family_profile", data)
        return True
    
    def store_activity(self, activity: Dict[str, Any]) -> bool:
        """Store an activity."""
        activity["updated_at"] = datetime.utcnow().isoformat()
        if "created_at" not in activity:
            activity["created_at"] = activity["updated_at"]
        
        activity_json = json.dumps(activity)
        activity_id = activity.get("id", "unknown")
        
        # Try ChromaDB
        if self.client and "activities" in self.collections:
            try:
                embedding_text = f"{activity.get('name', '')} {activity.get('description', '')} {activity.get('category', '')}"
                embedding = self._get_embedding(embedding_text)
                self.collections["activities"].upsert(
                    ids=[activity_id],
                    documents=[activity_json],
                    embeddings=[embedding],
                    metadatas={
                        "city": activity.get("city", ""),
                        "category": activity.get("category", ""),
                        "status": activity.get("status", "new")
                    }
                )
                return True
            except Exception as e:
                print(f"Warning: ChromaDB upsert failed: {e}", file=sys.stderr)
        
        # Fallback to file
        data = self._load_file("activities")
        data[activity_id] = activity
        self._save_file("activities", data)
        return True
    
    def get_activities(self, city: Optional[str] = None, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get activities, optionally filtered by city and/or category."""
        data = self._load_file("activities")
        activities = list(data.values())
        
        if city:
            activities = [a for a in activities if a.get("city", "").lower() == city.lower()]
        if category:
            activities = [a for a in activities if self._category_matches(a.get("category", ""), category)]
        
        sorted_activities = sorted(activities, key=lambda a: a.get("updated_at", ""), reverse=True)
        return sorted_activities[:limit]
    
    def _category_matches(self, activity_category, search_category: str) -> bool:
        """Check if activity category matches search category (handles both string and array)."""
        if isinstance(activity_category, list):
            return search_category in activity_category
        else:
            return activity_category == search_category
    
    def record_visit(self, activity_id: str, rating: Optional[int] = None, notes: Optional[str] = None) -> bool:
        """Record a visit to an activity."""
        visit = {
            "activity_id": activity_id,
            "rating": rating,
            "notes": notes,
            "visit_date": datetime.utcnow().isoformat()
        }
        
        visit_json = json.dumps(visit)
        
        # Try ChromaDB
        if self.client and "visit_history" in self.collections:
            try:
                embedding = self._get_embedding(notes or "")
                self.collections["visit_history"].add(
                    ids=[f"visit_{activity_id}_{datetime.utcnow().timestamp()}"],
                    documents=[visit_json],
                    embeddings=[embedding],
                    metadatas={"activity_id": activity_id, "rating": rating or 0}
                )
                return True
            except Exception as e:
                print(f"Warning: ChromaDB add failed: {e}", file=sys.stderr)
        
        # Fallback to file
        data = self._load_file("visit_history")
        visits = data.get("visits", [])
        visits.append(visit)
        data["visits"] = visits
        self._save_file("visit_history", data)
        return True
    
    def get_visit_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent visit history."""
        data = self._load_file("visit_history")
        visits = data.get("visits", [])
        return sorted(visits, key=lambda v: v.get("visit_date", ""), reverse=True)[:limit]
    
    def search_activities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search activities by semantic similarity."""
        if self.client and "activities" in self.collections:
            try:
                embedding = self._get_embedding(query)
                results = self.collections["activities"].query(
                    query_embeddings=[embedding],
                    n_results=limit
                )
                activities = []
                for doc in results.get("documents", [[]])[0]:
                    try:
                        activities.append(json.loads(doc))
                    except json.JSONDecodeError:
                        pass
                return activities
            except Exception as e:
                print(f"Warning: ChromaDB search failed: {e}", file=sys.stderr)
        
        # Fallback: simple text search in file
        data = self._load_file("activities")
        query_lower = query.lower()
        matching = [
            a for a in data.values()
            if query_lower in a.get("name", "").lower() or
               query_lower in a.get("description", "").lower() or
               query_lower in a.get("category", "").lower()
        ]
        return sorted(matching, key=lambda a: a.get("updated_at", ""), reverse=True)[:limit]


# CLI Interface

def main():
    """CLI for memory operations."""
    parser = argparse.ArgumentParser(description="Activity Agent Memory Store")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Family profile commands
    profile_parser = subparsers.add_parser("profile", help="Family profile operations")
    profile_parser.add_argument("action", choices=["get", "set", "update"], help="Action")
    profile_parser.add_argument("--file", help="Profile JSON file")
    profile_parser.add_argument("--key", help="Key to update")
    profile_parser.add_argument("--value", help="Value to set")
    
    # Activity commands
    activity_parser = subparsers.add_parser("activity", help="Activity operations")
    activity_parser.add_argument("action", choices=["store", "get", "search"], help="Action")
    activity_parser.add_argument("--id", help="Activity ID")
    activity_parser.add_argument("--city", help="Filter by city")
    activity_parser.add_argument("--category", help="Filter by category")
    activity_parser.add_argument("--query", help="Search query")
    activity_parser.add_argument("--file", help="Activity JSON file")
    
    # Visit commands
    visit_parser = subparsers.add_parser("visit", help="Visit history operations")
    visit_parser.add_argument("action", choices=["record", "list"], help="Action")
    visit_parser.add_argument("--activity-id", help="Activity ID")
    visit_parser.add_argument("--rating", type=int, help="Rating (0-5)")
    visit_parser.add_argument("--notes", help="Visit notes")
    
    args = parser.parse_args()
    
    store = MemoryStore()
    
    if args.command == "profile":
        if args.action == "get":
            profile = store.get_family_profile()
            print(json.dumps(profile, indent=2))
        elif args.action == "set" and args.file:
            with open(args.file) as f:
                profile = json.load(f)
            store.set_family_profile(profile)
            print(json.dumps({"status": "ok"}))
        elif args.action == "update" and args.key and args.value:
            profile = store.get_family_profile()
            profile[args.key] = json.loads(args.value) if args.value.startswith(("[", "{")) else args.value
            store.set_family_profile(profile)
            print(json.dumps({"status": "ok"}))
    
    elif args.command == "activity":
        if args.action == "store" and args.file:
            with open(args.file) as f:
                activity = json.load(f)
            store.store_activity(activity)
            print(json.dumps({"status": "ok"}))
        elif args.action == "get":
            activities = store.get_activities(city=args.city, category=args.category)
            print(json.dumps(activities, indent=2))
        elif args.action == "search" and args.query:
            activities = store.search_activities(args.query)
            print(json.dumps(activities, indent=2))
    
    elif args.command == "visit":
        if args.action == "record" and args.activity_id:
            store.record_visit(args.activity_id, args.rating, args.notes)
            print(json.dumps({"status": "ok"}))
        elif args.action == "list":
            visits = store.get_visit_history()
            print(json.dumps(visits, indent=2))


if __name__ == "__main__":
    main()
