#!/usr/bin/env python3
"""
FPL Helper Agent CLI

An AI agent for Fantasy Premier League decision support. Provides recommendations on:
- Player transfers (buy/sell)
- Captain picks
- Chip strategy (when to play Wildcard, Free Hit, Bench Boost, Triple Captain)
- Injury and fixture insights

Usage:
  python fpl_helper.py --chat              # Interactive chat mode
  python fpl_helper.py "Who should I captain this week?"  # Single query
  python fpl_helper.py --help            # Show help
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agent_env import load_agent_environment

load_agent_environment()

from google import genai
from google.genai import types

AGENT_DIR = Path(__file__).parent
sys.path.insert(0, str(AGENT_DIR / "memory"))
sys.path.insert(0, str(AGENT_DIR / "tools"))
sys.path.insert(0, str(AGENT_DIR / "subagents"))

from memory import FPLMemory

DEFAULT_MODEL = "gemini-3-flash-preview"


def load_api_key() -> str:
    """Load Gemini API key from environment."""
    api_key = (
        os.environ.get("GOOGLE_AI_STUDIO_KEY") or
        os.environ.get("GEMINI_API_KEY") or
        os.environ.get("GOOGLE_API_KEY")
    )
    if not api_key:
        print("Error: API key not found. Set GOOGLE_AI_STUDIO_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY.")
        sys.exit(1)
    return api_key


def load_skills() -> str:
    """Load all skill files and return as context."""
    skills_dir = AGENT_DIR / "skills"
    skills_content = []

    if skills_dir.exists():
        for skill_file in skills_dir.glob("*.md"):
            try:
                with open(skill_file, "r") as f:
                    content = f.read()
                    skills_content.append(f"## Skill: {skill_file.stem}\n\n{content}")
            except Exception:
                pass

    return "\n\n---\n\n".join(skills_content) if skills_content else ""


def build_function_declarations() -> List[Dict[str, Any]]:
    """Build function declarations for the agent's tools."""
    return [
        {
            "name": "get_fpl_data",
            "description": "Fetch current FPL data from the official Fantasy Premier League API including player stats, team info, and fixtures",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_type": {
                        "type": "string",
                        "enum": ["players", "teams", "fixtures", "events", "all"],
                        "description": "Type of FPL data to fetch"
                    }
                },
                "required": ["data_type"]
            }
        },
        {
            "name": "get_player_info",
            "description": "Get detailed information about a specific player including form, fixtures, and stats",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {
                        "type": "string",
                        "description": "Player name (full or partial)"
                    },
                    "player_id": {
                        "type": "integer",
                        "description": "FPL player ID"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_injuries",
            "description": "Get current injury and suspension news from Premier League官方 sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "Filter by team name"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_captain_recommendations",
            "description": "Get captain picks based on form, fixtures, and ownership",
            "parameters": {
                "type": "object",
                "properties": {
                    "budget": {
                        "type": "number",
                        "description": "Maximum price in millions"
                    },
                    "position": {
                        "type": "string",
                        "enum": ["GK", "DEF", "MID", "FWD", "any"],
                        "description": "Player position filter"
                    },
                    "min_ownership": {
                        "type": "number",
                        "description": "Minimum ownership percentage"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_transfer_recommendations",
            "description": "Get recommended transfers (buy/sell) based on form, fixtures, and value",
            "parameters": {
                "type": "object",
                "properties": {
                    "budget": {
                        "type": "number",
                        "description": "Available transfer budget in millions"
                    },
                    "players_to_sell": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Players you're considering selling"
                    },
                    "focus": {
                        "type": "string",
                        "enum": ["form", "value", "fixtures", "any"],
                        "description": "Primary focus for recommendations"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_chip_advice",
            "description": "Get advice on when to use FPL chips (Wildcard, Free Hit, Bench Boost, Triple Captain)",
            "parameters": {
                "type": "object",
                "properties": {
                    "chips_available": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Chips still available"
                    },
                    "current_rank": {
                        "type": "integer",
                        "description": "Current overall rank"
                    },
                    "team_value": {
                        "type": "number",
                        "description": "Current team value"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_fixture_difficulty",
            "description": "Get fixture difficulty ratings for teams in upcoming gameweeks",
            "parameters": {
                "type": "object",
                "properties": {
                    "team": {
                        "type": "string",
                        "description": "Team name"
                    },
                    "gameweeks": {
                        "type": "integer",
                        "description": "Number of upcoming gameweeks (default: 5)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "save_squad",
            "description": "Save user's current squad for analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "squad_json": {
                        "type": "string",
                        "description": "Squad data as JSON string"
                    },
                    "players": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of player names in your squad"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_saved_squad",
            "description": "Get your saved squad for analysis",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "get_blog_posts",
            "description": "Get FPL-related blog posts and articles from Premier League official sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic to search for"
                    }
                },
                "required": []
            }
        }
    ]


def log_status(message: str):
    """Log a status message to stderr for UI streaming."""
    print(message, file=sys.stderr, flush=True)


def run_subagent(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Run a subagent and return its output."""
    log_status(f"Calling subagent: {name}")
    subagent_path = AGENT_DIR / "subagents" / f"{name}.py"

    if not subagent_path.exists():
        return {"error": f"Subagent not found: {name}"}

    cmd = ["python", str(subagent_path)]

    for key, value in args.items():
        if value is not None:
            # Map function parameter names to subagent argument names
            arg_name = key.replace('_', '-')
            if arg_name == "player-name":
                arg_name = "name"
            elif arg_name == "player-id":
                arg_name = "id"
            cmd.extend([f"--{arg_name}", str(value)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(AGENT_DIR)
        )

        if result.returncode == 0:
            log_status(f"Subagent {name} completed successfully")
            try:
                output = json.loads(result.stdout)
                return output
            except json.JSONDecodeError:
                return {"raw_output": result.stdout}
        else:
            # Return graceful failure
            log_status(f"Subagent {name} failed: {result.stderr[:100] if result.stderr else 'unknown error'}")
            return {"data": [], "error": f"{name} failed", "message": "Could not fetch data"}

    except subprocess.TimeoutExpired:
        log_status(f"Subagent {name} timed out")
        return {"data": [], "error": "Subagent timed out"}
    except Exception as e:
        log_status(f"Subagent {name} error: {str(e)}")
        return {"data": [], "error": str(e)}


def execute_function(name: str, args: Dict[str, Any], memory: FPLMemory) -> Dict[str, Any]:
    """Execute a function call and return results."""
    log_status(f"Executing function: {name}")

    if name == "get_fpl_data":
        data_type = args.get("data_type", "all")
        log_status(f"Fetching FPL data: {data_type}...")
        return run_subagent("fpl_fetcher", {"data_type": data_type})

    elif name == "get_player_info":
        log_status(f"Looking up player: {args.get('player_name', args.get('player_id'))}...")
        return run_subagent("player_lookup", args)

    elif name == "get_injuries":
        log_status("Fetching injury news...")
        return run_subagent("injury_news", args)

    elif name == "get_captain_recommendations":
        log_status("Calculating captain picks...")
        return build_captain_recommendations(args, memory)

    elif name == "get_transfer_recommendations":
        log_status("Analyzing transfers...")
        return build_transfer_recommendations(args, memory)

    elif name == "get_chip_advice":
        log_status("Analyzing chip strategy...")
        return build_chip_advice(args, memory)

    elif name == "get_fixture_difficulty":
        log_status("Calculating fixture difficulty...")
        return run_subagent("fixture_difficulty", args)

    elif name == "save_squad":
        log_status("Saving squad...")
        if args.get("squad_json"):
            squad = json.loads(args["squad_json"])
        else:
            squad = {"players": args.get("players", [])}
        return memory.save_squad(squad)

    elif name == "get_saved_squad":
        log_status("Loading saved squad...")
        return memory.get_squad()

    elif name == "get_blog_posts":
        log_status("Searching blog posts...")
        return run_subagent("blog_search", args)

    else:
        return {"error": f"Unknown function: {name}"}


def build_captain_recommendations(args: Dict[str, Any], memory: FPLMemory) -> Dict[str, Any]:
    """Build captain recommendations based on form and fixtures."""
    budget = args.get("budget", 13.0)
    position = args.get("position", "any")
    min_owner = args.get("min_ownership", 5)

    fpl_data = memory.get_fpl_cache()
    players = fpl_data.get("players", []) if fpl_data else []
    fixtures = fpl_data.get("fixtures", []) if fpl_data else []

    if not players:
        return {
            "recommendations": [],
            "message": "No FPL data available. Run get_fpl_data first."
        }

    scored = []
    for player in players:
        if position != "any" and player.get("element_type") != position:
            continue

        price = player.get("now_cost", 0) / 10.0
        if price > budget:
            continue

        owner = player.get("selected_by_percent", 0)
        if owner < min_owner:
            continue

        form = float(player.get("form", 0))
        total_pts = player.get("total_points", 0)
        pts_per_million = total_pts / price if price > 0 else 0

        team_id = player.get("team")
        fixture_score = calculate_fixture_score(team_id, fixtures)

        score = (form * 2.5) + (fixture_score * 2.0) + (pts_per_million * 0.3)

        scored.append({
            "player": player.get("web_name"),
            "team": player.get("team"),
            "price": price,
            "form": form,
            "total_points": total_pts,
            "ownership": owner,
            "fixture_score": fixture_score,
            "score": round(score, 2)
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = scored[:5]

    return {
        "captain_picks": top,
        "methodology": "Weighted by form (40%), fixture difficulty (40%), points per million (20%)"
    }


def build_transfer_recommendations(args: Dict[str, Any], memory: FPLMemory) -> Dict[str, Any]:
    """Build transfer recommendations."""
    budget = args.get("budget", 2.0)
    players_to_sell = args.get("players_to_sell", [])
    focus = args.get("focus", "any")

    fpl_data = memory.get_fpl_cache()
    players = fpl_data.get("players", []) if fpl_data else []

    if not players:
        return {
            "buy": [],
            "sell": [],
            "message": "No FPL data available. Run get_fpl_data first."
        }

    squad = memory.get_squad()
    current_players = squad.get("players", []) if squad else []

    sell_recs = []
    for name in current_players:
        for player in players:
            if player.get("web_name") == name:
                form = float(player.get("form", 0))
                if form < 4.0:
                    sell_recs.append({
                        "player": name,
                        "reason": f"Low form ({form})",
                        "priority": "high" if form < 2.0 else "medium"
                    })

    buy_recs = sorted(
        [p for p in players if p not in current_players],
        key=lambda x: float(x.get("form", 0)),
        reverse=True
    )[:5]

    return {
        "buy": [
            {
                "player": p.get("web_name"),
                "team": p.get("team"),
                "price": p.get("now_cost", 0) / 10.0,
                "form": p.get("form"),
                "reason": "High form and good fixtures"
            }
            for p in buy_recs
        ],
        "sell": sell_recs,
        "budget_remaining": budget
    }


def calculate_fixture_score(team_id: int, fixtures: List[Dict]) -> float:
    """Calculate fixture difficulty score for a team."""
    team_fixtures = [f for f in fixtures if f.get("team_h") == team_id or f.get("team_a") == team_id]

    if not team_fixtures:
        return 5.0

    scores = []
    for f in team_fixtures[:5]:
        if f.get("team_h") == team_id:
            diff = f.get("difficulty_h", 3)
        else:
            diff = f.get("difficulty_a", 3)
        scores.append(6 - diff)

    return sum(scores) / len(scores) if scores else 5.0


def build_chip_advice(args: Dict[str, Any], memory: FPLMemory) -> Dict[str, Any]:
    """Build chip strategy advice."""
    chips = args.get("chips_available", ["wildcard", "free_hit", "bench_boost", "triple_captain"])
    current_rank = args.get("current_rank", 0)
    team_value = args.get("team_value", 100)

    fpl_data = memory.get_fpl_cache()
    events = fpl_data.get("events", []) if fpl_data else []

    current_gw = 0
    for e in events:
        if e.get("is_current"):
            current_gw = e.get("id", 0)
            break

    dgw_gameweeks = [e.get("id") for e in events if e.get("is_double")]

    advice = {
        "wildcard": {
            "when": "Gameweek 32-35 (before final double gameweeks)",
            "reason": "Best used to set up for bench boost in DGW33 or DGW36"
        },
        "bench_boost": {
            "when": f"Gameweek {dgw_gameweeks[0]}" if dgw_gameweeks else "First double gameweek",
            "reason": "Use when 15 players have double fixtures"
        },
        "free_hit": {
            "when": "Blank gameweek (check fixture schedule)",
            "reason": "Cover blank weeks without affecting long-term squad"
        },
        "triple_captain": {
            "when": f"Gameweek {dgw_gameweeks[1]}" if len(dgw_gameweeks) > 1 else "Best double gameweek",
            "reason": "Use on premium player with 2 good fixtures"
        }
    }

    return {
        "current_gameweek": current_gw,
        "double_gameweeks": dgw_gameweeks,
        "advice": {c: advice.get(c, {}) for c in chips if c in advice},
        "strategy": "WC -> BB -> FH is the optimal chip sequence"
    }


def find_function_calls(response) -> List[Tuple[str, Dict[str, Any]]]:
    """Extract function calls from response."""
    calls = []
    try:
        parts = response.candidates[0].content.parts if response.candidates else []
        for part in parts:
            if hasattr(part, "function_call") and part.function_call:
                fc = part.function_call
                name = fc.name
                args = dict(fc.args) if fc.args else {}
                calls.append((name, args))
    except Exception:
        pass
    return calls


def truncate_response(result: Dict[str, Any], max_items: int = 50) -> Dict[str, Any]:
    """Truncate large responses to prevent token overflow."""
    # Handle case where result is already a list
    if isinstance(result, list):
        if len(result) > max_items:
            log_status(f"Truncated list from {len(result)} to {max_items} items")
            return {"data": result[:max_items], "count": len(result), "truncated": True}
        return {"data": result, "count": len(result)}
    
    # Handle non-dict types
    if not isinstance(result, dict):
        return {"result": result}
    
    truncated = {}
    
    for key, value in result.items():
        if isinstance(value, list) and len(value) > max_items:
            # Limit list responses to max_items
            truncated[key] = value[:max_items]
            truncated[f"{key}_truncated"] = True
            truncated[f"{key}_total_count"] = len(value)
            log_status(f"Truncated {key} from {len(value)} to {max_items} items")
        elif isinstance(value, dict):
            # Recursively truncate nested dicts
            if "data" in value and isinstance(value["data"], list):
                truncated[key] = {"data": value["data"][:max_items], "count": len(value["data"])}
            else:
                truncated[key] = value
        else:
            truncated[key] = value
    
    return truncated


def make_function_response(name: str, result: Dict[str, Any]) -> types.Part:
    """Create a function response part."""
    # Truncate large responses
    response_data = truncate_response(result, max_items=20)
    
    # Ensure response is a dictionary (wrap lists in a dict)
    if isinstance(response_data, list):
        response_data = {"data": response_data, "count": len(response_data)}
    elif not isinstance(response_data, dict):
        response_data = {"result": response_data}
    
    return types.Part(
        function_response=types.FunctionResponse(
            name=name,
            response=response_data
        )
    )


def build_system_prompt(prefs: Optional[Dict] = None) -> str:
    """Build the system prompt with skills and context."""
    skills = load_skills()

    squad_info = ""
    if prefs and prefs.get("players"):
        squad_info = f"""
## User's Squad
```json
{json.dumps(prefs, indent=2)}
```
"""

    today = datetime.now()
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    return f"""You are an FPL Helper Agent. Your job is to help FPL managers make better decisions.

## Today's Date
{weekdays[today.weekday()]}, {today.strftime('%Y-%m-%d')}

## Your Capabilities

1. **Fetch FPL Data**: Get current player stats, fixtures, teams from official FPL API
2. **Player Lookup**: Get detailed info on specific players
3. **Injury News**: Check current injury and suspension updates
4. **Captain Picks**: Recommend best captains based on form, fixtures, ownership
5. **Transfer Advice**: Recommend buy/sell based on value and form
6. **Chip Strategy**: Advise when to use Wildcard, Free Hit, Bench Boost, Triple Captain
7. **Fixture Analysis**: Show fixture difficulty ratings

## How to Work

1. **Gather Data First**: Always fetch current FPL data before making recommendations
2. **Check Injuries**: Review injury news as it affects decisions
3. **Analyze Form**: Look at recent performance (last 5 games)
4. **Consider Fixtures**: Factor in upcoming fixture difficulty
5. **Provide Context**: Explain WHY you're making each recommendation

## Key Behaviors

- **Be Data-Driven**: Base recommendations on stats and form, not gut feeling
- **Consider Value**: Factor in points-per-million, not just total points
- **Check Injuries**: NEVER recommend an injured player
- **Factor Fixtures**: Easy fixtures = higher expected points
- **Chip Timing**: WC -> BB -> FH is optimal sequence

## Workflow for "Who should I captain?"

1. Fetch current player data
2. Get fixture difficulty for each team
3. Filter by form (top performers)
4. Weight by ownership
5. Recommend top 3 with reasoning

{squad_info}
## Skills Reference

{skills}

## Response Style

- Present recommendations clearly (top 3-5 options)
- Show key stats for each recommendation
- Explain WHY each player is recommended
- Be specific about gameweek timing for chips"""


def print_response(response) -> str:
    """Print and return model response text."""
    text_parts = []
    try:
        if not response or not hasattr(response, 'candidates'):
            log_status(f"Response error: {response}")
            return ""
        
        if not response.candidates:
            log_status("No candidates in response")
            return ""
        
        candidate = response.candidates[0]
        if not hasattr(candidate, 'content'):
            log_status(f"Candidate has no content: {candidate}")
            return ""
        
        parts = candidate.content.parts if candidate.content else []
        log_status(f"Response has {len(parts)} parts")
        
        for i, part in enumerate(parts):
            log_status(f"  Part {i}: {type(part).__name__}")
            if hasattr(part, "text") and part.text:
                text_parts.append(part.text)
            elif hasattr(part, "function_call"):
                log_status(f"    Function call: {part.function_call.name}")
    except Exception as e:
        log_status(f"Error extracting response: {str(e)}")
        import traceback
        log_status(traceback.format_exc())
        return ""

    text = "\n".join(text_parts)
    if text:
        print(text)
    else:
        log_status("Warning: No text content in response")
    return text


async def run_chat_loop(client: genai.Client, model: str, memory: FPLMemory):
    """Run interactive chat loop."""
    print("FPL Helper Agent - Interactive Mode")
    print("=" * 45)
    print("Commands: 'exit' to quit, 'help' for commands")
    print()

    squad = memory.get_squad()
    if squad and squad.get("players"):
        print(f"Squad loaded: {len(squad.get('players', []))} players")
    else:
        print("Use 'squad' command to add your players")

    print()

    function_declarations = build_function_declarations()
    tools = [types.Tool(function_declarations=function_declarations)]

    system_prompt = build_system_prompt(squad)
    history: List[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=system_prompt)]),
        types.Content(role="model", parts=[types.Part(text="I'm ready to help you with your FPL decisions! Ask me about transfers, captain picks, or chip strategy.")])
    ]

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGood luck with your transfers!")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit", ":q", "/exit"}:
            print("Good luck!")
            break

        if user_input.lower() == "help":
            print("""
Available commands:
  captain           - Get captain recommendations
  transfers        - Get transfer advice
  chips             - Get chip strategy advice
  injuries          - Check injury news
  fixtures <team>   - Get fixture difficulty
  squad <players>   - Set your squad
  data              - Refresh FPL data
  exit              - Quit
            """)
            continue

        if user_input.lower() == "data":
            log_status("Refreshing FPL data...")
            result = execute_function("get_fpl_data", {"data_type": "all"}, memory)
            memory.cache_fpl_data(result)
            print(f"[Data refreshed: {len(result.get('players', []))} players]")
            continue

        history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))

        config = types.GenerateContentConfig(tools=tools)

        response = await client.aio.models.generate_content(
            model=model,
            contents=history,
            config=config
        )

        for _ in range(5):
            function_calls = find_function_calls(response)

            if not function_calls:
                break

            if response.candidates and response.candidates[0].content:
                history.append(response.candidates[0].content)

            function_responses = []
            for func_name, func_args in function_calls:
                print(f"\n[Executing: {func_name}]")
                result = execute_function(func_name, func_args, memory)

                if "captain_picks" in result:
                    print(f"[Captain picks: {len(result.get('captain_picks', []))}]")
                elif "buy" in result:
                    print(f"[Transfer analysis complete]")
                elif "players" in result:
                    print(f"[Players: {len(result.get('players', []))}]")
                elif "error" in result:
                    print(f"[Error: {result['error']}]")

                function_responses.append(make_function_response(func_name, result))

            history.append(types.Content(
                role="user",
                parts=function_responses
            ))

            response = await client.aio.models.generate_content(
                model=model,
                contents=history,
                config=config
            )

        print("\nAgent:", end=" ")
        print_response(response)

        if response.candidates and response.candidates[0].content:
            history.append(response.candidates[0].content)


def run_single_query(client: genai.Client, model: str, query: str, memory: FPLMemory):
    """Run a single query."""
    log_status(f"Processing query: {query[:50]}...")

    function_declarations = build_function_declarations()
    tools = [types.Tool(function_declarations=function_declarations)]

    squad = memory.get_squad()
    if squad:
        log_status(f"Loaded squad with {len(squad.get('players', []))} players")

    system_prompt = build_system_prompt(squad)
    contents = [
        types.Content(role="user", parts=[types.Part(text=system_prompt)]),
        types.Content(role="model", parts=[types.Part(text="Ready to help with FPL decisions.")]),
        types.Content(role="user", parts=[types.Part(text=query)])
    ]

    config = types.GenerateContentConfig(tools=tools)

    log_status("Sending request to Gemini API...")
    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
    except Exception as e:
        log_status(f"API request failed: {str(e)[:100]}")
        print(f"Error: Failed to get initial response: {e}")
        return
    
    log_status("Received initial response")

    max_iterations = 10  # Max function call loops
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        function_calls = find_function_calls(response)

        if not function_calls:
            # No more function calls, model provided text response
            break

        log_status(f"Processing function calls (iteration {iteration})...")

        if response.candidates and response.candidates[0].content:
            contents.append(response.candidates[0].content)

        function_responses = []
        for func_name, func_args in function_calls:
            result = execute_function(func_name, func_args, memory)
            function_responses.append(make_function_response(func_name, result))

        contents.append(types.Content(
            role="user",
            parts=function_responses
        ))

        # Keep only last 6 messages to prevent token overflow
        # (system + model responses + current turn)
        if len(contents) > 6:
            # Keep first message (system prompt) and last 5
            contents = [contents[0]] + contents[-5:]
            log_status(f"Trimmed conversation history to prevent token overflow")

        log_status("Continuing conversation...")
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
        except Exception as e:
            if "token count" in str(e).lower():
                log_status("Token limit reached, stopping iterations")
                break
            else:
                log_status(f"API error: {str(e)[:100]}")
                print(f"Error: {e}")
                return

    # If we hit max iterations and still have function calls, force text generation
    if iteration >= max_iterations:
        log_status(f"Hit max iterations ({max_iterations}), forcing text generation...")
        if response.candidates and response.candidates[0].content:
            contents.append(response.candidates[0].content)
        
        # Add a user message forcing text response
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text="Now provide your final recommendations and analysis without calling any more functions.")]
        ))
        
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig()  # No tools, forces text only
            )
        except Exception as e:
            log_status(f"Error forcing text generation: {str(e)[:100]}")

    log_status("Generating final response...")
    print_response(response)


def main():
    parser = argparse.ArgumentParser(
        description="FPL Helper - Fantasy Premier League Decision Support",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query to process (if not using --chat)"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Start interactive chat mode"
    )
    parser.add_argument(
        "--model", "-m",
        default=DEFAULT_MODEL,
        help=f"Gemini model to use (default: {DEFAULT_MODEL})"
    )

    args = parser.parse_args()

    if not args.chat and not args.query:
        parser.print_help()
        sys.exit(1)

    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    memory = FPLMemory()

    if args.chat:
        asyncio.run(run_chat_loop(client, args.model, memory))
    else:
        run_single_query(client, args.model, args.query, memory)


if __name__ == "__main__":
    main()