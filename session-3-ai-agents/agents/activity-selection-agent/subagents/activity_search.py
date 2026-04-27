#!/usr/bin/env python3
"""
Activity Search Subagent

Uses Gemini's integrated tools (Google Search, URL Context) to find
child-friendly activities in specified cities.

Usage:
  python activity_search.py --city "Helsinki" --category "playground"
  python activity_search.py --city "Barcelona" --query "indoor activities for toddlers"
  python activity_search.py --city "Helsinki" --category "swimming" --age 2
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import uuid

_AGENT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AGENT_DIR))
from agent_env import load_agent_environment

load_agent_environment()

from google import genai
from google.genai import types

# Configuration
DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"


def load_api_key() -> str:
    """Load Gemini API key from environment."""
    api_key = (
        os.environ.get("GOOGLE_AI_STUDIO_KEY") or 
        os.environ.get("GEMINI_API_KEY") or 
        os.environ.get("GOOGLE_API_KEY")
    )
    if not api_key:
        print(json.dumps({
            "error": "API key not found",
            "message": "Set GOOGLE_AI_STUDIO_KEY, GEMINI_API_KEY, or GOOGLE_API_KEY"
        }))
        sys.exit(1)
    return api_key


def build_search_prompt(city: str, category: Optional[str] = None, custom_query: Optional[str] = None, age: int = 2) -> str:
    """Build a search prompt for family-friendly activities."""
    
    if custom_query:
        return f"""Search for family-friendly activities in {city} matching this query: {custom_query}

Focus on activities suitable for young children (0-5 years old).

Return a JSON object with this structure:
{{
  "activities": [
    {{
      "name": "Activity Name",
      "website": "https://...",
      "category": "Category (playground, museum, etc.)",
      "description": "Brief description of what the activity offers",
      "address": "Physical address in {city}",
      "city": "{city}",
      "why_suitable": "Why this is good for toddlers/young children",
      "source": "Where this information came from"
    }}
  ],
  "search_summary": "Brief summary of what was found in {city}"
}}

Find 5-10 relevant activities. Focus on:
1. Safe, age-appropriate activities
2. Places with good infrastructure for small children (changing facilities, etc.)
3. Activities accessible from {city}
4. Verifiable venues with actual websites
5. Quality recommendations over quantity"""
    
    category_text = f"Category: {category}" if category else "Any category"
    
    return f"""Search for family-friendly activities and venues in {city} for young children (especially {age} year olds and younger).

**Search Criteria:**
- City: {city}
- {category_text}
- Age group: Toddlers and young children (0-5 years)
- Safety and accessibility for small children

IMPORTANT GUIDELINES:
- Find ACTUAL venues in {city}, not generic lists
- Prioritize places designed for young children
- Include practical information (website, address)
- Focus on safe, age-appropriate activities
- Only include verifiable venues with real websites

Categories to consider: playground, park, museum, zoo, swimming, indoor play, nature, farm, library

Return a JSON object with this structure:
{{
  "activities": [
    {{
      "name": "Venue/Activity Name",
      "website": "https://...",
      "category": "playground|museum|swimming|nature|park|etc.",
      "description": "What the activity/venue offers (2-3 sentences)",
      "address": "Physical address in {city}",
      "city": "{city}",
      "phone": "Contact phone if found",
      "why_suitable": "Specifically why this is good for {age} year olds and toddlers",
      "estimated_duration_minutes": 60,
      "source_url": "URL where info was found"
    }}
  ],
  "search_summary": "Summary of activities found in {city}",
  "search_location": "{city}"
}}

Find 5-10 relevant activities. Prioritize:
1. Actual venues in {city} with verified websites
2. Activities designed for or very suitable for young children
3. Places with good facilities for small children
4. A mix of indoor and outdoor options when possible"""


def search_activities(
    city: str,
    category: Optional[str] = None,
    custom_query: Optional[str] = None,
    age: int = 2,
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Search for family-friendly activities using Gemini's integrated tools.
    
    Uses:
    - Google Search for finding activities
    - URL Context for analyzing activity websites
    """
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    
    # Build tools list
    tools = [
        types.Tool(google_search=types.GoogleSearch()),
        types.Tool(url_context=types.UrlContext())
    ]
    
    # Build configuration
    config = types.GenerateContentConfig(tools=tools)
    
    # Build prompt
    prompt = build_search_prompt(city, category, custom_query, age)
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        
        # Extract text response
        if not response.candidates or not response.candidates[0].content.parts:
            return {"error": "No response from model", "activities": []}
        
        response_text = response.candidates[0].content.parts[0].text
        
        # Try to parse as JSON
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except json.JSONDecodeError:
                    result = {"raw_response": response_text, "activities": []}
            else:
                result = {"raw_response": response_text, "activities": []}
        
        # Add IDs and timestamps to activities
        for i, activity in enumerate(result.get("activities", [])):
            if "id" not in activity:
                timestamp = datetime.utcnow().isoformat().replace(":", "").replace("-", "")[:12]
                activity["id"] = f"activity_{timestamp}_{i}"
            
            activity["status"] = "new"
            activity["created_at"] = datetime.utcnow().isoformat()
            
            # Ensure required fields
            if "city" not in activity:
                activity["city"] = city
            if "category" not in activity:
                activity["category"] = category or "other"
            if "country" not in activity:
                # Try to infer country from city
                city_to_country = {
                    "Helsinki": "FI", "Espoo": "FI", "Tampere": "FI", "Turku": "FI",
                    "Barcelona": "ES", "Madrid": "ES", "Valencia": "ES",
                    "London": "UK", "Manchester": "UK",
                    "Paris": "FR", "Lyon": "FR",
                    "Berlin": "DE", "Munich": "DE",
                    "Stockholm": "SE", "Gothenburg": "SE",
                    "Oslo": "NO", "Bergen": "NO",
                    "Copenhagen": "DK",
                    "Amsterdam": "NL",
                    "New York": "US", "Los Angeles": "US", "San Francisco": "US"
                }
                activity["country"] = city_to_country.get(city, "UNKNOWN")
        
        # Add metadata
        result["search_metadata"] = {
            "model": model,
            "timestamp": datetime.utcnow().isoformat(),
            "city": city,
            "category": category,
            "age": age
        }
        
        # Extract grounding metadata if available
        if response.candidates[0].grounding_metadata:
            meta = response.candidates[0].grounding_metadata
            if meta.grounding_chunks:
                sources = []
                for chunk in meta.grounding_chunks[:5]:  # Limit to 5 sources
                    if hasattr(chunk, 'web') and chunk.web:
                        sources.append({
                            "title": chunk.web.title if hasattr(chunk.web, 'title') else "Source",
                            "url": chunk.web.uri if hasattr(chunk.web, 'uri') else ""
                        })
                if sources:
                    result["sources"] = sources
            
            if meta.web_search_queries:
                result["search_queries_used"] = meta.web_search_queries
        
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "activities": []
        }


def main():
    """CLI interface for activity search."""
    parser = argparse.ArgumentParser(description="Search for family-friendly activities")
    parser.add_argument("--city", required=True, help="City to search in")
    parser.add_argument("--category", help="Activity category (playground, museum, zoo, etc.)")
    parser.add_argument("--query", help="Custom search query")
    parser.add_argument("--age", type=int, default=2, help="Child age (default: 2)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model to use")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    result = search_activities(
        city=args.city,
        category=args.category,
        custom_query=args.query,
        age=args.age,
        model=args.model
    )
    
    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent))


if __name__ == "__main__":
    main()
