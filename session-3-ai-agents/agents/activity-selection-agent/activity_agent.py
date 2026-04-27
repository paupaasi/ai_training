#!/usr/bin/env python3
"""
Activity Selection Agent CLI

An AI agent for finding personalized family-friendly activities based on 
location, preferences, and past visits. Uses Gemini's integrated tools 
(Google Search, URL Context) along with subagent delegation.

Usage:
  # Interactive chat mode
  python activity_agent.py --chat

  # Single query
  python activity_agent.py "Find playgrounds in Helsinki"

  # With custom family profile
  python activity_agent.py --profile family_profile.json "Recommend activities for this weekend"

  # Show help
  python activity_agent.py --help
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

# Add local modules to path
AGENT_DIR = Path(__file__).parent
sys.path.insert(0, str(AGENT_DIR / "memory"))
sys.path.insert(0, str(AGENT_DIR / "tools"))
sys.path.insert(0, str(AGENT_DIR / "subagents"))

from memory import MemoryStore

# Configuration
DEFAULT_MODEL = "gemini-3-flash-preview"
MAX_CHAT_ITERATIONS = 5


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
        for skill_file in sorted(skills_dir.glob("*.md")):
            try:
                with open(skill_file, "r") as f:
                    content = f.read()
                    skills_content.append(content)
            except Exception:
                pass
    
    return "\n\n---\n\n".join(skills_content) if skills_content else ""


def build_function_declarations() -> List[Dict[str, Any]]:
    """Build function declarations for the agent's tools."""
    return [
        {
            "name": "search_activities",
            "description": "Search for family-friendly activities in a specified city. Uses Google Search and website analysis. Returns activities with basic info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City to search in (e.g., 'Helsinki', 'Barcelona', 'London')"
                    },
                    "category": {
                        "type": "string",
                        "description": "Activity category to filter by (e.g., 'playground', 'museum', 'swimming', 'nature')"
                    },
                    "age": {
                        "type": "integer",
                        "description": "Child age for age-appropriate recommendations (default: 2)"
                    },
                    "custom_query": {
                        "type": "string",
                        "description": "Custom search query for specific needs"
                    }
                },
                "required": ["city"]
            }
        },
        {
            "name": "enrich_activity",
            "description": "Extract detailed information from an activity's website: opening hours, pricing, facilities, age suitability. Requires a website URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "activity_id": {
                        "type": "string",
                        "description": "ID of activity to enrich"
                    },
                    "name": {
                        "type": "string",
                        "description": "Activity name"
                    },
                    "website": {
                        "type": "string",
                        "description": "Activity website URL (required)"
                    }
                },
                "required": ["website"]
            }
        },
        {
            "name": "store_activity",
            "description": "Store an activity to the local database for future reference and recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "activity_json": {
                        "type": "string",
                        "description": "Full activity data as JSON string"
                    }
                },
                "required": ["activity_json"]
            }
        },
        {
            "name": "retrieve_activities",
            "description": "Retrieve activities from the database with optional filters",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Filter by city"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["new", "enriched", "visited", "favorite", "skipped"],
                        "description": "Filter by status"
                    },
                    "toddler_friendly": {
                        "type": "boolean",
                        "description": "Filter for toddler-friendly only"
                    },
                    "stroller_friendly": {
                        "type": "boolean",
                        "description": "Filter for stroller-friendly only"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Max results to return (default: 20)"
                    }
                },
                "required": []
            }
        },
        {
            "name": "get_family_profile",
            "description": "Get the current family profile with preferences and composition",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "update_family_profile",
            "description": "Update family profile settings (home city, preferences, budget, etc.)",
            "parameters": {
                "type": "object",
                "properties": {
                    "home_city": {
                        "type": "string",
                        "description": "Home city"
                    },
                    "home_country": {
                        "type": "string",
                        "description": "Home country code (e.g., FI, US)"
                    },
                    "budget_preference": {
                        "type": "string",
                        "enum": ["free", "budget", "moderate", "any"],
                        "description": "Budget preference"
                    },
                    "preferred_categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Preferred activity categories"
                    },
                    "indoor_outdoor_preference": {
                        "type": "string",
                        "enum": ["indoor", "outdoor", "both"],
                        "description": "Indoor/outdoor preference"
                    },
                    "max_travel_minutes": {
                        "type": "integer",
                        "description": "Maximum willing travel time in minutes"
                    }
                },
                "required": []
            }
        },
        {
            "name": "record_visit",
            "description": "Record a visit to an activity with rating and notes for future recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "activity_id": {
                        "type": "string",
                        "description": "Activity ID that was visited"
                    },
                    "rating": {
                        "type": "integer",
                        "description": "Rating 0-5 (5 = excellent, 0 = didn't work)"
                    },
                    "notes": {
                        "type": "string",
                        "description": "Notes about the visit (what went well, what to improve)"
                    }
                },
                "required": ["activity_id"]
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
    
    cmd = ["python3", str(subagent_path)]
    
    # Build command arguments based on subagent
    if name == "activity_search":
        if args.get("city"):
            cmd.extend(["--city", args["city"]])
        if args.get("category"):
            cmd.extend(["--category", args["category"]])
        if args.get("age"):
            cmd.extend(["--age", str(args["age"])])
        if args.get("custom_query"):
            cmd.extend(["--query", args["custom_query"]])
        cmd.append("--pretty")
    
    elif name == "activity_enrich":
        if args.get("website"):
            cmd.extend(["--url", args["website"]])
        if args.get("name"):
            cmd.extend(["--name", args["name"]])
        cmd.append("--pretty")
    
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
                # Log summary of results
                if "activities" in output:
                    count = len(output.get("activities", []))
                    log_status(f"Found {count} activities")
                return output
            except json.JSONDecodeError:
                return {"raw_output": result.stdout}
        else:
            log_status(f"Subagent {name} failed: {result.stderr[:100] if result.stderr else 'unknown error'}")
            return {"error": result.stderr or "Subagent failed"}
    
    except subprocess.TimeoutExpired:
        log_status(f"Subagent {name} timed out")
        return {"error": "Subagent timed out"}
    except Exception as e:
        log_status(f"Subagent {name} error: {str(e)}")
        return {"error": str(e)}


