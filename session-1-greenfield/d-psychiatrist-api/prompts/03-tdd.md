# Prompt 03: Implement Feature 1 with TDD

**When to use:** After the TDD Cycle theory block
**Goal:** Implement "Start Session & Chat" using Red-Green-Refactor

---

## Step 1: RED — Write Failing Test for AC1 (Start Session)

Copy-paste this prompt:

```
@specs/start-session.md
@src/types.ts
@src/services/psychiatrist-service.ts

Looking at AC1 (Start a new therapy session), write a failing test.

Requirements:
- Use Vitest
- Test file: src/services/psychiatrist-service.test.ts
- Test the service function directly (not the Express route)
- Mock the Gemini service to return a fixed greeting like "Ah, velcome to ze couch! Tell me about your motherboard..."
- Test that startSession() returns a session object with id, greeting message, and createdAt
- Do NOT modify the service implementation yet

Run the test to confirm it fails.
```

**Verify:** Run `npm test` — it should FAIL (red). This is correct!

---

## Step 2: GREEN — Implement AC1

```
The test in psychiatrist-service.test.ts is failing.

Implement startSession() in src/services/psychiatrist-service.ts to make the AC1 test pass.

Requirements:
- Accept a Gemini client (or mock) as parameter
- Call the Gemini client with the psychiatrist system prompt
- Create a new session in storage with a unique id
- Return the session id and the greeting from Gemini
- Keep it simple — just make the test pass

Run tests to confirm they pass.
```

**Verify:** Run `npm test` — it should PASS (green).

---

## Step 3: RED — Write Failing Test for AC2 (Send Message)

```
@specs/start-session.md
@src/services/psychiatrist-service.test.ts
@src/services/psychiatrist-service.ts

Looking at AC2 (Send message to psychiatrist), write a failing test.

Requirements:
- First start a session (using the mock from Step 1)
- Then call sendMessage(sessionId, "I feel anxious about my RAM usage")
- Mock Gemini to return: "Hmm, zis is very common in computers your age..."
- Test that the response contains the psychiatrist's message
- Test that the message history is updated (session now has 2+ messages)

Run the test to confirm it fails.
```

**Verify:** Run `npm test` — the new test should FAIL.

---

## Step 4: GREEN — Implement AC2

```
The sendMessage test is failing.

Implement sendMessage() in src/services/psychiatrist-service.ts.

Requirements:
- Look up the session by id in storage
- Add the user's message to history
- Call Gemini with the system prompt + full message history
- Add the psychiatrist's response to history
- Return the response
- Keep it simple — just make the test pass

Run tests to confirm they pass.
```

**Verify:** Run `npm test` — all tests should PASS.

---

## Step 5: RED/GREEN — Add Edge Cases

```
@specs/start-session.md
@src/services/psychiatrist-service.test.ts
@src/services/psychiatrist-service.ts

Add tests for the remaining ACs one at a time:

1. Session not found — sendMessage("nonexistent-id", "hello") should return null or throw
2. Empty message — sendMessage(validId, "") should throw a validation error

For each:
- Write the test first (RED)
- Run tests — confirm just that test fails
- Implement the minimum code (GREEN)
- Run tests — confirm all pass

Keep all existing tests passing.
```

**Verify:** Run `npm test` — all tests pass.

---

## Step 6: Refactor

```
All tests pass. Refactor the psychiatrist service:
1. Extract the system prompt building into a helper function
2. Add proper TypeScript return types to all functions
3. Make sure the Gemini client interface is clean and minimal

Keep all tests passing after each change.
```

**Key rule:** Run tests after EVERY change. If they break, undo and try again.
