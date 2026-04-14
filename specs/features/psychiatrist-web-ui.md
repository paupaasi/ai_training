# Feature: 80s Retro Web UI for the Home Psychiatrist Game

> **Status:** Draft
> **Created:** 2026-04-14
> **Author:** AI Agent
> **Affected Subsystems:** Frontend (new), API (serve static files)
> **Depends On:** psychiatrist API (POST /sessions, POST /sessions/:id/messages, GET /sessions/:id/diagnosis, GET /personalities)

---

## Overview

### Purpose
Build a full browser-based 80s retro game UI for the Home Psychiatrist API — a single-page app that looks and feels like a CRT-screen home computer therapy program from 1985. Garish neon colors, scanline effects, blinking cursors, pixelated fonts, and ASCII art psychiatrists included. No framework needed — plain HTML, CSS, and vanilla JavaScript, served directly by the existing Express server.

### User Story
As a user, I want to open a webpage that puts me in a hilarious 80s home computer therapy session, so that I can choose my psychiatrist, chat with them, and receive an official diagnosis — all in glorious retro style.

### Scope

**Included:**
- Single-page HTML/CSS/JS frontend served from `public/index.html`
- Express serves `public/` as static files (one-line change to `src/index.ts`)
- Screen 1: Personality picker — 4 personality cards with ASCII art, name, description
- Screen 2: Chat interface — retro terminal with blinking cursor, scrolling chat history
- Screen 3: Diagnosis printout — animated typewriter diagnosis certificate
- 80s visual style: CRT scanlines, neon colors, pixel font, blinking text, ASCII borders
- Loading state: animated "PROCESSING..." spinners while waiting for Ollama
- Error state: funny retro error messages ("SYSTEM ERROR 404: EMPATHY MODULE OFFLINE")

**Not Included:**
- Multiple simultaneous sessions or user accounts
- Saved session history between page reloads
- Mobile responsiveness (this is a desktop-first retro game)
- Sound effects (future enhancement)
- Animated sprites (see `psychiatrist-sprite-integration.md`)

---

## Requirements

### Functional Requirements

- **FR-1:** The app MUST display a personality picker as the initial screen
- **FR-2:** Each personality card MUST show: name, tagline, ASCII art character, and description
- **FR-3:** Clicking a personality MUST start a session (`POST /sessions`) and transition to the chat screen
- **FR-4:** The chat screen MUST display: personality name/title in header, scrolling message history, input field, "SEND" button, "GET DIAGNOSIS" button
- **FR-5:** Sending a message MUST call `POST /sessions/:id/messages` and display the response in the chat
- **FR-6:** While waiting for a response the UI MUST show a "PROCESSING..." animation
- **FR-7:** The "GET DIAGNOSIS" button MUST call `GET /sessions/:id/diagnosis` and transition to the diagnosis screen
- **FR-8:** The diagnosis screen MUST display the diagnosis text with a typewriter animation and an "OFFICIAL CERTIFICATE" ASCII art frame
- **FR-9:** A "NEW SESSION" button on the diagnosis screen MUST return to the personality picker (clearing session state)
- **FR-10:** A "CHANGE THERAPIST" button in the chat MUST return to the personality picker (clearing session state)
- **FR-11:** API errors MUST display as retro error boxes with funny messages (not raw JSON)

### Non-Functional Requirements

- **Style:** 80s CRT aesthetic — dark background, neon green/cyan/yellow/pink, pixel font (Press Start 2P via Google Fonts CDN), scanline overlay via CSS
- **Self-contained:** A single `public/index.html` file — no build step, no npm, no framework
- **No external fetch library:** Use the native `fetch` API
- **XSS safety:** All dynamic text inserted with `textContent`, never `innerHTML` for user or API content
- **Performance:** Page loads and is interactive before Ollama is called
- **Accessibility:** All interactive elements reachable by keyboard; input submits on Enter

---

## Design Specification

### Color Palette
| Name | Hex | Usage |
|------|-----|-------|
| CRT Black | `#0a0a0a` | Page background |
| Phosphor Green | `#00ff41` | Default text, borders |
| Neon Cyan | `#00ffff` | Headings, user messages |
| Hot Pink | `#ff00ff` | Accents, personality cards |
| Amber | `#ffb000` | Psychiatrist responses |
| CRT Dark | `#001100` | Panel backgrounds |
| Error Red | `#ff2200` | Error messages |