def run_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Run a tool and return its output."""
    log_status(f"Running tool: {name}")
    tool_path = AGENT_DIR / "tools" / f"{name}.py"
    
    if not tool_path.exists():
        return {"error": f"Tool not found: {name}"}
    
    cmd = ["python3", str(tool_path)]
    
    # Build command arguments
    if name == "store_activity":
        if args.get("activity_json"):
            try:
                result = subprocess.run(
                    cmd + ["--stdin"],
                    input=args["activity_json"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(AGENT_DIR)
                )
                if result.returncode == 0:
                    try:
                        return json.loads(result.stdout)
                    except json.JSONDecodeError:
                        return {"status": "ok", "raw_output": result.stdout}
                else:
                    return {"error": result.stderr}
            except Exception as e:
                return {"error": str(e)}
    
    elif name == "retrieve_activities":
        if args.get("city"):
            cmd.extend(["--city", args["city"]])
        if args.get("category"):
            cmd.extend(["--category", args["category"]])
        if args.get("status"):
            cmd.extend(["--status", args["status"]])
        if args.get("toddler_friendly"):
            cmd.append("--toddler-friendly")
        if args.get("stroller_friendly"):
            cmd.append("--stroller-friendly")
        if args.get("limit"):
            cmd.extend(["--limit", str(args["limit"])])
        cmd.append("--pretty")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(AGENT_DIR)
        )
        
        if result.returncode == 0:
            log_status(f"Tool {name} completed successfully")
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"raw_output": result.stdout}
        else:
            log_status(f"Tool {name} failed")
            return {"error": result.stderr or "Tool failed"}
    
    except subprocess.TimeoutExpired:
        log_status(f"Tool {name} timed out")
        return {"error": "Tool timed out"}
    except Exception as e:
        log_status(f"Tool {name} error: {str(e)}")
        return {"error": str(e)}


def execute_function(name: str, args: Dict[str, Any], memory: MemoryStore) -> Dict[str, Any]:
    """Execute a function call and return results."""
    log_status(f"Executing function: {name}")
    
    if name == "search_activities":
        city = args.get("city", "unknown city")
        log_status(f"Searching for activities in {city}...")
        return run_subagent("activity_search", args)
    
    elif name == "enrich_activity":
        website = args.get("website", "unknown URL")
        log_status(f"Enriching activity from {website}")
        activity = {
            "id": args.get("activity_id", f"activity_{datetime.utcnow().timestamp()}"),
            "name": args.get("name", "Activity"),
            "website": website
        }
        result = run_subagent("activity_enrich", {"website": website, "name": args.get("name")})
        return result
    
    elif name == "store_activity":
        log_status("Saving activity to database...")
        return run_tool("store_activity", args)
    
    elif name == "retrieve_activities":
        log_status("Querying activity database...")
        return run_tool("retrieve_activities", args)
    
    elif name == "get_family_profile":
        log_status("Fetching family profile...")
        profile = memory.get_family_profile()
        return profile if profile else {"message": "No family profile defined yet"}
    
    elif name == "update_family_profile":
        log_status("Updating family profile...")
        current = memory.get_family_profile()
        if not current:
            current = {"name": "Our Family", "family_members": [], "home_city": "Helsinki", "home_country": "FI"}
        
        # Update fields
        for key in ["home_city", "home_country", "budget_preference", "preferred_categories", 
                    "indoor_outdoor_preference", "max_travel_minutes"]:
            if key in args and args[key] is not None:
                current[key] = args[key]
        
        if memory.set_family_profile(current):
            return {"status": "success", "message": "Profile updated"}
        else:
            return {"error": "Failed to update profile"}
    
    elif name == "record_visit":
        activity_id = args.get("activity_id")
        if not activity_id:
            return {"error": "activity_id required"}
        
        log_status(f"Recording visit to activity {activity_id}")
        rating = args.get("rating")
        notes = args.get("notes")
        
        memory.record_visit(activity_id, rating, notes)
        return {"status": "success", "message": "Visit recorded"}
    
    else:
        return {"error": f"Unknown function: {name}"}


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


def make_function_response(name: str, result: Dict[str, Any]) -> types.Part:
    """Create a function response part."""
    # Handle list responses by wrapping them in a dictionary
    if isinstance(result, list):
        result = {"results": result}
    return types.Part(
        function_response=types.FunctionResponse(
            name=name,
            response=result
        )
    )


def build_system_prompt(family_profile: Optional[Dict] = None) -> str:
    """Build the system prompt with skills and context."""
    skills = load_skills()
    
    profile_context = ""
    if family_profile:
        members_str = ", ".join([f"{m['name']} ({m['age']}yo)" for m in family_profile.get("family_members", [])])
        profile_context = f"""
