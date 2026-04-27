# Agent Factory — Concept Integration Map

This document shows how the three core factory concepts (Roles, Sessions, Loops) are unified in `05_agent_factory.py`.

## Concept 1: Roles (from `02_factory_catalog.py`)

**Concept:** Different personas, different behaviors.

**In Agent Factory:**

```python
def agent_role_spec_writer() -> str:
    return "You are an Agent Specification Writer..."

def agent_role_developer() -> str:
    return "You are an Agent Developer..."

def agent_role_tester() -> str:
    return "You are an Agent Tester..."

def agent_role_reviewer() -> str:
    return "You are an Agent Code Reviewer..."

def agent_role_fixer() -> str:
    return "You are an Agent Problem Fixer..."
```

**How It's Used:**

Each factory phase invokes a specialized role. The **same backend** but **different roles** produce **different behaviors**:

```
Phase 1: SPEC (Spec Writer role)
  ↓ Gets constraints, returns comprehensive spec
Phase 2: IMPLEMENT (Developer role)
  ↓ Reads spec, implements agent code
Phase 3: TEST (Tester role)
  ↓ Creates tests, validates implementation
Phase 4: REVIEW (Reviewer role)
  ↓ Assesses compliance, returns verdict
Phase 5: FIX (Fixer role) [if needed]
  ↓ Fixes issues, loops back
```

**Key Role Characteristics:**

| Role | Tools | Behavior | Output |
|------|-------|----------|--------|
| Spec Writer | Read, Glob | Think, structure, plan | Markdown spec document |
| Developer | Read, Glob, Grep, Edit, Bash | Implement, test locally | Working Python code |
| Tester | Read, Glob, Grep, Edit, Bash | Create tests, run tests | [PASS]/[FAIL] results |
| Reviewer | Read, Glob, Grep | Analyze, assess | APPROVED or CHANGES_REQUIRED |
| Fixer | Read, Glob, Grep, Edit, Bash | Diagnose, fix surgically | Fixed code + re-test |

---

## Concept 2: Session Resumption (from `03_resumable_factory.py`)

**Concept:** Persist state between calls; resume with full context.

**In Agent Factory:**

```python
@dataclass
class SessionState:
    agent_name: str
    session_id: str | None = None
    iteration: int = 0
    phase: str = "spec"
    spec_content: str = ""
    test_results: dict[str, Any] | None = None
    review_feedback: str = ""

    def save(self) -> None:
        file = session_file_for(self.agent_name)
        file.write_text(json.dumps(asdict(self)), encoding="utf-8")

    @staticmethod
    def load(agent_name: str) -> SessionState | None:
        file = session_file_for(agent_name)
        return SessionState(**json.loads(file.read_text())) if file.exists() else None
```

**Session File Format:**

```json
{
  "agent_name": "sentiment-analyzer",
  "session_id": "claude-session-123456",
  "iteration": 3,
  "phase": "test",
  "spec_content": "Agent: Sentiment Analyzer\nPurpose: ...",
  "test_results": {"output": "[PASS] test_basic..."},
  "review_feedback": ""
}
```

**How It Works:**

1. User runs: `python 05_agent_factory.py start agent-name`
   - Factory creates new `SessionState` and saves to `.factory-agent-agent-name.json`

2. User interrupts (Ctrl+C) mid-iteration
   - `state.save()` persists current progress
   - Exit cleanly

3. Later, user runs: `python 05_agent_factory.py resume agent-name`
   - Factory loads saved session: `SessionState.load(agent_name)`
   - Restores: iteration count, phase, spec, test results, backend session ID
   - **Continues from exact stopping point** with full LLM context intact

4. User checks status: `python 05_agent_factory.py status agent-name`
   - Loads and displays current state without resuming work

**Benefits:**

- ✅ Recover from interruptions without losing progress
- ✅ Resume with full LLM context (via `session_id`)
- ✅ Track multi-iteration progress across sessions
- ✅ Inspect intermediate states for debugging
- ✅ No need to restart from beginning

---

## Concept 3: Spec-Driven Loops (from `04_spec_loop_factory.py`)

**Concept:** Implement → Test → Review → Loop until approved.

**In Agent Factory:**

```python
def run(self, agent_goal: str) -> int:
    for iteration in range(self.state.iteration, self.config.max_iterations + 1):
        print(f"\n--- ITERATION {iteration}/{self.config.max_iterations} ---")

        # Phase 1: Spec
        if not self._phase_spec(agent_goal):
            return 1
        self.state.phase = "implement"
        self.save_state()

        # Phase 2: Implement
        if not self._phase_implement():
            return 1
        self.state.phase = "test"
        self.save_state()

        # Phase 3: Test
        if not self._phase_test():
            return 1
        self.state.phase = "review"
        self.save_state()

        # Phase 4: Review
        approved = self._phase_review()
        if approved:
            print("\n✓ Agent factory completed successfully!")
            return 0
        
        # Phase 5: Fix and loop
        self.state.phase = "fix"
        if not self._phase_fix():
            return 1
        # Loop back to testing
```

**Loop Structure:**

```
┌─ ITERATION 1 ──────────────────────────────────┐
│  1. SPEC GENERATION                            │
│  2. IMPLEMENTATION                             │
│  3. TESTING                                    │
│  4. REVIEW                                     │
│     ├─ if APPROVED → Done ✓                   │
│     └─ if CHANGES_REQUIRED → 5               │
│  5. FIXING                                     │
│     └─ Loop back to TESTING                   │
└─────────────────────────────────────────────────┘
                    ↑ Loop back if issues found
         (max 8 iterations before abort)
```

**Key Phase Behaviors:**