### Typography
- **Primary:** `Press Start 2P` (Google Fonts CDN, 8px base) — all headings, labels, buttons
- **Chat text:** `Courier New, monospace` (14px) — message bubbles for readability

### Screen 1 — Personality Picker

```
╔══════════════════════════════════════════════════════════════╗
║  *** HOME PSYCHIATRIST v1.0 ***   LOADING... ░░░░░░░░░  ▓▓  ║
║  INSERT COIN TO BEGIN THERAPY                               ║
╚══════════════════════════════════════════════════════════════╝

  ┌──────────────────┐  ┌──────────────────┐
  │   DR-MIND 8000   │  │  DR. S. KLUDGE   │
  │  ╔════════════╗  │  │  ╔════════════╗  │
  │  ║  (・_・)   ║  │  │  ║  (◕ ‿ ◕)  ║  │ 
  │  ║   |DR|     ║  │  │  ║  |FREUD|  ║  │
  │  ╚════════════╝  │  │  ╚════════════╝  │
  │  FUNNY 80s COMP  │  │  IT'S ALL MUM's  │
  │  [ SELECT ]      │  │  [ SELECT ]      │
  └──────────────────┘  └──────────────────┘
```

### Screen 2 — Chat Terminal

```
╔══════════════════════════════════════════════════════════════╗
║  PATIENT SESSION #A4F2  ///  DR-MIND 8000  ///  [CHANGE]   ║
╚══════════════════════════════════════════════════════════════╝
│                                                              │
│  DR-MIND: Velcome! Tell me about your RAM situation...       │
│                                                              │
│  YOU: My computer is running slow.                           │
│                                                              │
│  DR-MIND: >>>>>PROCESSING EMOTIONAL DATA<<<<<               │
│           Zis is clearly Fragmented Soul Drive Syndrome!     │
│                                                              │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  > _ (blinking cursor)                                       │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  [ SEND MESSAGE ]              [ GET DIAGNOSIS ]             │
└──────────────────────────────────────────────────────────────┘
```

### Screen 3 — Diagnosis Printout

```
╔══════════════════════════════════════════════════════════════╗
║              *** OFFICIAL DIAGNOSIS CERTIFICATE ***         ║
║                    DR-MIND 8000 CLINICS                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  PATIENT PRESENTS WITH:                                      ║
║  [typewriter animation of diagnosis text...]                 ║
║                                                              ║
║  ~~~~~ CERTIFIED BY DR-MIND 8000 ~~~~~~                     ║
║  ████████████████████████████████████                        ║
║  STAMP: CLINICALLY UNUSUAL (NOT A REAL DIAGNOSIS)           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
                        [ NEW SESSION ]
```

---

## Files to Modify / Create

| File | Change |
|------|--------|
| `public/index.html` | **Create** — entire frontend (HTML + embedded CSS + embedded JS) |
| `src/index.ts` | **Modify** — add `express.static('public')` before routes |

---

## Acceptance Criteria

### AC1: Personality picker loads on page open
**Given** the API server is running  
**When** the user opens `http://localhost:3000` in a browser  
**Then** the personality picker screen is shown with all 4 personality cards loaded from `GET /personalities`  
**And** the page title reads "HOME PSYCHIATRIST v1.0"  
**And** the page background is CRT black with phosphor green text

### AC2: Session starts on personality selection
**Given** the personality picker is displayed  
**When** the user clicks "SELECT" on the DR-MIND 8000 card  
**Then** `POST /sessions` is called with `{ "personality": "default" }`  
**And** the chat screen appears with the greeting message shown as a psychiatrist message  
**And** a "PROCESSING..." indicator is shown while the request is in flight

### AC3: Chat message displayed correctly
**Given** a session is active on the chat screen  
**When** the user types a message and presses Enter or clicks SEND  
**Then** the user's message appears immediately in the chat history styled as a "YOU:" entry in cyan  
**And** `POST /sessions/:id/messages` is called  
**And** a "PROCESSING..." animation replaces the input area while waiting  
**And** the psychiatrist's response appears styled as a "DR-MIND:" entry in amber  
**And** the chat scrolls to the latest message