## Family Profile
- **Home City:** {family_profile.get("home_city", "Unknown")}
- **Family Members:** {members_str}
- **Preferences:** {', '.join(family_profile.get("preferred_categories", []))}
- **Budget:** {family_profile.get("budget_preference", "moderate")}
- **Max Travel Time:** {family_profile.get("max_travel_minutes", 30)} minutes
- **Accessibility:** {', '.join(family_profile.get("accessibility_needs", ["stroller-friendly"]))}
"""
    
    return f"""You are an Activity Selection Agent for families with young children. Your job is to help find fun, age-appropriate activities.

## Your Capabilities

1. **Search for Activities**: Find family-friendly activities in specified cities
2. **Enrich Details**: Extract opening hours, pricing, facilities from websites
3. **Store & Recall**: Save discovered activities for future recommendations
4. **Track Preferences**: Remember what the family enjoyed and didn't enjoy
5. **Personalize**: Recommend activities that fit the family's profile and preferences

## How to Work

1. **Listen to the User**: Understand their needs and constraints
2. **Use Tools Appropriately**:
   - `search_activities` - find activities in a city
   - `enrich_activity` - get detailed info (hours, prices, facilities)
   - `store_activity` - save discovered activities
   - `retrieve_activities` - query saved activities
   - `record_visit` - track visits and ratings for personalization
   - `get_family_profile` / `update_family_profile` - manage family preferences

