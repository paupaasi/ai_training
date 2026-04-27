# FPL Helper Agent 🏴󠁧󠁢󠁥󠁮󠁧󠁿⚽

**AI-powered Fantasy Premier League decision support and recommendations**

An intelligent agent that helps you make better Fantasy Premier League decisions through real-time data analysis, player recommendations, and strategic guidance.

---

## 📋 Overview

The FPL Helper Agent is an AI assistant designed to help Fantasy Premier League managers:

- **Transfer Decisions** — Get buy/sell recommendations based on form, fixtures, and value
- **Captain Picks** — Find the best captain choice for each gameweek
- **Chip Strategy** — Decide when to use Wildcard, Free Hit, Bench Boost, or Triple Captain
- **Injury & News** — Stay updated on player injuries and suspensions
- **Player Analysis** — Deep dive into player stats, fixtures, and form
- **Fixture Analysis** — Evaluate upcoming fixture difficulty for all teams
- **Squad Optimization** — Improve your squad composition and value

Powered by **Gemini AI**, the agent uses real FPL data and expert analysis to provide actionable advice.

---

## 🚀 Quick Start

### Installation

```bash
# Navigate to the agent directory
cd session-3-ai-agents/agents/fpl-helper

# Install dependencies (requires Python 3.9+)
pip install -r requirements.txt

# Or with uv (recommended)
uv pip install -r requirements.txt
```

### Setup API Key

The agent requires a **Google Gemini API key**. Set it in one of these ways:

**Option 1: Environment Variable (Recommended)**
```bash
export GOOGLE_AI_STUDIO_KEY="your-api-key"
# Or
export GEMINI_API_KEY="your-api-key"
# Or
export GOOGLE_API_KEY="your-api-key"
```

**Option 2: .env File**
Create `.env` in the `fpl-helper/` directory:
```
GOOGLE_AI_STUDIO_KEY=your-api-key
```

**Get your API key:** https://aistudio.google.com/app/apikey

### First Query

```bash
python fpl_helper.py "Who should I captain this week?"
```

You should see a response with captain recommendations!

---

## 📖 Usage

### Mode 1: Single Query (Recommended for Scripting)

Ask a specific question and get a response:

```bash
python fpl_helper.py "What are the key player stats I should monitor?"
python fpl_helper.py "Who are the best value midfielders right now?"
python fpl_helper.py "Should I use my Wildcard this week?"
```

**Advantages:**
- Fast response
- Easy to script and automate
- Perfect for specific questions
- Can save output to files

### Mode 2: Interactive Chat Mode

Have a conversation with the agent:

```bash
python fpl_helper.py --chat
```

**Advantages:**
- Multi-turn conversations
- Ask follow-up questions
- Context is maintained across turns
- More natural interaction

**Example chat session:**
```
> Who should I captain?
[Agent provides captain options]

> Tell me more about Haaland's upcoming fixtures
[Agent analyzes Haaland's fixtures]

> What's my best transfer option?
[Agent recommends a transfer]

> quit
```

### Display Help

```bash
python fpl_helper.py --help
```

---

## 🎯 Example Queries

The agent can handle many types of queries. Here are some examples:

### Captain & Squad

```bash
python fpl_helper.py "Who should I captain this week?"
python fpl_helper.py "Should I captain Haaland or Salah?"
python fpl_helper.py "Who's the best differential captain?"
python fpl_helper.py "Analyze my squad: Salah, Haaland, Foden, Saka"
```

### Transfers & Value

```bash
python fpl_helper.py "Who should I sell? I have Salah, Son, and Mitoma"
python fpl_helper.py "Best value players under 7m?"
python fpl_helper.py "Should I downgrade Haaland to fund a better midfielder?"
python fpl_helper.py "Who's the best replacement for an injured player?"
```

### Fixtures & Form

```bash
python fpl_helper.py "Which teams have the easiest fixtures?"
python fpl_helper.py "Show me the fixture difficulty for the next 5 gameweeks"
python fpl_helper.py "Who's in good form right now?"
python fpl_helper.py "Which players are returning from injury?"
```

### Strategy & Chips

```bash
python fpl_helper.py "When should I use my Wildcard?"
python fpl_helper.py "Is this a good week to Free Hit?"
python fpl_helper.py "Should I use Triple Captain on Haaland?"
python fpl_helper.py "What's my chip strategy for the Double Gameweek?"
```

### Analysis & Stats

```bash
python fpl_helper.py "What stats should I monitor when choosing players?"
python fpl_helper.py "Explain Expected Goals (xG) and why it matters"
python fpl_helper.py "How does ownership affect my decision-making?"
python fpl_helper.py "What's the difference between form and fixtures?"
```

---

## 🔧 Features & Capabilities

### Core Functions

