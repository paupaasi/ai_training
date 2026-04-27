# Activity Selection Agent - Complete System

A family-oriented AI agent that helps find personalized, age-appropriate activities in any city. Uses Gemini's integrated tools (Google Search, URL Context) with persistent memory for learning preferences.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  activity_agent.py (Main Orchestrator)                     │
│  - Uses: gemini-3-flash-preview (ONLY)                     │
│  - Loads: Skills + Family Profile → System Prompt         │
│  - Manages: Chat loop, function calls, iterations         │
│  - Delegates: Subagents via subprocess                    │
└─────────────────────────────────────────────────────────────┘
       ↓                ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Subagents    │  │ Tools        │  │ Memory/Util  │
├──────────────┤  ├──────────────┤  ├──────────────┤
│search        │  │store_activity│  │memory.py     │
│enrich        │  │retrieve_acti │  │              │
│              │  │              │  │              │
│Models:       │  │Models:       │  │Uses:         │
│3.1-lite-     │  │3.1-lite-     │  │ ChromaDB     │
│preview       │  │preview       │  │ + JSON       │
│              │  │              │  │ fallback     │
└──────────────┘  └──────────────┘  └──────────────┘
       ↓                ↓
    Google Search    SQLite/Postgres
    + URL Context    + Gemini
                     Embeddings
```

## Files Overview

### Core Agent
- **`activity_agent.py`** (810 lines) — Main orchestrator
  - CLI with `--chat` (interactive) or query modes
  - 7 function declarations for Gemini tool calling
  - System prompt injection with family profile + skills
  - Subagent delegation via subprocess (120s timeout)
  - Chat loop with up to 5 function-call iterations
  - **Model**: `gemini-3-flash-preview` (REQUIRED - no other models)

### Environment & Configuration
- **`agent_env.py`** — Loads API key and .env files from directory tree
- **`requirements.txt`** — 24 Python dependencies (google-genai, chromadb, fastapi, etc.)

### Subagents (Run separately via subprocess)
- **`subagents/activity_search.py`** — Find activities in a city
  - Uses Google Search + URL Context
  - Returns: activities[], search_summary, sources, search_queries
  - **Model**: `gemini-3.1-flash-lite-preview` (enforced)

- **`subagents/activity_enrich.py`** — Extract details from website
  - Extracts: hours, pricing, facilities, age-suitability
  - Uses URL Context + Google Search as fallback
  - **Model**: `gemini-3.1-flash-lite-preview` (enforced)

### Memory & Storage
- **`memory/memory.py`** — Persistent storage with ChromaDB + JSON fallback
  - Collections: family_profile, activities, visit_history, preferences
  - Semantic search via Gemini embeddings (768-dim)
  - Family profile and activity history
  - **Methods**: get/set_family_profile(), store_activity(), get_activities(), record_visit(), search_activities()

- **`tools/store_activity.py`** — SQLite/PostgreSQL storage
  - Insert or replace activities with 27 columns
  - Handles JSON fields (cost_info, opening_hours, facilities)
  - **Methods**: store(activity), close()

- **`tools/retrieve_activities.py`** — Query activities with filters
  - Filters: city, category, status, toddler_friendly, stroller_friendly, min_rating
  - Pagination support
  - **Methods**: get_by_id(), get_all(), query()

### Data Schemas (JSON)
- **`memory/family_profile_schema.json`** — Family definition (members, preferences)
- **`memory/activity_schema.json`** — Activity details (30+ fields)
- **`memory/data/family_profile.json`** — Pre-filled default profile

### Skills (Markdown Documentation)
- **`skills/activity-search.md`** — When/how to search for activities
- **`skills/enrichment.md`** — How to extract details from websites
- **`skills/recommendations.md`** — Personalization & scoring algorithm

## Quick Start

### 1. Setup Environment

```bash
# Navigate to agent directory
cd session-3-ai-agents/agents/activity-selection-agent

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set API Key

```bash
# Any of these work:
export GOOGLE_AI_STUDIO_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"

# Or create .env file:
echo "GOOGLE_API_KEY=your-key-here" > .env
```

### 3. Run Agent

```bash
# Interactive chat mode
python3 activity_agent.py --chat

# Single query
python3 activity_agent.py "Find playgrounds in Helsinki"

# With custom profile
python3 activity_agent.py --profile my_family.json "What's fun today?"
```

## Function Declarations (7 Tools Available)

| Function | Purpose | Subagent | Returns |
|----------|---------|----------|---------|
| `search_activities` | Find activities in city | activity_search | activities[], sources |
| `enrich_activity` | Get hours/pricing/facilities | activity_enrich | enriched activity data |
| `store_activity` | Save activity to DB | store_activity tool | {status, activity_id} |
| `retrieve_activities` | Query activities by filter | retrieve_activities tool | activities[] |
| `get_family_profile` | Get current preferences | memory.py | family profile |
| `update_family_profile` | Update preferences | memory.py | {status} |
| `record_visit` | Log visit + rating | memory.py | {status} |

## Model Enforcement

**CRITICAL:** Model names are strictly enforced:

- **Main Agent MUST use**: `gemini-3-flash-preview`
  - Located in: `activity_agent.py` line ~85 (DEFAULT_MODEL)
  - No alternatives permitted