3. **Be Proactive**: Act on requests immediately. Don't just describe what you could do.

4. **Stay Focused**: Filter by:
   - Family member ages and needs
   - Accessibility requirements (stroller-friendly, etc.)
   - Distance/travel time
   - Budget
   - Weather/seasonality (when relevant)

5. **Quality Focus**: Prioritize verified, real venues with actual websites
{profile_context}
## Skills Reference

{skills}

## Response Style

- Be warm and friendly (helping families have fun!)
- Present info in clear, practical formats
- Explain your actions ("Searching for...", "Found X activities...")
- Offer helpful next steps ("Would you like me to get the hours?", "Shall I save these?")
- Make personalized recommendations based on family profile

Remember: Focus on finding FUN, age-appropriate activities that fit YOUR family's needs and constraints."""


def print_response(response) -> str:
    """Print and return model response text."""
    text_parts = []
    try:
        parts = response.candidates[0].content.parts if response.candidates else []
        for part in parts:
            if hasattr(part, "text") and part.text:
                text_parts.append(part.text)
    except Exception:
        pass
    
    text = "\n".join(text_parts)
    if text:
        print(text)
    return text


def run_chat_loop(client: genai.Client, model: str, memory: MemoryStore, initial_profile: Optional[Dict] = None):
    """Run interactive chat loop."""
    print("\n" + "=" * 60)
    print("  Activity Selection Agent - Interactive Mode")
    print("=" * 60)
    print("\nI help families with young children find fun activities in any city.")
    print("Commands: 'exit' to quit, 'profile' to see preferences, 'help' for more")
    print()
    
    # Get initial family profile
    profile = initial_profile or memory.get_family_profile()
    
    if profile:
        members = ", ".join([f"{m['name']} ({m['age']}yo)" for m in profile.get("family_members", [])])
        print(f"📍 Family Profile: {members} in {profile.get('home_city', 'Unknown')}")
    else:
        print("📍 Family profile not loaded")
    print()
    
    # Build tools
    function_declarations = build_function_declarations()
    tools = [types.Tool(function_declarations=function_declarations)]
    
    # Initialize conversation
    system_prompt = build_system_prompt(profile)
    history: List[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=system_prompt)]),
        types.Content(role="model", parts=[types.Part(text="I'm ready to help you find fun activities! What city are you interested in, or would you like me to recommend activities based on your profile?")])
    ]
    
    while True:
        try:
            user_input = input("\n👨‍👩‍👧‍👦 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye! Have fun with the family!")
            break
        
        if not user_input:
            continue
        
        if user_input.lower() in {"exit", "quit", ":q"}:
            print("👋 Goodbye! Have fun with the family!")
            break
        
        if user_input.lower() == "profile":
            print("\n📋 Current Family Profile:")
            if profile:
                print(json.dumps(profile, indent=2))
            else:
                print("No profile set yet")
            continue
        
        if user_input.lower() == "help":
            print("""
Commands:
  find <criteria>     - Search for activities (e.g., "find playgrounds in Helsinki")
  enrich <url>        - Get detailed info from a website
  list                - Show saved activities
  profile             - Show/edit family preferences
  record visit        - Track visits and ratings
  exit                - Quit
            """)
            continue
        
        # Add user message
        history.append(types.Content(role="user", parts=[types.Part(text=user_input)]))
        
        # Configure request
        config = types.GenerateContentConfig(tools=tools)
        
        # Generate response
        log_status("Sending request to Gemini API...")
        response = client.models.generate_content(
            model=model,
            contents=history,
            config=config
        )
        
        # Handle function calls (up to MAX_CHAT_ITERATIONS iterations)
        for iteration in range(MAX_CHAT_ITERATIONS):
            function_calls = find_function_calls(response)
            
            if not function_calls:
                break
            
            # Append the model's response
            if response.candidates and response.candidates[0].content:
                history.append(response.candidates[0].content)
            
            # Execute function calls and collect results
            function_responses = []
            for func_name, func_args in function_calls:
                result = execute_function(func_name, func_args, memory)
                
                # Show brief result
                if "activities" in result:
                    count = len(result.get("activities", []))
                    print(f"   ✓ Found {count} activities")
                elif "status" in result and result["status"] == "success":
                    print(f"   ✓ {result.get('message', 'Success')}")
                elif "error" in result:
                    print(f"   ✗ Error: {result['error']}")
                
                function_responses.append(make_function_response(func_name, result))
            
            # Add function responses
            history.append(types.Content(
                role="user",
                parts=function_responses
            ))
            
            # Get next response
            response = client.models.generate_content(
                model=model,
                contents=history,
                config=config
            )
        
        # Print final response
        print("\n🤖 Agent:", end=" ")
        response_text = print_response(response)
        
        # Add final response to history
        if response.candidates and response.candidates[0].content:
            history.append(response.candidates[0].content)


