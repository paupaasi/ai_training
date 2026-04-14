# Prompt 01: Scaffold Your Project

**When to use:** After the Context Sandwich + Model Selection theory blocks
**Goal:** Use a Context Sandwich prompt to scaffold the psychiatrist API

---

## Your Context Sandwich Prompt

```
@CLAUDE.md
@package.json
@tsconfig.json

Create the initial project structure for a funny retro home psychiatrist API.

Think 80s-style "home computer therapy" programs like ELIZA — but powered by
Google Gemini for actually funny, absurd responses. The API lets clients start
a therapy session, send messages, and get a humorous diagnosis.

The API should have these endpoints:
- POST /sessions — start a new therapy session (returns session id + greeting)
- POST /sessions/:id/messages — send a message to the psychiatrist (returns response)
- GET /sessions/:id/diagnosis — get a funny summary diagnosis of the session
- GET /health — health check

Set up the following folder structure:
- src/index.ts — Express server setup, mount routes, listen on PORT or 3000
- src/types.ts — TypeScript interfaces (Session, Message, Personality, ChatRequest, ChatResponse, DiagnosisResponse)
- src/routes/psychiatrist.ts — route handlers for all session/chat endpoints
- src/services/gemini-service.ts — Gemini API wrapper (must be mockable for tests)
- src/services/psychiatrist-service.ts — business logic (start session, send message, get diagnosis)
- src/data/personalities.ts — personality definitions (default: funny retro psychiatrist)
- src/storage.ts — in-memory session storage (Map of sessions by id)

Requirements:
- Follow the coding standards in CLAUDE.md
- Define all TypeScript interfaces in types.ts first
- Create placeholder functions that throw "not implemented"
- The Gemini service must accept a dependency-injectable interface (so tests can mock it)
- A Session should have: id, personality, messages (array), createdAt
- A Message should have: role ("user" | "psychiatrist"), content, timestamp
- Express server listens on PORT env var or 3000
- Do NOT implement the full Gemini integration yet — just the structure
```

---

## What to look for

After AI generates the scaffold:
1. Are all interfaces defined in types.ts?
2. Is the Gemini service a separate, mockable module?
3. Are route handlers separate from business logic?
4. Does the personality type have a systemPrompt field?
5. Does `npm run lint` pass (no TypeScript errors)?
6. Does the server start and respond to `/health`?

If something doesn't match your rules, iterate:
```
The GeminiService in src/services/gemini-service.ts needs to be injectable.
Add an interface GeminiClient with a generateResponse(prompt: string, history: Message[]) method.
The service should accept this interface in its constructor so tests can provide a mock.
```