### AC4: Diagnosis screen shows typewriter animation
**Given** a session is active with at least one message exchange  
**When** the user clicks "GET DIAGNOSIS"  
**Then** `GET /sessions/:id/diagnosis` is called  
**And** the diagnosis screen is shown with the ASCII certificate frame  
**And** the diagnosis text appears character-by-character (typewriter effect, ~30ms per char)  
**And** a "NEW SESSION" button is visible once the typewriter animation completes

### AC5: New session returns to personality picker
**Given** the diagnosis screen is displayed  
**When** the user clicks "NEW SESSION"  
**Then** the session id is cleared from frontend state  
**And** the personality picker screen is shown again  
**And** `GET /personalities` is called again to refresh the list

### AC6: Change therapist mid-session
**Given** the chat screen is active  
**When** the user clicks "CHANGE THERAPIST"  
**Then** the session is abandoned (no API call needed — server-side session persists but is ignored)  
**And** the personality picker screen is shown  
**And** the old session id is cleared from state

### AC7: API error displayed as retro error box
**Given** Ollama is not running  
**When** the user tries to start a session or send a message  
**Then** a retro styled error box is shown with text like "!!! SYSTEM ERROR: THERAPIST MODULE OFFLINE !!!"  
**And** the user can retry without refreshing the page

### AC8: Input submits on Enter key
**Given** the chat input field is focused  
**When** the user presses Enter (not Shift+Enter)  
**Then** the message is submitted (same as clicking SEND)

### AC9: XSS safety — API content is text-only
**Given** the API returns a response containing `<script>alert(1)</script>`  
**When** it is rendered in the chat  
**Then** the literal text `<script>alert(1)</script>` is displayed, not executed  
(All API content MUST be inserted via `textContent`, never `innerHTML`)

### AC10: CRT scanline visual effect
**Given** any screen is displayed  
**Then** a CSS scanline overlay (semi-transparent repeating horizontal lines) is visible over the content, simulating a CRT monitor

---

## Testing Strategy

### Manual Browser Tests
| Test | Steps | Expected |
|------|-------|----------|
| Full happy path | Open page → select personality → chat → get diagnosis → new session | All 3 screens work, styles render correctly |
| Enter key submit | Type message, press Enter | Message sends |
| Empty message | Click SEND with empty input | Nothing sent, no API call |
| Typewriter speed | Watch diagnosis appear | Character-by-character, readable pace |
| Error display | Stop Ollama, try to chat | Retro error box appears |
| XSS check | Send `<b>bold</b>` | Literal text displayed |

### Automated Tests (none required for this spec)
The frontend is a single static HTML file with no build step. All business logic is tested via the existing `psychiatrist-service.test.ts` unit tests. Frontend integration can be validated manually.

---

## Implementation Notes

- **No build step**: the entire frontend lives in `public/index.html` — HTML structure, `<style>` block for CSS, `<script>` block for JS. This makes it trivially easy to open and edit during a training session.
- **ASCII art per personality**: each personality card uses a hardcoded ASCII art character block defined in the JS. These don't need to match the actual `id` values from the API — they're decorative.
- **Scanline effect**: implemented with a CSS `::before` pseudo-element on `body` using `repeating-linear-gradient` — no images needed.
- **Pixel font**: loaded from Google Fonts CDN (`https://fonts.googleapis.com/css2?family=Press+Start+2P`). Chat bubbles use `Courier New` for legibility.
- **State management**: three JS variables — `currentScreen`, `sessionId`, `selectedPersonality` — are sufficient. No framework needed.
- **Typewriter effect**: `setInterval` that appends one character at a time to a `<span>`, clears itself when text is complete.

---

## Related Documentation
- **API:** [d-psychiatrist-api/src/routes/psychiatrist.ts](../../session-1-greenfield/d-psychiatrist-api/src/routes/psychiatrist.ts) — all endpoints consumed by this UI
- **Personalities:** [d-psychiatrist-api/src/data/personalities.ts](../../session-1-greenfield/d-psychiatrist-api/src/data/personalities.ts) — personality ids used in POST /sessions
- **Other specs:** [psychiatrist-sprite-integration.md](psychiatrist-sprite-integration.md) — future animated sprite enhancement
