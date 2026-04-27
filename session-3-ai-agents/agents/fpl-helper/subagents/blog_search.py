#!/usr/bin/env python3
"""Blog Post Search - Search FPL blog posts and articles."""

import argparse
import json
import sys
from typing import Any, Dict

from google import genai
from google.genai import types


def search_fpl_blogs(query: str, api_key: str) -> Dict[str, Any]:
    """Search FPL-related content using web search."""
    client = genai.Client(api_key=api_key)

    search_query = f"FPL fantasy premier league {query} 2025 2026"
    
    result = client.models.generate_content(
        model="gemini-2.0-flash-exp",
        contents=[search_query],
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            google_search=types.GoogleSearch(query=search_query)
        )
    )

    return {
        "query": query,
        "results": query,
        "search_performed": True
    }


def get_fpl_news() -> Dict[str, Any]:
    """Get FPL news."""
    return {
        "news": [
            {"title": "Check Premier League官方 website", "url": "https://www.premierleague.com/news"},
            {"title": "FPL Blog", "url": "https://www.premierleague.com/fantasy"}
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="FPL Blog Search")
    parser.add_argument(
        "--query", "-q",
        default="tips",
        help="Search query"
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY env)"
    )

    args = parser.parse_args()

    import os
    api_key = args.api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_AI_STUDIO_KEY")

    if not api_key:
        result = get_fpl_news()
        print(json.dumps(result, indent=2))
    else:
        result = search_fpl_blogs(args.query, api_key)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()