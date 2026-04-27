# Transfer Recommendations

## Purpose
Analyze player form, fixtures, and value to recommend optimal transfers.

## When to Use
- User asks "who should I transfer?"
- User wants to sell underperforming players
- User has transfer budget and wants value picks

## Tools Required
- fpl_fetcher (get player data)
- player_lookup (detailed player analysis)
- fixture_difficulty (upcoming fixtures)
- memory (save/retrieve squad)

## Methodology
1. Fetch current player data from FPL API
2. Get user's current squad from memory
3. Identify underperforming players (low form, <4.0)
4. Find high-value alternatives (high form, good fixtures)
5. Calculate points-per-million for value
6. Return buy/sell recommendations

## Example
```
User: "I have 2.0m to spend, what transfers should I make?"
-> Get squad -> Analyze form -> Recommend top 3 buys and sell candidates
```