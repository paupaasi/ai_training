# Feature: Health Check Endpoint

> This is a reference example. Use this format for your own specs.

## Overview
A simple health check endpoint that confirms the API is running.

## Acceptance Criteria

### AC1: Returns healthy status
**Given** the server is running
**When** GET /health is called
**Then** return 200 with:
  - status: "ok"
  - uptime: number (seconds since start)

### AC2: Response format
**Given** the server is running
**When** GET /health is called
**Then** the response is JSON with Content-Type: application/json

### AC3: No auth required
**Given** no authentication headers are sent
**When** GET /health is called
**Then** return 200 (no auth check)

## Technical Constraints
- No authentication required
- Response time < 50ms
- No external dependencies (no Gemini call)

## Test Strategy
- Integration test: start server, call /health, verify response shape
- Verify uptime is a positive number
