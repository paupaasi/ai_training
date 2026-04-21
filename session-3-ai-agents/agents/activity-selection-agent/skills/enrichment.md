# Skill: Activity Enrichment

## Purpose
Extract detailed information from activity websites: opening hours, pricing, facilities, age suitability.

## When to Use
- Need complete pricing information: "How much does the museum cost?"
- Need opening hours: "What time does the zoo open on Sundays?"
- Need facility details: "Does the activity have a changing table?"
- Have an activity URL but need detailed information
- Activity was found but marked as "new" — enrich it before storing

## How It Works

### Function: `enrich_activity`

**Input Parameters:**
- `activity` (required): Activity object with at minimum:
  - `id`: Unique identifier
  - `name`: Activity name
  - `website`: URL to scrape (required)

**Output Structure:**
```json
{
  "id": "activity_abc123",
  "name": "Activity Name",
  "website": "https://...",
  "opening_hours": {
    "monday": "09:00-17:00",
    "tuesday": "09:00-17:00",
    "wednesday": "Closed",
    "thursday": "09:00-20:00",
    "friday": "09:00-21:00",
    "saturday": "10:00-18:00",
    "sunday": "10:00-17:00",
    "notes": "Seasonal variations: summer hours 09:00-22:00"
  },
  "cost_info": {
    "type": "paid",
    "price_range": "€8-12 for adults",
    "child_price": "€4-6 for children (3-12 years)",
    "family_deal": "Family package: €25 (2 adults + 2 children)",
    "currency": "EUR"
  },
  "age_suitability": {
    "min_age": 2,
    "max_age": null,
    "toddler_friendly": true,
    "best_age_range": "2-5 years"
  },
  "child_facilities": {
    "changing_table": true,
    "nursing_room": true,
    "high_chair": false,
    "cafe": true,
    "toilet": true,
    "hand_wash": true,
    "parking": true,
    "wheelchair_accessible": true
  },
  "duration_minutes": 120,
  "stroller_friendly": true,
  "indoor_outdoor": "indoor",
  "phone": "+358 1 234 5678",
  "address": "123 Main Street, Helsinki 00100",
  "google_maps_url": "https://maps.google.com/...",
  "enriched_at": "2026-04-21T...",
  "status": "enriched",
  "enrichment_model": "gemini-3.1-flash-lite-preview"
}
```

## Usage Examples

### Example 1: Enrich a found activity
```
activity = {
  "id": "activity_123",
  "name": "Helsinki Zoo",
  "website": "https://www.korkeasaari.fi"
}
enrich_activity(activity)
```
Returns: Full details including hours, pricing, facilities

### Example 2: Enrich by URL directly
```
enrich_activity({"name": "Zoo", "website": "https://..."})
```

## Key Features

1. **URL Context extraction** — Reads website content intelligently
2. **Structured data parsing** — Extracts opening hours, prices, facilities in consistent format
3. **Multilingual websites** — Handles websites in any language
4. **Fallback search** — If website doesn't have full info, searches for it
5. **Merge strategy** — Updates activity without overwriting existing data

## Information Extraction Details

### Opening Hours
- Extracts full weekly schedule
- Captures seasonal variations and special hours
- Marks closed days
- Notes holiday exceptions if visible

### Pricing
- Adult prices
- Child pricing (including age ranges)
- Family packages and bulk discounts
- Currency information
- Seasonal price variations if applicable

### Age Suitability
- Minimum and maximum recommended ages
- Toddler-friendly indicator (true/false)
- Description of best age range
- Activity limitations by age

### Facilities for Families
- Changing tables/facilities
- Nursing/breastfeeding rooms
- High chairs
- Cafes/restaurants
- Restrooms
- Hand-washing stations
- Parking availability
- Wheelchair accessibility

## Best Practices

1. **Enrich after discovery** — Search first, enrich immediately after
2. **Check critical fields** — Verify hours and prices are correct before storing
3. **Handle missing data** — If website doesn't mention a facility, field will be `null`
4. **Use actual prices** — Only extract information visible on website, don't estimate
5. **Store enriched activities** — After enrichment, store to avoid re-extracting later

## Troubleshooting

- **Missing hours** — Website may not have published hours online; try `google_search` or phone
- **Pricing unclear** → May be variable or require direct contact
- **Facilities not listed** → Call or email the venue directly
- **Outdated information** → Website may not be current; note the enrichment timestamp
- **Website error** → May need to search for alternative sources

## Integration Pattern

```
search_activities(city, category)
  ↓
[for each activity found]
  ↓
enrich_activity(activity_with_website)
  ↓
store_activity(enriched_activity)
  ↓
[activity ready for recommendations]
```

## Related Functions

- `search_activities()` — Find activities (provides websites to enrich)
- `store_activity()` — Save enriched activities for future use
- `record_visit()` — Track visits to enriched activities for better recommendations