def run_single_query(client: genai.Client, model: str, query: str, memory: MemoryStore, profile: Optional[Dict] = None):
    """Run a single query."""
    log_status(f"Processing query: {query[:50]}...")
    
    # Build tools
    function_declarations = build_function_declarations()
    tools = [types.Tool(function_declarations=function_declarations)]
    
    # Get profile if not provided
    if not profile:
        profile = memory.get_family_profile()
        if profile:
            log_status(f"Using family profile: {profile.get('name', 'default')}")
    
    # Build conversation
    system_prompt = build_system_prompt(profile)
    contents = [
        types.Content(role="user", parts=[types.Part(text=system_prompt)]),
        types.Content(role="model", parts=[types.Part(text="Ready.")]),
        types.Content(role="user", parts=[types.Part(text=query)])
    ]
    
    config = types.GenerateContentConfig(tools=tools)
    
    # Generate response
    log_status("Sending request to Gemini API...")
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )
    log_status("Received initial response from Gemini")
    
    # Handle function calls
    for iteration in range(MAX_CHAT_ITERATIONS):
        function_calls = find_function_calls(response)
        
        if not function_calls:
            break
        
        iteration_label = f" (iteration {iteration + 1})" if iteration > 0 else ""
        log_status(f"Processing function calls{iteration_label}...")
        
        # Append the model's response
        if response.candidates and response.candidates[0].content:
            contents.append(response.candidates[0].content)
        
        # Execute functions and collect results
        function_responses = []
        for func_name, func_args in function_calls:
            result = execute_function(func_name, func_args, memory)
            function_responses.append(make_function_response(func_name, result))
        
        # Append function results
        contents.append(types.Content(
            role="user",
            parts=function_responses
        ))
        
        # Get next response
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
    
    # Print final response (with fallback if empty)
    output = print_response(response)
    if not output:
        # If no text output, try to generate a summary of what was found
        log_status("No direct text response - generating summary")
        print("Got it! I've searched for activities based on your query. What would you like to know more about? Feel free to ask follow-up questions like 'Tell me more about [activity name]', 'What are the hours?', 'Is it good for toddlers?', or 'What else can we do nearby?'")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Activity Selection Agent - Find fun activities for your family",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python activity_agent.py --chat
  python activity_agent.py "Find playgrounds in Helsinki"
  python activity_agent.py --profile family.json "What's open today in Barcelona?"
        """
    )
    
    parser.add_argument("query", nargs="?", help="Query to process (if omitted, enters chat mode)")
    parser.add_argument("--chat", action="store_true", help="Enter interactive chat mode")
    parser.add_argument("--profile", help="Family profile JSON file (optional)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Gemini model to use (default: {DEFAULT_MODEL})")
    
    args = parser.parse_args()
    
    # Load API key and client
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    
    # Load memory and family profile
    memory = MemoryStore()
    
    initial_profile = None
    if args.profile:
        try:
            with open(args.profile) as f:
                initial_profile = json.load(f)
        except Exception as e:
            print(f"Error loading profile: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Chat mode or single query
    if args.chat or not args.query:
        run_chat_loop(client, args.model, memory, initial_profile)
    else:
        run_single_query(client, args.model, args.query, memory, initial_profile)


if __name__ == "__main__":
    main()
