# Prompt 02: Write Your Feature Spec

**When to use:** After the SDD + Specifications theory blocks
**Goal:** Write a spec for Feature 1 (Start Session & Chat) using the AGENTS.md spec template

---

## Your Task

Write a spec for the "Start Session & Chat" feature. Save it as `specs/start-session.md`.

**Use the spec template from `../../AGENTS.md` (Workflow: spec → Spec Template) as your format.**

### Feature Requirements

The API lets users start a therapy session and have a funny conversation with the AI psychiatrist.

**Endpoint 1: POST /sessions** — Start a new therapy session
Behaviors to cover:
- Starting a session returns a session id and a greeting message from the psychiatrist
- The greeting should be in the style of a funny 80s home computer psychiatrist
- Response format: `{ data: { sessionId: string, greeting: string } }`
- Response status: 201

**Endpoint 2: POST /sessions/:id/messages** — Send a message to the psychiatrist
Behaviors to cover:
- Sending a message with a valid session id returns the psychiatrist's response
- Session not found (what status code? what error message?)
- Empty or missing message body (what validation? what error?)
- Response format: `{ data: { response: string } }`

Technical constraints:
- Gemini service is injectable/mockable — tests never call the real API
- Business logic lives in psychiatrist-service.ts, not in route handlers
- Session stores the full message history (for context in Gemini calls)
- Success response: `{ data: T }`
- Error response: `{ error: string }`

---

## The "Can AI Test This?" Check

Before moving on, verify each AC you wrote:
1. Does every AC have specific expected values (status codes, field names, types)?
2. Could you write an `expect()` assertion for each **Then** clause?
3. Are error cases covered with exact error messages?
4. Is it clear what the mock Gemini service should return?

If any answer is "no" — rewrite the AC until it's testable.

---

## Ask AI to Review Your Spec

```
@specs/start-session.md
@../../AGENTS.md

Review this spec against the spec template in AGENTS.md:
1. Is every AC testable with a concrete assertion?
2. Are there missing edge cases?
3. Does the response format match the technical constraints?
4. Is the test strategy complete?
5. Is it clear how to mock the Gemini service for each test?

List any issues found.
```
