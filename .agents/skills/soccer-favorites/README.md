# Soccer Favorites RAG Memory Skill

A RAG-backed memory system for storing, retrieving, and semantically searching your favorite soccer players using SQLite and Gemini embeddings.

## Features

- **Persistent Storage**: SQLite database stored locally in the skill folder
- **Semantic Search**: Uses Gemini embeddings to find players by natural language queries
- **Rich Metadata**: Store player name, position, team, and detailed notes
- **Import/Export**: Backup and share your favorite players as JSON
- **RAG Integration**: Leverages Gemini API for intelligent embeddings and search

## Quick Start

```bash
# Add a new favorite player
npm run soccer-favorites -- --add --name "Messi" --position "Forward" --team "Inter Miami" --notes "Argentine legend, incredible dribbler and left-footed magician"

# List all your favorites
npm run soccer-favorites -- --list

# Search for players
npm run soccer-favorites -- --search "fast wingers"

# Export your collection
npm run soccer-favorites -- --export

# Import from backup
npm run soccer-favorites -- --import --file backup.json
```

## Usage Examples

### Adding Players

```bash
npm run soccer-favorites -- --add \
  --name "Lewandowski" \
  --position "Striker" \
  --team "Barcelona" \
  --notes "Polish striker with incredible goal-scoring consistency and positioning"
```

### Searching

The semantic search uses natural language to find similar players:

```bash
# Find defenders
npm run soccer-favorites -- --search "strong defenders with good ball distribution"

# Find athletic players
npm run soccer-favorites -- --search "fast runners with high stamina"

# Find creative players
npm run soccer-favorites -- --search "playmakers who create chances"
```

### Managing Your Collection

```bash
# Update a player's information
npm run soccer-favorites -- --update \
  --name "Messi" \
  --notes "Updated notes about the player"

# Delete a player
npm run soccer-favorites -- --delete --name "OldPlayer"

# List with JSON output
npm run soccer-favorites -- --list -f json

# Export with custom filename
npm run soccer-favorites -- --export --output my_players.json
```

## Database Schema

The SQLite database stores the following fields for each player:

```
players (table)
├── id (INTEGER, primary key)
├── name (TEXT, unique) - Player's full name
├── position (TEXT) - Playing position (Forward, Midfielder, Defender, Goalkeeper, etc.)
├── team (TEXT) - Current or former team
├── notes (TEXT) - Rich description, achievements, and attributes
├── added_date (TEXT) - ISO timestamp when added
└── embedding (BLOB) - Gemini embedding vector (stored as JSON)
```

## Configuration

The skill requires a Gemini API key set in `.env.local`:

```env
GEMINI_API_KEY=your-api-key-here
```

Or use `GOOGLE_AI_STUDIO_KEY` as an alternative.

## Database Location

The SQLite database is automatically created at:
```
.agents/skills/soccer-favorites/soccer_favorites.db
```

## Architecture

```
┌─────────────────────────────────────────┐
│     npm run soccer-favorites [options]   │
└────────────────┬────────────────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  CLI Argument Parsing   │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────┐
        │  SoccerFavoritesDB                     │
        │  (SQLite + Gemini Integration)         │
        └────────┬─────────────────┬─────────────┘
                 │                 │
        ┌────────▼──────┐  ┌──────▼────────────┐
        │  SQLite DB    │  │  Gemini API       │
        │ (persistent)  │  │ (embeddings)      │
        └───────────────┘  └───────────────────┘
```

## How It Works

1. **Adding Players**: When you add a player, the skill creates an embedding from the combined player metadata (name, position, team, notes)
2. **Semantic Search**: When searching, your query is embedded using the same Gemini model
3. **Similarity Matching**: The skill calculates cosine similarity between the query embedding and all stored player embeddings
4. **Results**: Players are ranked by similarity and returned in order

## API Reference

See [SKILL.md](./SKILL.md) for complete command-line reference.

## Requirements

- Python 3.8+
- `google-genai` package
- Gemini API key in `.env.local`
- SQLite3 (built-in with Python)

## Troubleshooting

### "GEMINI_API_KEY not set"
Make sure you have a `.env.local` file in the project root with your Gemini API key:
```env
GEMINI_API_KEY=sk-xxxxx
```

### "Player already exists"
Each player name must be unique. Delete the existing player first or use `--update` to modify.

### Database file not found
The database is created automatically on first run in the skill folder. Check permissions if this fails.

## Tips & Tricks

- **Detailed Notes Matter**: More detailed notes in the `--notes` field lead to better search results
- **Use Position Keywords**: Include position words ("forward", "midfielder", "defender") in notes for better semantic search
- **Export Regularly**: Use `--export` to backup your collection before major updates
- **JSON Format**: Use `-f json` output format for programmatic use

---

**Skill**: `soccer-favorites`  
**Database**: SQLite  
**Embeddings**: Gemini (models/embedding-001)  
**Status**: Production Ready
