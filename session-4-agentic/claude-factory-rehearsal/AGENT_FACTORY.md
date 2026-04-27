# Agent Factory: Unified Design Document

**Agent Factory** is a specialized factory that combines three core concepts from the factory suite:
1. **Roles** — Multiple specialized personas (spec-writer, developer, tester, reviewer, fixer)
2. **Session Resumption** — Persist and resume work across sessions
3. **Spec-Driven Loops** — Iterative workflow that implements → tests → reviews → fixes until complete

## Purpose

Generate and validate new AI agents for the `session-3-ai-agents` folder using a fully automated, spec-driven workflow.

## Concepts Reference

### 1. Roles (from `02_factory_catalog.py`)

The factory uses **five specialized agent roles**, each with distinct responsibilities:

| Role | Responsibility | Tools |
|------|-----------------|-------|
| **Spec Writer** | Generate comprehensive agent specifications | Read, Glob |
| **Developer** | Implement agents following specs | Read, Glob, Grep, Edit, Bash |
| **Tester** | Create and run validation tests | Read, Glob, Grep, Edit, Bash |
| **Reviewer** | Assess completeness and quality | Read, Glob, Grep |
| **Fixer** | Diagnose and resolve issues | Read, Glob, Grep, Edit, Bash |

Each role is invoked at the right phase in the workflow, ensuring specialized expertise at each step.

### 2. Session Resumption (from `03_resumable_factory.py`)

Sessions are persisted to `.factory-agent-<agent_name>.json`:

```json
{
  "agent_name": "my-agent",
  "session_id": "...",
  "iteration": 3,
  "phase": "test",
  "spec_content": "...",
  "test_results": {...},
  "review_feedback": "..."
}
```

Commands:
- `python 05_agent_factory.py start my-agent` — Begin new factory run
- `python 05_agent_factory.py resume my-agent` — Continue from last paused state
- `python 05_agent_factory.py status my-agent` — Check current status

### 3. Spec-Driven Loop (from `04_spec_loop_factory.py`)

Each iteration follows this flow:

```
┌─────────────────────────────────────────────────────────────┐
│  ITERATION N                                                │
├─────────────────────────────────────────────────────────────┤
│  ① SPEC GENERATION                                          │
│     └─ Spec Writer generates/refines agent specification    │
│                                                             │
│  ② IMPLEMENTATION                                           │
│     └─ Developer implements agent code from spec            │
│                                                             │
│  ③ TESTING                                                  │
│     └─ Tester runs validation tests                         │
│     └─ Reports PASS/FAIL/ERROR for each test              │
│                                                             │
│  ④ REVIEW                                                   │
│     └─ Reviewer assesses spec compliance                    │
│     └─ Decision: APPROVED → Done | CHANGES_REQUIRED → ⑤   │
│                                                             │
│  ⑤ FIXING (if needed)                                       │
│     └─ Fixer addresses review feedback                      │
│     └─ Jump back to TESTING (repeat ③-⑤)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ↑                                        │
         └────────────────────────────────────────┘
              Loop if not approved (max 8 iterations)
```

## Workflow Example

### Start a New Agent

```bash
python 05_agent_factory.py start sentiment-analyzer --backend claude

# When prompted, enter the agent goal:
# "Create an agent that analyzes sentiment in user feedback and categorizes it"
```

The factory will then:

1. **Spec Generation** — AI writes a comprehensive spec for the sentiment analyzer
2. **Implementation** — AI implements the agent based on the spec
3. **Testing** — AI creates tests and runs them against the implementation
4. **Review** — AI checks if implementation matches spec and tests pass
5. **Loop or Complete** — If approved, the agent is done. If not, fix issues and re-test.

### Resume a Paused Run

```bash
# Mid-iteration, you hit Ctrl+C or timeout
# Session state is automatically saved

# Resume from where you left off:
python 05_agent_factory.py resume sentiment-analyzer

# The factory continues from the last phase (test, review, or fix)
```

### Check Status

```bash
python 05_agent_factory.py status sentiment-analyzer

# Output:
# Agent: sentiment-analyzer
# Iteration: 3
# Phase: test
# Spec (first 200 chars): Agent: Sentiment Analyzer...
```

## State Persistence

Session state is stored in `.factory-agent-<agent_name>.json` with:

- **session_id** — Backend session for resuming LLM context
- **iteration** — Current iteration (1-8)
- **phase** — Last completed phase (spec, implement, test, review, fix)
- **spec_content** — The generated specification
- **test_results** — Output from testing phase
- **review_feedback** — Reviewer's assessment and feedback

This enables:
- ✅ Resume after interruptions (Ctrl+C, timeout)
- ✅ Continue with full context restored
- ✅ Track multi-iteration progress
- ✅ Inspect intermediate states for debugging

