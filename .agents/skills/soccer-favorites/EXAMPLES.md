# Soccer Favorites Skill — Usage Examples

This document demonstrates how to use the soccer-favorites skill to manage your collection of favorite soccer players.

## Basic Operations

### 1. Add Your First Player

```bash
npm run soccer-favorites -- --add \
  --name "Cristiano Ronaldo" \
  --position "Forward" \
  --team "Al Nassr" \
  --notes "Portuguese legend, 5x Ballon d'Or winner, exceptional free-kick taker and header specialist"
```

### 2. View Your Favorites

```bash
# Display all players with formatted output
npm run soccer-favorites -- --list

# Get JSON output (useful for scripting)
npm run soccer-favorites -- --list -f json
```

### 3. Semantic Search

The skill supports natural language search using AI embeddings:

```bash
# Find defenders
npm run soccer-favorites -- --search "strong defenders"

# Find creative midfielders
npm run soccer-favorites -- --search "midfielders who create goals"

# Find specific style players
npm run soccer-favorites -- --search "fast left-footed wingers"

# Search with custom result count
npm run soccer-favorites -- --search "goalkeepers with reflexes" -n 3
```

### 4. Update Player Information

```bash
npm run soccer-favorites -- --update \
  --name "Cristiano Ronaldo" \
  --notes "Portuguese GOAT, 5x Ballon d'Or, prolific goal scorer with incredible athleticism"
```

### 5. Remove a Player

```bash
npm run soccer-favorites -- --delete --name "Cristiano Ronaldo"
```

## Data Management

### Export Your Collection

```bash
# Export to default location (players_export.json)
npm run soccer-favorites -- --export

# Export to custom location
npm run soccer-favorites -- --export --output my_favorites.json

# Export and view the JSON
npm run soccer-favorites -- --export --output backup.json && cat backup.json
```

### Import from Backup

```bash
npm run soccer-favorites -- --import --file my_favorites.json
```

## Building a Collection

Here's a step-by-step example of building a collection:

```bash
# Add forwards
npm run soccer-favorites -- --add --name "Messi" --position "Forward" --team "Inter Miami" \
  --notes "Argentine genius, 8x Ballon d'Or, incredible dribbler and playmaker"

npm run soccer-favorites -- --add --name "Mbappé" --position "Forward" --team "PSG" \
  --notes "French speedster, explosive athleticism, prolific scorer"

# Add midfielders
npm run soccer-favorites -- --add --name "De Bruyne" --position "Midfielder" --team "Manchester City" \
  --notes "Belgian magician, incredible vision, one of the best playmakers in the world"

npm run soccer-favorites -- --add --name "Bellingham" --position "Midfielder" --team "Real Madrid" \
  --notes "Young English talent, athletic and technical, rising star in football"

# Add defenders
npm run soccer-favorites -- --add --name "Van Dijk" --position "Defender" --team "Liverpool" \
  --notes "Dutch colossus, incredible strength and positioning, leader on the pitch"

# View your collection
npm run soccer-favorites -- --list

# Backup your work
npm run soccer-favorites -- --export --output my_favorites_collection.json
```

## Semantic Search Examples

The skill uses AI embeddings to understand player descriptions and find similar players:

```bash
# Find strikers with specific skills
npm run soccer-favorites -- --search "target man strikers with aerial dominance"

# Find defenders by playing style
npm run soccer-favorites -- --search "intelligent defenders with ball distribution"

# Find creative players
npm run soccer-favorites -- --search "players who create chances and assist teammates"

# Find athletic players
npm run soccer-favorites -- --search "quick wingers with high endurance"

# Find leaders
npm run soccer-favorites -- --search "captains with leadership qualities"

# Find by team
npm run soccer-favorites -- --search "players from Premier League clubs"

# Find by era/style
npm run soccer-favorites -- --search "modern technical footballers"
```

## Database Information

- **Location**: `.agents/skills/soccer-favorites/soccer_favorites.db`
- **Type**: SQLite 3
- **Storage**: Local file-based (no external services needed except Gemini API for embeddings)
- **Persistence**: All players are saved locally and survive between sessions
- **Embeddings**: Stored as binary JSON blobs for semantic search

## Tips & Tricks

### 1. Write Detailed Notes

More detailed notes lead to better search results:

```bash
# BETTER: Detailed description
npm run soccer-favorites -- --add --name "Neymar" --position "Winger" --team "Al-Hilal" \
  --notes "Brazilian attacking midfielder/winger, exceptional dribbler, creative playmaker, known for flair and technical ability, plays both wings, strong finisher"

# LESS EFFECTIVE: Brief description
npm run soccer-favorites -- --add --name "Neymar" --position "Winger" --team "Al-Hilal" \
  --notes "Brazilian footballer"
```

### 2. Include Position and Team in Notes

```bash
# BETTER
npm run soccer-favorites -- --add --name "Haaland" --position "Forward" --team "Manchester City" \
  --notes "Tall Norwegian striker playing as center forward for Manchester City, lethal finisher, rapid acceleration, physical presence"

# The position and team help semantic search understand context
```

### 3. Use Consistent Terminology

```bash
# Use standard position names for better search:
# - Forward / Striker / Centre Forward
# - Winger / Left Wing / Right Wing
# - Midfielder / Central Midfielder / Box-to-Box
# - Defender / Centre Back / Full Back
# - Goalkeeper / Goalie
```

### 4. Backup Regularly

```bash
# Weekly backup
npm run soccer-favorites -- --export --output backups/favorites_$(date +%Y%m%d).json
```

### 5. Search Multiple Ways

```bash
# Same player can be found with different queries:

npm run soccer-favorites -- --search "Portuguese striker Al Nassr"
npm run soccer-favorites -- --search "free-kick specialist header"
npm run soccer-favorites -- --search "Ballon d'Or winner forward"
# All might find Cristiano Ronaldo due to semantic similarity
```

## Integration with Other Skills

You can combine the soccer-favorites skill with other skills:

```bash
# Export to file and then use with other tools
npm run soccer-favorites -- --export --output players.json

# Use the exported data with semantic-search or other processing
```

## Troubleshooting

### Issue: "Player already exists"
**Solution**: Each player name must be unique. Delete the existing player first:
```bash
npm run soccer-favorites -- --delete --name "Duplicate Player"
npm run soccer-favorites -- --add --name "Duplicate Player" ...
```

### Issue: Search returns no results
**Solution**: Make sure you have players added first:
```bash
npm run soccer-favorites -- --list  # Should show players
npm run soccer-favorites -- --search "any query"
```

### Issue: Database file not found
**Solution**: The database is created automatically on first use. If it doesn't exist:
```bash
# Run any command to initialize the database
npm run soccer-favorites -- --list
```

### Issue: API key error
**Solution**: Make sure your `.env.local` file contains:
```env
GEMINI_API_KEY=your-api-key-here
```

Or use `GOOGLE_AI_STUDIO_KEY` as an alternative.

---

**Last Updated**: April 21, 2026  
**Skill Version**: 1.0  
**Status**: Production Ready
