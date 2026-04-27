# Software Factory Training Rehearsals

This folder is designed for live training. It demonstrates how to move from a
single-agent "factory" call to a spec-driven implementation loop.

Core idea for participants:

"A software factory is a reusable policy wrapper around an agent loop:
goal contract + tool policy + quality gates."

## Training flow (4 rehearsals)

### Rehearsal 1 - Minimal Factory

**Goal:** show the smallest possible factory shape.

Script:

- `01_minimal_factory.py`

What to teach:

- a factory accepts a task
- a backend executes it (`claude`, `codex`, `opencode`)
- output comes back as one final result

Run:

```bash
uv run python 01_minimal_factory.py --backend claude "Summarize this project"
uv run python 01_minimal_factory.py --backend codex "Summarize this project"
uv run python 01_minimal_factory.py --backend opencode "Summarize this project"
```

### Rehearsal 2 - Behavior by Factory Role + Session Resume

**Goal:** show that factories are policies, not just prompts.

Scripts:

- `02_factory_catalog.py` (analyzer / fixer / planner)
- `03_resumable_factory.py` (start/resume)

What to teach:

- same backend, different role policy => different behavior
- sessions can continue across calls (factory memory)

Run:

```bash
uv run python 02_factory_catalog.py analyzer --backend codex "Find likely risk areas"
uv run python 02_factory_catalog.py planner --backend claude "Create implementation plan"

uv run python 03_resumable_factory.py start --backend opencode "Inspect auth flow"
uv run python 03_resumable_factory.py resume --backend opencode "Continue and propose fixes"
```

### Rehearsal 3 - Spec-Driven Delivery Loop

**Goal:** show automation loop used in real software work.

Script:

- `04_spec_loop_factory.py`

Spec:

- `spec.example.json`

What to teach:

- factory reads a delivery spec
- runs loop: implement -> checks -> review
- repeats until approved or max iterations reached

Run:

```bash
uv run python 04_spec_loop_factory.py --backend codex --spec spec.example.json
```

### Rehearsal 4 - Agent Factory (Combined: Roles + Sessions + Loops)

**Goal:** demonstrate a practical, production-grade factory that generates new AI agents end-to-end.

Scripts:

- `05_agent_factory.py`

Documentation:

- `AGENT_FACTORY.md` (full design and concepts)
- `QUICKSTART_AGENT_FACTORY.md` (quick start guide)

What to teach:

- combines all three concepts: roles + session resumption + spec-driven loops
- specialized factories can be domain-specific (in this case: agent generation)
- five roles working in concert: Spec Writer → Developer → Tester → Reviewer → Fixer
- complete workflow from goal → validated agent implementation

Run:

```bash
# Start a new agent factory run
uv run python 05_agent_factory.py start sentiment-analyzer --backend claude

# When prompted, provide agent goal:
# "Create an agent that analyzes sentiment in customer reviews and categorizes them"

# Resume a paused run
uv run python 05_agent_factory.py resume sentiment-analyzer

# Check status of any run
uv run python 05_agent_factory.py status sentiment-analyzer
```

Output is created in `session-3-ai-agents/agents/<agent_name>/` with:
- Complete agent implementation
- Comprehensive test suite
- Agent documentation
- All dependencies configured

---

## Setup for training session

**No API keys required** — uses CLI subscriptions.

1. Verify Python:

```bash
uv run python -V  # or python3 -V
```

2. Verify CLIs (at least one required):

```bash
claude --version   # Claude Code
codex --version    # OpenAI Codex
opencode --version # OpenCode
```

3. Install Python SDK:

```bash
pip install claude-agent-sdk
```

4. Run all checks + sample runs:

```bash
./run_demo.sh
```

---

## Files in this training pack

- `01_minimal_factory.py` - single factory call
- `02_factory_catalog.py` - role-based factory policies
- `03_resumable_factory.py` - session continuation
- `04_spec_loop_factory.py` - implement/test/review loop
- `05_agent_factory.py` - **agent generation factory (combines all concepts)**
- `backend_runner.py` - backend adapter (`claude`, `codex`, `opencode`)
- `spec.example.json` - editable loop specification
- `AGENT_FACTORY.md` - **full design documentation for agent factory**
- `QUICKSTART_AGENT_FACTORY.md` - **quick start guide with examples**
- `run_demo.sh` - quick environment and demo runner

---

## Spec format for rehearsal 3

`04_spec_loop_factory.py` expects JSON with:

- `goal`: target outcome
- `max_iterations`: maximum loop rounds
- `checks`: deterministic local commands
- optional:
  - `implement_instructions`
  - `review_instructions`
  - `allowed_tools`
  - `permission_mode`
  - `agent_max_turns`
  - `model`

`checks[].command` can use `{python}` placeholder, which resolves to:

- `uv run python` when available
- otherwise `python3`