- **Subagents MUST use**: `gemini-3.1-flash-lite-preview`
  - Search agent: `subagents/activity_search.py` line ~40
  - Enrich agent: `subagents/activity_enrich.py` line ~40
  - No alternatives permitted

The code validates model names at runtime (subagent CLI will fail if wrong model specified).

## System Prompt Structure

The main agent builds its system prompt dynamically:

1. **Base Instructions** — Role, capabilities, how to work
2. **Skills Injection** — All 3 markdown files loaded from `skills/` directory
3. **Family Profile Context** — Current preferences, member ages, budget, location
4. **Response Style Guide** — Warmth, clarity, personalized recommendations

Example:
```
You are an Activity Selection Agent for families...

## Skills Reference
[activity-search.md content]
[enrichment.md content]
[recommendations.md content]

## Family Profile
- Home City: Helsinki
- Family Members: Parent1 (35yo), Parent2 (34yo), Son (2yo)
- Preferences: playground, park, nature, indoor_play...
```

## Data Flow - Typical Request

```
User: "Find toddler-friendly playgrounds in Helsinki"
  ↓
Main Agent (activity_agent.py)
  - Builds system prompt with family profile
  - Calls Gemini → function_call: search_activities
  ↓
Subprocess: activity_search.py --city Helsinki --age 2
  - Uses Google Search + URL Context
  - Returns: [{id, name, url, category}, ...]
  ↓
Main Agent receives results
  - User asks: "Get the hours for that first one?"
  - Calls: enrich_activity with URL
  ↓
Subprocess: activity_enrich.py --url https://...
  - Extracts: opening_hours, pricing, facilities
  - Returns: enriched activity
  ↓
Main Agent
  - Stores activity via store_activity tool
  - Updates memory
  - Recommends next activities based on family profile
```

## Memory Persistence

Activities are stored in **two systems**:

1. **SQLite (primary)** — Fast queries, reliable storage
   - Location: `memory/data/activities.db`
   - Schema: 27 columns (id, name, city, category, hours, pricing, facilities, ratings, etc.)

2. **JSON Fallback** — Works without database setup
   - Location: `memory/data/activities.json`
   - Auto-synced with SQLite

**Family Profile** stored in:
- Location: `memory/data/family_profile.json`
- Loaded at startup, updated via `update_family_profile` function

**Semantic Search** (via ChromaDB):
- Collections: activities, family_profile, visit_history
- Fallback: JSON file if ChromaDB not available
- Embeddings: Gemini embedding-001 (768-dim)

## Testing the Agent

### 1. Basic Query Test

```bash
python3 activity_agent.py "What playgrounds are in Helsinki suitable for a 2-year-old?"
```

Expected output:
- List of playgrounds with names, descriptions, websites
- Offer to get more details (hours, pricing)

### 2. Interactive Test

```bash
python3 activity_agent.py --chat
```

Try:
- "Find swimming pools in Barcelona"
- "Enrich that first one" (will extract hours/pricing)
- "Show my profile" 
- "Update my budget to free"
- "Record a visit - that was amazing!"

### 3. Recommendation Test

```bash
python3 activity_agent.py "Based on my preferences, what should we do this weekend?"
```

Expected behavior:
- Agent retrieves family profile
- Gets visit history
- Applies recommendation scoring
- Suggests top 3 activities matching family

## Customization Points

### Change Default Home City
Edit `memory/data/family_profile.json`:
```json
{
  "home_city": "Barcelona",
  "home_country": "ES"
}
```

### Change Supported Categories
Edit `memory/activity_schema.json` enum for `category` field:
```json
"category": {
  "enum": ["playground", "museum", "zoo", "swimming", "nature", ...custom...]
}
```

### Adjust Recommendation Scoring
Edit `skills/recommendations.md` formula and weights

### Adjust Search Behavior
Edit `subagents/activity_search.py` system prompt and search queries

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not found" | Set GOOGLE_API_KEY environment variable |
| Subagent timeout (120s) | Activity search taking too long; check internet connection |
| No activities found | Try broader search term or different city |
| Memory not persisting | Check write permissions on `memory/data/` directory |
| Model error | Verify exact model names: main=`gemini-3-flash-preview`, subagents=`gemini-3.1-flash-lite-preview` |
| Import errors | Ensure venv is activated and requirements.txt installed |

## Next Phase: API & Web UI (Phase 6)

Phase 6 will add:
- **FastAPI REST endpoints** for programmatic access
- **Flask web UI** with dashboard and search interface
- **WebSocket support** for real-time activity feeds
- **User authentication** (optional)

Both will delegate to the main agent (activity_agent.py) for all logic.

## Statistics

| Metric | Count |
|--------|-------|
| Python files | 13 |
| Total lines of code | ~2,800 |
| Function declarations | 7 |
| Subagents | 2 |
| Tools | 2 |
| Skill documents | 3 |
| Data schemas | 2 |
| Dependencies | 24 |
| Main agent model | gemini-3-flash-preview |
| Subagent model | gemini-3.1-flash-lite-preview |

## References

- Gemini API Docs: https://ai.google.dev/gemini-api
- Activity Schema: [memory/activity_schema.json](memory/activity_schema.json)
- Family Profile Schema: [memory/family_profile_schema.json](memory/family_profile_schema.json)
- Skills Documentation: [skills/](skills/)
