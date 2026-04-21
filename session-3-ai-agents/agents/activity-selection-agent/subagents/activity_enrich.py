#!/usr/bin/env python3
"""
Activity Enrichment Subagent

Uses Gemini's url_context tool to extract details from activity websites,
particularly opening hours, pricing, and facilities information.

Usage:
  python activity_enrich.py --url "https://example.com" --name "Zoo"
  python activity_enrich.py --file activity.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import re

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


def build_enrichment_prompt(activity: Dict[str, Any]) -> str:
    """Build a prompt for enriching activity details from its website."""
    
    activity_info = f"Activity: {activity.get('name', 'Unknown')}\nWebsite: {activity.get('website', 'N/A')}"
    
    return f"""Extract detailed information from the website for this family-friendly activity:

{activity_info}

Please extract and return the following information as a JSON object:

{{
  "opening_hours": {{
    "monday": "09:00-17:00",
    "tuesday": "09:00-17:00",
    "wednesday": "09:00-17:00",
    "thursday": "09:00-17:00",
    "friday": "09:00-17:00",
    "saturday": "10:00-18:00",
    "sunday": "10:00-18:00",
    "notes": "Note any seasonal closures or special hours"
  }},
  "cost_info": {{
    "type": "free|paid|variable",
    "price_range": "€5-10 for adults",
    "child_price": "€3-5 for children",
    "family_deal": "Family pass: €20 for 4 people",
    "currency": "EUR"
  }},
  "age_suitability": {{
    "min_age": 0,
    "max_age": 10,
    "toddler_friendly": true,
    "best_age_range": "2-5 years"
  }},
  "child_facilities": {{
    "changing_table": true,
    "nursing_room": true,
    "high_chair": false,
    "cafe": true,
    "toilet": true,
    "hand_wash": true,
    "parking": true,
    "wheelchair_accessible": true
  }},
  "duration_minutes": 120,
  "stroller_friendly": true,
  "indoor_outdoor": "both",
  "phone": "+358 1 2345 6789",
  "address": "Full address if available",
  "google_maps_url": "URL to Google Maps if available"
}}

EXTRACTION GUIDELINES:
1. Use the website's contact form, location page, and FAQ for information
2. For opening hours, extract the full weekly schedule and note any variations
3. For pricing, extract all relevant prices (adult, child, family packages)
4. For facilities, list what's actually mentioned on the website
5. Mark unknown values as null, not as estimated guesses
6. If a facility is not mentioned, assume null (unknown)
7. If the site is in a different language, Gemini will translate naturally

Only include information actually found on the website. If something is not mentioned, leave it as null.
Focus especially on:
- Exact opening hours (including seasonal variations)
- Pricing for different age groups
- Facilities specifically mentioned for families/children
- Stroller accessibility
- Parking availability"""


def enrich_activity(
    activity: Dict[str, Any],
    model: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """
    Enrich activity details by extracting info from its website.
    
    Uses:
    - URL Context to read and analyze the activity's website
    """
    api_key = load_api_key()
    client = genai.Client(api_key=api_key)
    
    # Check if activity has a website URL
    website_url = activity.get("website")
    if not website_url:
        return {
            "error": "No website URL provided",
            "activity_id": activity.get("id"),
            "status": "incomplete"
        }
    
    # Build tools list
    tools = [
        types.Tool(url_context=types.UrlContext()),
        types.Tool(google_search=types.GoogleSearch())  # Fallback for finding website info
    ]
    
    # Build configuration
    config = types.GenerateContentConfig(tools=tools)
    
    # Build prompt
    prompt = build_enrichment_prompt(activity)
    
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=config
        )
        
        # Extract text response
        if not response.candidates or not response.candidates[0].content.parts:
            return {
                "error": "No response from model",
                "activity_id": activity.get("id"),
                "status": "enrichment_failed"
            }
        
        response_text = response.candidates[0].content.parts[0].text
        
        # Try to parse as JSON
        try:
            enriched_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                try:
                    enriched_data = json.loads(json_match.group())
                except json.JSONDecodeError:
                    enriched_data = {}
            else:
                enriched_data = {}
        
        # Merge enriched data with original activity
        # Strategy: don't overwrite existing non-null values, only fill in missing data
        result = activity.copy()
        
        for key, value in enriched_data.items():
            if value is not None and value != "" and value != []:
                # Only update if key doesn't exist or is null/empty in original
                if key not in result or result[key] is None or result[key] == "":
                    result[key] = value
            elif key in enriched_data and isinstance(enriched_data[key], dict):
                # For nested objects (like opening_hours), merge recursively
                if key not in result:
                    result[key] = {}
                if isinstance(result[key], dict):
                    for subkey, subvalue in enriched_data[key].items():
                        if subvalue is not None and subvalue != "":
                            result[key][subkey] = subvalue
        
        # Add metadata
        result["enriched_at"] = datetime.utcnow().isoformat()
        result["status"] = "enriched"
        result["enrichment_model"] = model
        result["enrichment_source"] = website_url
        
        return result
    
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__,
            "activity_id": activity.get("id"),
            "status": "enrichment_failed",
            "original_activity": activity
        }


def main():
    """CLI interface for activity enrichment."""
    parser = argparse.ArgumentParser(description="Enrich activity details from website")
    parser.add_argument("--url", help="Activity website URL")
    parser.add_argument("--name", help="Activity name")
    parser.add_argument("--file", help="Activity JSON file to enrich")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Gemini model to use")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    
    args = parser.parse_args()
    
    activity = None
    
    if args.file:
        with open(args.file) as f:
            activity = json.load(f)
    elif args.url and args.name:
        activity = {
            "name": args.name,
            "website": args.url,
            "id": f"activity_{datetime.utcnow().timestamp()}"
        }
    else:
        print(json.dumps({
            "error": "Must provide either --file or both --url and --name"
        }), file=sys.stderr)
        sys.exit(1)
    
    result = enrich_activity(activity, model=args.model)
    
    indent = 2 if args.pretty else None
    print(json.dumps(result, indent=indent))


if __name__ == "__main__":
    main()
