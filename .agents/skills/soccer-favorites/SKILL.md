---
name: soccer-favorites
description: Use for storing, retrieving, and searching favorite soccer players using RAG with SQLite database. Supports adding players with rich metadata (position, team, skill, stats), retrieving favorites, and semantic search through player descriptions and attributes.
---

## Command
`npm run soccer-favorites -- [options] [query]`

## Options
| Flag | Required | Description |
|------|----------|-------------|
| --add | One of operation | Add a new favorite player (requires: --name, --position, --team, --notes) |
| --list | One of operation | List all favorite players |
| --search | One of operation | Search players by description or attributes (requires: query argument) |
| --delete | One of operation | Delete a player by name (requires: --name) |
| --update | One of operation | Update a player's notes (requires: --name, --notes) |
| --export | One of operation | Export all players to JSON file (optional: --output) |
| --import | One of operation | Import players from JSON file (requires: --file) |
| --name | Depends on operation | Player full name |
| --position | With --add | Playing position (e.g., "Forward", "Midfielder", "Defender", "Goalkeeper") |
| --team | With --add | Current or former team |
| --notes | With --add or --update | Description, achievements, or notes about the player |
| --query | With --search | Search query for semantic search |
| -n, --n-results | No | Number of search results to return (default: 5) |
| -f, --format | No | Output format: text or json (default: text) |
| --db | No | Path to SQLite database (default: ./soccer_favorites.db) |

## Requirements
- `GOOGLE_AI_STUDIO_KEY` or `GEMINI_API_KEY` in `.env.local`
- Python 3.8+ with: sqlite3 (built-in), google-genai, python-dotenv
- `pip install google-genai python-dotenv` (if not already installed)

## Examples
```bash
# Add a new favorite player
npm run soccer-favorites -- --add --name "Cristiano Ronaldo" --position "Forward" --team "Al Nassr" --notes "Legendary Portuguese striker, 5x Ballon d'Or winner, exceptional free-kick taker and header specialist"

# List all favorite players
npm run soccer-favorites -- --list

# Search for players by description
npm run soccer-favorites -- --search "fast wingers who play for english clubs"

# Update a player's notes
npm run soccer-favorites -- --update --name "Messi" --notes "Argentine legend, 8x Ballon d'Or, incredible dribbler and playmaker"

# Delete a player
npm run soccer-favorites -- --delete --name "Ronaldo"

# Export to JSON
npm run soccer-favorites -- --export --output my_players.json

# Import from JSON
npm run soccer-favorites -- --import --file my_players.json

# Search with specific number of results
npm run soccer-favorites -- --search "defenders with strong tackling" -n 3

# JSON output format
npm run soccer-favorites -- --list -f json
```

## Features
- **SQLite Storage**: Persistent local database stored in the skill folder
- **Semantic Search**: Uses Gemini embeddings to find players by description or attributes
- **Rich Metadata**: Store player name, position, team, and detailed notes
- **Import/Export**: Backup and share favorite players as JSON
- **Flexible Queries**: Natural language search ("fast wingers", "defenders with great leadership")

## Data Structure
Each player record contains:
- `name`: Player full name (unique identifier)
- `position`: Playing position
- `team`: Current or former team
- `notes`: Rich description, achievements, skills
- `added_date`: When the player was added to favorites
- `embedding`: Vector embedding of player description for semantic search

## Database Location
Database is stored at: `.agents/skills/soccer-favorites/soccer_favorites.db`