| Feature | Description | Example |
|---------|-------------|---------|
| **Player Lookup** | Find players by name, position, team | "Find all MID players under 8m" |
| **Transfer Recommendations** | Get buy/sell suggestions | "Who should I transfer in?" |
| **Captain Analysis** | Best captain picks based on form/fixtures | "Who should I captain?" |
| **Chip Strategy** | When to use special chips | "When should I use my Wildcard?" |
| **Injury News** | Current injury and suspension updates | "Who's injured this week?" |
| **Fixture Analysis** | Team fixture difficulty ratings | "Show me tough fixtures" |
| **Form Analysis** | Player recent performance trends | "Which forwards are in form?" |
| **Value Metrics** | Points per million and efficiency | "Best value defenders?" |

### Data Analysis

The agent analyzes:

- **Expected Goals (xG)** — Quality of chances
- **Expected Assists (xA)** — Quality of passes
- **Form Metrics** — 3-5 gameweek averages
- **Fixture Difficulty** — Next 5 gameweeks
- **Ownership %** — Differential vs safety
- **Points Per Million (PPM)** — Value efficiency
- **ICT Index** — All-in-one player score

### Integration Points

- **FPL Official API** — Real player data and stats
- **Memory System** — Persists your squad and decisions
- **Subagents** — Specialized analysis tools
- **Skills System** — Reusable knowledge modules

---

## 📁 Directory Structure

```
fpl-helper/
├── README.md                    # This file
├── fpl_helper.py               # Main agent CLI
├── agent_env.py                # Environment setup
├── requirements.txt            # Python dependencies
│
├── memory/                     # Agent memory & persistence
│   ├── __init__.py
│   ├── fpl_memory.py          # Squad & decision memory
│   └── cache.py               # Data caching
│
├── skills/                     # Agent skills/knowledge
│   ├── fpl_stats.md           # FPL statistics guide
│   ├── transfer_strategy.md   # Transfer decision framework
│   ├── chip_guide.md          # Chip usage guide
│   └── fixture_analysis.md    # Fixture evaluation
│
├── subagents/                  # Specialized sub-agents
│   ├── fpl_fetcher.py         # Fetch FPL data
│   ├── player_lookup.py       # Search players
│   ├── fixture_difficulty.py  # Fixture analysis
│   └── transfer_advisor.py    # Transfer recommendations
│
├── api/                        # API integrations
│   └── fpl_client.py          # FPL API wrapper
│
├── tools/                      # Utility tools
│   ├── data_processor.py      # Data transformation
│   └── formatter.py           # Output formatting
│
├── ui/                         # User interface
│   ├── cli.py                 # CLI interface
│   └── chat.py                # Chat mode
│
└── tests/                      # Test suite (13 tests)
    ├── run_tests.py           # Test runner
    ├── test_memory.py
    ├── test_fpl_fetcher.py
    ├── test_player_lookup.py
    ├── test_fixture_difficulty.py
    └── test_integration.py
```

---

## 🧪 Testing

The agent includes a comprehensive test suite with **13 passing tests**.

### Run All Tests

```bash
# From fpl-helper directory
python tests/run_tests.py
```

**Expected output:**
```
======================================================================
FINAL SUMMARY
======================================================================
Total test groups: 5
Passed: 13
Failed: 0
Errors: 0

✓ All tests PASSED
```

### Run Specific Tests

```bash
# Test memory system
python tests/test_memory.py

# Test FPL data fetching
python tests/test_fpl_fetcher.py

# Test player lookup
python tests/test_player_lookup.py

# Test fixture analysis
python tests/test_fixture_difficulty.py

# Test integration
python tests/test_integration.py
```

---

## 🔐 Environment Configuration

### Automatic Env Loading

The agent automatically loads environment variables from:

1. `fpl-helper/.env.local` (highest priority)
2. `fpl-helper/.env`
3. `session-3-ai-agents/.env`
4. `ai_training/.env` (lowest priority)

Later files override earlier ones, so local `.env.local` takes precedence.

### Required Variables

```bash
# API Key (Required - one of these)
GOOGLE_AI_STUDIO_KEY=your-key
GEMINI_API_KEY=your-key
GOOGLE_API_KEY=your-key
```

### Optional Variables

```bash
# Model selection
FPL_AGENT_MODEL=gemini-3-flash-preview  # or gemini-2-flash, etc.

# API endpoints
FPL_API_BASE=https://fantasy.premierleague.com/api/

# Cache settings
FPL_CACHE_TTL=3600  # seconds
```

---

## 💡 Tips & Tricks

### Tip 1: Save Your Squad

Store your squad for analysis:

```bash
python fpl_helper.py --chat
> Save my squad: Salah, Haaland, Foden, Saka, Van Dijk
> Analyze my squad
> Who should I transfer out?
```

### Tip 2: Interactive Exploration

Use chat mode to explore multiple scenarios:

```bash
python fpl_helper.py --chat
> Who's the best captain this week?
> What if I captain Foden instead?
> Show me both captains' fixtures
> Which has better odds?
```

### Tip 3: Batch Queries

Run multiple queries in a script:

```bash
#!/bin/bash
echo "=== THIS WEEK'S CAPTAIN ==="
python fpl_helper.py "Who should I captain?"

echo "=== TRANSFER RECOMMENDATION ==="
python fpl_helper.py "Best transfer for my budget?"

echo "=== FIXTURE ANALYSIS ==="
python fpl_helper.py "Which teams have easy fixtures?"
```

### Tip 4: Save Output

```bash
python fpl_helper.py "Detailed squad analysis" > analysis.txt
python fpl_helper.py --chat > chat_log.txt
```

---

## 🐛 Troubleshooting

### Issue: "API key not found"

**Solution:** Set one of these environment variables:
```bash
export GOOGLE_AI_STUDIO_KEY="your-api-key"
# or
export GEMINI_API_KEY="your-api-key"
```

Then retry:
```bash
python fpl_helper.py "Test query"
```

### Issue: "No module named 'google'"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Subagent timed out"

**Solution:** The FPL API might be slow. Retry:
```bash
python fpl_helper.py "Your query"
```

If persistent, check internet connection and FPL API status.

### Issue: "Memory file not found"

**Solution:** The memory system creates files automatically. Ensure write permissions:
```bash
ls -la fpl-helper/memory/
chmod 755 fpl-helper/memory/
```

### Issue: Chat mode not responsive

**Solution:** Exit and restart:
```bash
# Press Ctrl+C or type: quit
python fpl_helper.py --chat
```

---

## 📊 Performance & Data

### Data Sources

- **FPL Official API** — Real-time player stats, fixtures, events
- **Premier League Data** — Injury news, suspensions, fixtures
- **Agent Memory** — Your squad history, past decisions

### Response Time

- **Single Query:** 5-15 seconds (API + AI analysis)
- **Chat Mode:** 3-10 seconds per turn (with context)
- **First Run:** ~15-20 seconds (initial data fetch)

### Caching

The agent caches data to speed up subsequent queries:
- Player data: 1 hour
- Fixture data: 2 hours
- Team data: 1 hour

Clear cache if you need fresh data:
```bash
rm -rf fpl-helper/memory/cache/
```

---

## 🚀 Advanced Usage

### Use in Python Scripts

```python
import subprocess
import json

def ask_fpl_agent(query):
    """Ask the FPL agent a question from Python."""
    result = subprocess.run(
        ["python", "fpl_helper.py", query],
        capture_output=True,
        text=True,
        cwd="session-3-ai-agents/agents/fpl-helper"
    )
    return result.stdout

# Example
print(ask_fpl_agent("Who should I captain?"))
```

### Custom Skills

Add custom skills in `skills/`:

```markdown
# Custom Skill: Advanced Differential Strategy

## Overview
Find high-upside differential players with good fixture run.

## Analysis Points
1. Ownership < 5%
2. Upcoming 3 fixtures avg difficulty < 2.5
3. Recent form trend positive
```

### Memory Persistence

The agent remembers:
- Your saved squads
- Past transfer decisions
- Captain picks by gameweek
- Analysis history

Access memory:
```bash
python fpl_helper.py "What was my squad last week?"
python fpl_helper.py "Who did I captain in GW10?"
```

---

## 📚 Learning Resources

### FPL Concepts

- **xG (Expected Goals)** — Measures quality of chances a player creates/receives
- **Form** — Average points over last 3-5 gameweeks
- **Fixture Difficulty (FDR)** — Rated 1-5 (1=easy, 5=hard)
- **Ownership %** — Percentage of players who own this player
- **PPM (Points Per Million)** — Efficiency metric (higher = better value)

### Strategy Guides (Built-in)

```bash
# Learn about stats
python fpl_helper.py "What stats should I monitor?"

# Understand chips
python fpl_helper.py "When should I use my Wildcard?"

# Value optimization
python fpl_helper.py "How do I find value in FPL?"
```

---

## 📧 Support & Feedback

If you encounter issues or have suggestions:

1. Check [Troubleshooting](#-troubleshooting) section
2. Review test output: `python tests/run_tests.py`
3. Check agent logs for detailed error messages
4. Verify API key and internet connection

---

## 📄 License

This agent is part of the AI Training project.

---

## 🎯 Next Steps

1. **Set up your API key** → [API Key Setup](#-environment-configuration)
2. **Try your first query** → `python fpl_helper.py "Who should I captain?"`
3. **Explore chat mode** → `python fpl_helper.py --chat`
4. **Save your squad** → Ask the agent to remember your team
5. **Run the tests** → Ensure everything works: `python tests/run_tests.py`

**Happy FPL managing! ⚽** 🏆