| Phase | Input | Processing | Output | Next |
|-------|-------|-----------|--------|------|
| SPEC | goal + feedback | Generate spec | Markdown doc | IMPLEMENT |
| IMPLEMENT | spec | Code agent | Agent files | TEST |
| TEST | spec | Run tests | [PASS]/[FAIL] | REVIEW |
| REVIEW | spec + tests | Assess | APPROVED/CHANGES | Done or FIX |
| FIX | feedback | Fix issues | Fixed code | TEST (loop) |

---

## How It All Comes Together

### Example: Create Sentiment Analyzer

```bash
python 05_agent_factory.py start sentiment-analyzer --backend claude
# Enter: "Create an agent that analyzes sentiment in customer reviews"
```

### Iteration 1

**SPEC Phase (Spec Writer role):**
```
Input: agent goal
Role: "You are an Agent Specification Writer..."
Output: 
  Agent: Sentiment Analyzer
  Purpose: Analyzes sentiment in reviews
  Responsibilities: ...
  Success Criteria: ...
```

**IMPLEMENT Phase (Developer role):**
```
Input: spec
Role: "You are an Agent Developer..."
Output: Python code in session-3-ai-agents/agents/sentiment-analyzer/
```

**TEST Phase (Tester role):**
```
Input: spec
Role: "You are an Agent Tester..."
Output:
  [PASS] test_positive_sentiment
  [PASS] test_negative_sentiment
  [FAIL] test_edge_cases: ValueError on empty input
```

**REVIEW Phase (Reviewer role):**
```
Input: spec + test results
Role: "You are an Agent Code Reviewer..."
Output: FINAL_STATUS: CHANGES_REQUIRED
  Issues: 1. Edge case handling missing
```

**FIX Phase (Fixer role):**
```
Input: review feedback
Role: "You are an Agent Problem Fixer..."
Output: Fixed code (adds edge case handling)
Loop back to TEST
```

### Iteration 2

**TEST Phase:** [PASS] all tests

**REVIEW Phase:** FINAL_STATUS: APPROVED

**DONE:** Agent factory completed successfully! ✓

### Session State After Completion

Persisted state shows:
```json
{
  "agent_name": "sentiment-analyzer",
  "iteration": 2,
  "phase": "review",
  "spec_content": "...",
  "test_results": {"output": "[PASS] all tests..."},
  "review_feedback": "FINAL_STATUS: APPROVED"
}
```

User can later:
- Resume the session and make further refinements
- Check status to see what was built
- Use generated agent in code

---

## Why This Design?

### Why Roles?

→ Specialized behavior ensures quality at each step.
→ Same backend, different persona = different output.
→ Roles can be swapped or customized for different use cases.

### Why Sessions?

→ Support long-running processes that may be interrupted.
→ Resume with full LLM context (via session_id).
→ Track progress across days/weeks without restarting.

### Why Loops?

→ Real software requires iteration.
→ Automated testing + review gates ensure quality.
→ Fixed issues are re-validated, not just applied.

### Why Combine All Three?

→ **Comprehensive automation:** Roles handle expertise, loops handle iteration, sessions handle resilience.
→ **Production-grade:** Can handle complex, multi-iteration tasks.
→ **Practical:** Works in real scenarios where interruptions and refinements are normal.

---

## Extending the Factory

To add new roles or phases:

### Add a New Role

```python
def agent_role_documentation_writer() -> str:
    return """
You are a Documentation Writer. Your role is to:
1. Read the agent implementation
2. Generate comprehensive docstring and README
...
""".strip()
```

### Add a New Phase

```python
def _phase_documentation(self) -> bool:
    prompt = build_documentation_phase_prompt(self.config.agent_name, self.state.spec_content)
    result = run_sync(
        BackendRunOptions(
            backend=self.config.backend,
            prompt=prompt,
            cwd=get_default_cwd(),
            allowed_tools=["Read", "Glob", "Grep", "Edit"],
            permission_mode="acceptEdits",
            max_turns=self.config.agent_max_turns,
            resume_session_id=self.state.session_id,
            timeout_seconds=self.config.timeout,
        )
    )
    if not result.ok:
        return False
    self.state.session_id = result.session_id or self.state.session_id
    print("[ok] Documentation generated")
    return True

# Add to run() method after review phase
if not self._phase_documentation():
    return 1
```

### Update Phase Order

Edit the factory loop in `run()` to insert the new phase in the right place.

---

## Files Structure

```
session-4-agentic/claude-factory-rehearsal/
├── 01_minimal_factory.py          (Concept 1: Simple factory)
├── 02_factory_catalog.py          (Concept 1: Roles)
├── 03_resumable_factory.py        (Concept 2: Sessions)
├── 04_spec_loop_factory.py        (Concept 3: Loops)
├── 05_agent_factory.py            (✨ Concepts 1+2+3 COMBINED)
├── AGENT_FACTORY.md               (Design documentation)
├── QUICKSTART_AGENT_FACTORY.md    (Quick start guide)
├── backend_runner.py              (Backend adapter)
└── README.md                       (This training pack)
```

## Next Steps

1. **Understand the lineage:** Review 01→02→03→04 to see concepts build up
2. **Review 05_agent_factory.py:** Read the source to see how concepts unify
3. **Try it:** Run `python 05_agent_factory.py start test-agent`
4. **Customize:** Modify roles and phases for your use case
5. **Integrate:** Use with CI/CD, metrics, extended validation

---

## Summary

**Agent Factory = Roles + Sessions + Loops**

- **Roles** provide specialized behavior at each step
- **Sessions** enable resumption and long-running work
- **Loops** automate iteration until quality gates pass
- **Together:** A production-grade system for generating and validating agents
