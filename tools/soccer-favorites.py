#!/usr/bin/env python3
"""
Soccer Favorites RAG Memory Skill
Stores and retrieves favorite soccer players using SQLite and Gemini embeddings for semantic search.
"""

import sqlite3
import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import hashlib

# Import Gemini
try:
    from google import genai
except ImportError:
    print("Error: google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

# Import dotenv
try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env.local")

class SoccerFavoritesDB:
    """SQLite database for managing favorite soccer players with RAG embeddings."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection."""
        if db_path is None:
            # Store database in the skill folder (.agents/skills/soccer-favorites/)
            db_path = Path(__file__).parent.parent / ".agents" / "skills" / "soccer-favorites" / "soccer_favorites.db"
        
        self.db_path = db_path
        self.conn = None
        self.init_db()
    
    def init_db(self):
        """Initialize database schema."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Create players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                position TEXT NOT NULL,
                team TEXT NOT NULL,
                notes TEXT NOT NULL,
                added_date TEXT NOT NULL,
                embedding BLOB NOT NULL
            )
        """)
        
        self.conn.commit()
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding from Gemini for text."""
        try:
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_AI_STUDIO_KEY")
            if not api_key:
                print("Error: GEMINI_API_KEY or GOOGLE_AI_STUDIO_KEY not set in .env.local")
                sys.exit(1)
            
            client = genai.Client(api_key=api_key)
            
            response = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text
            )
            
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error getting embedding: {e}")
            sys.exit(1)
    
    def add_player(self, name: str, position: str, team: str, notes: str) -> bool:
        """Add a new player to favorites."""
        try:
            # Get embedding for the combined player description
            combined_text = f"{name} {position} {team} {notes}"
            embedding = self.get_embedding(combined_text)
            
            # Convert embedding to binary
            embedding_blob = json.dumps(embedding).encode('utf-8')
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO players (name, position, team, notes, added_date, embedding)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                name,
                position,
                team,
                notes,
                datetime.now().isoformat(),
                embedding_blob
            ))
            
            self.conn.commit()
            print(f"✓ Added {name} ({position}) to favorites")
            return True
        except sqlite3.IntegrityError:
            print(f"Error: {name} already exists in favorites")
            return False
        except Exception as e:
            print(f"Error adding player: {e}")
            return False
    
    def update_player(self, name: str, notes: str) -> bool:
        """Update a player's notes."""
        try:
            cursor = self.conn.cursor()
            
            # Check if player exists
            cursor.execute("SELECT position, team FROM players WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if not row:
                print(f"Error: {name} not found in favorites")
                return False
            
            # Get new embedding
            combined_text = f"{name} {row['position']} {row['team']} {notes}"
            embedding = self.get_embedding(combined_text)
            embedding_blob = json.dumps(embedding).encode('utf-8')
            
            cursor.execute("""
                UPDATE players
                SET notes = ?, embedding = ?
                WHERE name = ?
            """, (notes, embedding_blob, name))
            
            self.conn.commit()
            print(f"✓ Updated {name}'s notes")
            return True
        except Exception as e:
            print(f"Error updating player: {e}")
            return False
    
    def delete_player(self, name: str) -> bool:
        """Delete a player from favorites."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM players WHERE name = ?", (name,))
            
            if cursor.rowcount == 0:
                print(f"Error: {name} not found in favorites")
                return False
            
            self.conn.commit()
            print(f"✓ Deleted {name} from favorites")
            return True
        except Exception as e:
            print(f"Error deleting player: {e}")
            return False
    
    def list_players(self, format: str = "text") -> bool:
        """List all favorite players."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT name, position, team, notes, added_date
                FROM players
                ORDER BY added_date DESC
            """)
            
            rows = cursor.fetchall()
            
            if not rows:
                print("No favorite players yet. Add one with: npm run soccer-favorites -- --add")
                return True
            
            if format == "json":
                players = [
                    {
                        "name": row["name"],
                        "position": row["position"],
                        "team": row["team"],
                        "notes": row["notes"],
                        "added_date": row["added_date"]
                    }
                    for row in rows
                ]
                print(json.dumps(players, indent=2))
            else:
                print(f"\n📋 Favorite Soccer Players ({len(rows)} total)\n")
                for i, row in enumerate(rows, 1):
                    print(f"{i}. {row['name']}")
                    print(f"   Position: {row['position']}")
                    print(f"   Team: {row['team']}")
                    print(f"   Notes: {row['notes']}")
                    print(f"   Added: {row['added_date']}\n")
            
            return True
        except Exception as e:
            print(f"Error listing players: {e}")
            return False
    
    def search_players(self, query: str, n_results: int = 5, format: str = "text") -> bool:
        """Search players using semantic similarity."""
        try:
            # Get embedding for the search query
            query_embedding = self.get_embedding(query)
            query_embedding_json = json.dumps(query_embedding)
            
            cursor = self.conn.cursor()
            cursor.execute("SELECT name, position, team, notes, embedding FROM players")
            rows = cursor.fetchall()
            
            if not rows:
                print("No favorite players to search. Add some first!")
                return True
            
            # Calculate similarity scores
            results = []
            for row in rows:
                stored_embedding = json.loads(row["embedding"].decode('utf-8'))
                
                # Cosine similarity
                similarity = self._cosine_similarity(query_embedding, stored_embedding)
                
                results.append({
                    "name": row["name"],
                    "position": row["position"],
                    "team": row["team"],
                    "notes": row["notes"],
                    "similarity": similarity
                })
            
            # Sort by similarity (descending) and limit
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:n_results]
            
            if format == "json":
                print(json.dumps(results, indent=2))
            else:
                print(f"\n🔍 Search Results for: '{query}'\n")
                for i, result in enumerate(results, 1):
                    print(f"{i}. {result['name']} (Match: {result['similarity']:.2%})")
                    print(f"   Position: {result['position']}")
                    print(f"   Team: {result['team']}")
                    print(f"   Notes: {result['notes']}\n")
            
            return True
        except Exception as e:
            print(f"Error searching players: {e}")
            return False
    
    def export_players(self, output_file: str = None) -> bool:
        """Export all players to JSON file."""
        try:
            if output_file is None:
                output_file = Path(__file__).parent / "players_export.json"
            
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT name, position, team, notes, added_date
                FROM players
                ORDER BY added_date DESC
            """)
            
            rows = cursor.fetchall()
            players = [
                {
                    "name": row["name"],
                    "position": row["position"],
                    "team": row["team"],
                    "notes": row["notes"],
                    "added_date": row["added_date"]
                }
                for row in rows
            ]
            
            with open(output_file, 'w') as f:
                json.dump(players, f, indent=2)
            
            print(f"✓ Exported {len(players)} players to {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting players: {e}")
            return False
    
    def import_players(self, input_file: str) -> bool:
        """Import players from JSON file."""
        try:
            with open(input_file, 'r') as f:
                players = json.load(f)
            
            count = 0
            for player in players:
                if self.add_player(
                    player["name"],
                    player["position"],
                    player["team"],
                    player["notes"]
                ):
                    count += 1
            
            print(f"✓ Imported {count}/{len(players)} players")
            return True
        except FileNotFoundError:
            print(f"Error: File {input_file} not found")
            return False
        except Exception as e:
            print(f"Error importing players: {e}")
            return False
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Manage favorite soccer players with RAG and semantic search"
    )
    
    parser.add_argument(
        "--add",
        action="store_true",
        help="Add a new favorite player"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all favorite players"
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="Search players by description"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete a player"
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Update a player's notes"
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export all players to JSON"
    )
    parser.add_argument(
        "--import",
        action="store_true",
        dest="import_data",
        help="Import players from JSON"
    )
    parser.add_argument(
        "--name",
        help="Player name"
    )
    parser.add_argument(
        "--position",
        help="Playing position"
    )
    parser.add_argument(
        "--team",
        help="Team name"
    )
    parser.add_argument(
        "--notes",
        help="Player notes or description"
    )
    parser.add_argument(
        "--output",
        help="Output file path (for export)"
    )
    parser.add_argument(
        "--file",
        help="Input file path (for import)"
    )
    parser.add_argument(
        "--query",
        help="Search query"
    )
    parser.add_argument(
        "-n", "--n-results",
        type=int,
        default=5,
        help="Number of search results (default: 5)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--db",
        help="SQLite database path"
    )
    parser.add_argument(
        "search_query",
        nargs="?",
        help="Search query (positional argument)"
    )
    
    args = parser.parse_args()
    
    db = SoccerFavoritesDB(args.db)
    
    try:
        if args.add:
            if not all([args.name, args.position, args.team, args.notes]):
                print("Error: --add requires --name, --position, --team, and --notes")
                sys.exit(1)
            db.add_player(args.name, args.position, args.team, args.notes)
        
        elif args.list:
            db.list_players(format=args.format)
        
        elif args.search:
            query = args.query or args.search_query
            if not query:
                print("Error: --search requires a query")
                sys.exit(1)
            db.search_players(query, n_results=args.n_results, format=args.format)
        
        elif args.delete:
            if not args.name:
                print("Error: --delete requires --name")
                sys.exit(1)
            db.delete_player(args.name)
        
        elif args.update:
            if not args.name or not args.notes:
                print("Error: --update requires --name and --notes")
                sys.exit(1)
            db.update_player(args.name, args.notes)
        
        elif args.export:
            db.export_players(args.output)
        
        elif args.import_data:
            if not args.file:
                print("Error: --import requires --file")
                sys.exit(1)
            db.import_players(args.file)
        
        else:
            parser.print_help()
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
