# Prompt 04: Spec + Build Feature 2

**When to use:** After completing Feature 1 with TDD
**Goal:** Repeat the full cycle — spec → test → implement — for "Personality Modes"

---

## Step 1: Write the Spec Yourself

Write a spec for the "Personality Modes" feature. Save it as `specs/personality-modes.md`.

**Use the same format as your Feature 1 spec (which follows the AGENTS.md template).**

### Feature Requirements

The API supports different psychiatrist personalities that change the tone and style of responses.

**Endpoint 1: GET /personalities** — List available personalities
Returns all available personality modes with name and description.

**Endpoint 2: POST /sessions** — Now accepts an optional `personality` field
Starting a session with `{ personality: "freudian" }` uses that personality's system prompt.

Personalities to include:
- **default** — Funny 80s home computer psychiatrist (the original)
- **freudian** — Everything is about your mother(board). Heavy Austrian accent. Interprets everything as repressed memory.
- **newage** — Crystal-healing, chakra-aligning, mercury-retrograde-blaming therapist. Prescribes essential oils for segfaults.
- **conspiracy** — Believes all your problems are caused by government surveillance, chemtrails, and big tech. Your anxiety is actually "them" watching.

Behaviors to cover:
- Listing all personalities (what fields in the response?)
- Starting a session with a valid personality
- Starting a session with an invalid personality name (what error?)
- Default personality when no personality is specified
- Personality affects the system prompt sent to Gemini

---

## Step 2: Ask AI to Review Your Spec

```
@specs/personality-modes.md
@specs/start-session.md

Review this spec for completeness:
1. Is every AC testable with a concrete assertion?
2. Are there missing edge cases?
3. Does it cover how personality affects the system prompt?
4. Does it follow the same format as start-session.md?

List any issues found.
```

Fix any issues the AI identifies before proceeding.

---

## Step 3: TDD — RED for AC1 (List Personalities)

```
@specs/personality-modes.md
@src/types.ts
@src/data/personalities.ts

Looking at AC1 (List all personalities), write a failing test.

Requirements:
- Test file: src/services/psychiatrist-service.test.ts (add to existing)
- Test getPersonalities() returns array with at least 4 personalities
- Each personality has: id, name, description
- Do NOT implement yet

Run the test to confirm it fails.
```

**Verify:** `npm test` — the new test should FAIL.

---

## Step 4: GREEN for AC1

```
The getPersonalities test is failing.

Implement getPersonalities() in src/services/psychiatrist-service.ts.

Requirements:
- Read personality definitions from src/data/personalities.ts
- Return array of { id, name, description }
- Keep it simple — just make the test pass

Run tests to confirm they pass.
```

**Verify:** `npm test` — all tests pass.

---

## Step 5: RED/GREEN for AC2 (Start session with personality)

```
@specs/personality-modes.md
@src/services/psychiatrist-service.test.ts
@src/services/psychiatrist-service.ts
@src/data/personalities.ts

Add a test for AC2 (start session with specific personality):
- startSession({ personality: "freudian" }) should use the Freudian system prompt
- Verify the mock Gemini service receives the Freudian system prompt (not the default)
- The session object should record which personality is active

Run the test — it will likely FAIL.
Then update the implementation to make it pass.
All existing tests must still pass.
```

**Verify:** `npm test` — all tests pass.

---

## Step 6: RED/GREEN for remaining ACs

```
@specs/personality-modes.md
@src/services/psychiatrist-service.test.ts
@src/services/psychiatrist-service.ts

Add tests for the remaining ACs one at a time:
1. Invalid personality name returns an error
2. No personality specified defaults to "default"
3. Personality affects ongoing conversation tone (the system prompt persists)

For each: write test (RED), implement (GREEN), verify all pass.
```

---

## Wrap-Up

After both features are implemented, reflect:
- How many tests do you have?
- Did the spec help AI produce correct code on the first try?
- How did mocking the Gemini service affect your testing strategy?
- What would change if you switched from mock to real Gemini calls?
