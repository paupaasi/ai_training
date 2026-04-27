# Captain Recommendations

## Purpose
Recommend optimal captain picks based on form, fixtures, and ownership.

## When to Use
- User asks "who should I captain?"
- Before each gameweek deadline
- User wants to know top 3 captain options

## Tools Required
- fpl_fetcher (get player data and fixtures)
- player_lookup (player details)
- fixture_difficulty (fixture analysis)
- injury_news (check availability)

## Methodology
1. Fetch all player data
2. Get fixture difficulty for each team
3. Filter by form (top performers)
4. Check ownership % (avoid very high ownership for differential)
5. Weight: Form (40%) + Fixture (40%) + Value (20%)
6. Return top 5 captain picks

## Captain Selection Criteria
- High recent form (last 5 games)
- Easy upcoming fixtures (FDR 1-2)
- Not injured
- Reasonable price point
- Good points-per-million

## Example
```
User: "Who should I captain this week?"
-> Fetch player data -> Calculate fixture scores -> Rank by form + fixtures -> Top 3 picks
```