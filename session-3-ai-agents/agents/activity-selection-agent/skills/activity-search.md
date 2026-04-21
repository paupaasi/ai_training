# Skill: Activity Search

## Purpose
Find family-friendly activities in a specified city using Google Search and website analysis.

## When to Use
- User asks to find activities in a city: "Find playgrounds in Helsinki"
- User wants activities in a category: "Find museums suitable for toddlers"
- User searches for specific activity types: "Where can we go swimming with a 2-year-old?"
- User needs recommendations for a new city

## How It Works

### Function: `search_activities`

**Input Parameters:**
- `city` (required): City to search in (e.g., "Helsinki", "Barcelona", "London")
- `category` (optional): Activity category to filter by
  - Valid categories: playground, museum, zoo, swimming, nature, restaurant, show, sports, crafts, library, park, indoor_play, farm, amusement_park
- `age` (optional): Child age for age-appropriate recommendations (default: 2)
- `custom_query` (optional): Custom search query if standard search isn't enough

**Output Structure:**
```json
{
  "activities": [
    {
      "id": "activity_abc123",
      "name": "Activity Name",
      "website": "https://...",
      "category": "playground",
      "description": "What it offers",
      "address": "Physical address",
      "city": "Helsinki",
      "phone": "Contact number",
      "why_suitable": "Why it's good for toddlers",
      "estimated_duration_minutes": 90,
      "status": "new",
      "created_at": "2026-04-21T...",
      "source_url": "Where we found it"
    }
  ],
  "search_summary": "Overview of what was found",
  "sources": [{...}],
  "search_queries_used": ["..."]
}
```

## Usage Examples

### Example 1: Find playgrounds
```
search_activities(city="Helsinki", category="playground")
```
Returns: List of playgrounds in Helsinki suitable for young children

### Example 2: Find swimming venues for toddlers
```
search_activities(city="Barcelona", category="swimming", age=2)
```
Returns: Family-friendly swimming venues accessible for 2-year-olds

### Example 3: General activities with custom query
```
search_activities(city="Stockholm", custom_query="free indoor activities on rainy days for toddlers")
```
Returns: Activities matching the custom criteria

## Key Features

1. **Multi-language support** — Gemini automatically detects city and searches in appropriate language
2. **Grounding with actual websites** — Results include verified URLs from real venues
3. **Age-appropriate filtering** — Focuses on activities suitable for young children
4. **Location-specific** — Finds activities actually in the specified city
5. **Practical information** — Extracts address, phone, website for each venue

## Best Practices

1. **Be specific about categories** — Use category names from the valid list when possible
2. **Include age context** — Activities for 2-year-olds differ from 5-year-olds
3. **One city per search** — Search for one city at a time for best results
4. **Follow with enrichment** — After search, use `enrich_activity()` to get cost and hours
5. **Store discovered activities** — Always store successful results to avoid re-searching

## Troubleshooting

- **No results found** → Try broadening the category or removing filters
- **Results from other cities** → Specify full context in custom query if needed
- **Missing website URLs** → Use `enrich_activity()` with Google Search to find contact info
- **Wrong language** → Gemini auto-detects; results will be in city's language

## Related Functions

- `enrich_activity()` — Extract detailed cost, hours, facilities from websites found
- `store_activity()` — Save discovered activities to database
- `search_activities()` → `enrich_activity()` → `store_activity()` is the typical workflow