## Prompts & Roles

Each phase uses a carefully crafted prompt that invokes the appropriate role:

### Phase: SPEC GENERATION
```
Prompt includes: Agent name, goal, previous feedback (if iteration > 1)
Role invoked: Spec Writer
Expected output: Markdown specification with Purpose, Responsibilities, Contracts, etc.
```

### Phase: IMPLEMENTATION
```
Prompt includes: Agent name, full specification, previous code issues (if any)
Role invoked: Developer
Expected output: Working Python code in session-3-ai-agents/agents/<name>/
```

### Phase: TESTING
```
Prompt includes: Agent name, specification
Role invoked: Tester
Expected output: Test files + test results with [PASS]/[FAIL]/[ERROR] markers
```

### Phase: REVIEW
```
Prompt includes: Agent name, spec, test results
Role invoked: Reviewer
Expected output: FINAL_STATUS: APPROVED or FINAL_STATUS: CHANGES_REQUIRED
```

### Phase: FIXING
```
Prompt includes: Agent name, review feedback
Role invoked: Fixer
Expected output: Fixed code + re-run tests
```

## Key Features

✅ **Role Specialization** — Each phase uses the right expertise
✅ **Resumable Sessions** — Paused work can be resumed with full context
✅ **Iterative Refinement** — Loops until spec compliance and tests pass
✅ **Comprehensive Logging** — See what each phase is doing
✅ **Configurable Limits** — Max iterations, timeouts, tool restrictions
✅ **State Inspection** — Check status of any run at any time

## Configuration

Modify `FactoryConfig` to adjust behavior:

```python
@dataclass
class FactoryConfig:
    agent_name: str
    backend: Backend = "claude"
    timeout: int = 180  # Seconds per phase
    agent_max_turns: int = 25  # Max turns per backend call
    permission_mode: str = "acceptEdits"  # Accept edits automatically
    max_iterations: int = 8  # Max refinement loops
```

## Extending the Factory

To add new roles or phases:

1. Define a new role function:
   ```python
   def agent_role_my_role() -> str:
       return "You are a ... Your role is to..."
   ```

2. Create a phase method:
   ```python
   def _phase_my_phase(self) -> bool:
       prompt = build_my_phase_prompt(...)
       result = run_sync(...)
       return result.ok
   ```

3. Update the factory loop to call it:
   ```python
   if not self._phase_my_phase():
       return 1
   ```

## Error Handling

- **Phase failures** — Logged with stop reason; factory halts
- **Timeouts** — Phase times out after `timeout` seconds
- **Interrupts** — Ctrl+C saves state and exits (can resume later)
- **No session found** — Resume without prior start is prevented with helpful message

## Integration with Session-3-AI-Agents

The factory creates new agents in:
```
session-3-ai-agents/agents/<agent_name>/
├── agent.py (or main implementation file)
├── config.py (if needed)
├── tests/
│   └── test_agent.py
└── README.md (agent documentation)
```

Each agent is self-contained and can be imported directly:
```python
from session_3_ai_agents.agents.sentiment_analyzer.agent import SentimentAnalyzer

agent = SentimentAnalyzer()
result = agent.run(input_data)
```

## Comparison with Other Factories

| Factory | Purpose | Concepts Used |
|---------|---------|---------------|
| `01_minimal_factory.py` | Simple automation | Role only |
| `02_factory_catalog.py` | Multiple specialized factories | Roles (multi) |
| `03_resumable_factory.py` | Resume work across sessions | Session resumption |
| `04_spec_loop_factory.py` | Implement → Test → Review loop | Spec-driven loops |
| **`05_agent_factory.py`** | **Generate agents end-to-end** | **Roles + Sessions + Loops** |

## Debugging Tips

1. **Check current state:**
   ```bash
   python 05_agent_factory.py status <agent_name>
   ```

2. **View session file directly:**
   ```bash
   cat .factory-agent-<agent_name>.json | jq .
   ```

3. **Clear session and restart:**
   ```bash
   rm .factory-agent-<agent_name>.json
   python 05_agent_factory.py start <agent_name>
   ```

4. **Increase verbosity** (edit factory code):
   ```python
   # Uncomment debug prints in phase methods
   print(f"[DEBUG] {state_variable}")
   ```

## Future Enhancements

- [ ] Parallel phase execution for independent tasks
- [ ] Caching of test results across iterations
- [ ] Integration with CI/CD for automated validation
- [ ] Metric tracking (iterations needed, time per phase, success rate)
- [ ] Custom phase chains (allow skipping phases, reordering)
- [ ] Template library for common agent types
- [ ] Interactive phase mode (pause and modify prompts before continuing)
