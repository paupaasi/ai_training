# Factory Rehearsals — Comparison & Progression

This document shows how each rehearsal builds on previous concepts.

## Overview Matrix

| Aspect | 01: Minimal | 02: Catalog | 03: Resumable | 04: Spec Loop | 05: Agent |
|--------|-----------|-----------|--------------|----------------|----------|
| **Concept** | Single call | Roles | Sessions | Loops | All combined |
| **Script** | `01_minimal_factory.py` | `02_factory_catalog.py` | `03_resumable_factory.py` | `04_spec_loop_factory.py` | `05_agent_factory.py` |
| **Complexity** | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Lines of Code** | ~50 | ~100 | ~80 | ~200 | ~500+ |
| **Use Case** | One-off task | Different behaviors | Long-running work | Deliver software | Generate agents |
| **State Management** | None | None | Session file | External spec | Full persistence |
| **Quality Gates** | None | None | None | Tests + Review | Tests + Review + Loop |
| **Max Iterations** | 1 | 1 | N/A | Configurable | 8 (configurable) |
| **Can Resume?** | ❌ | ❌ | ✅ | ❌ | ✅ |
| **Domain-Specific** | ❌ | ❌ | ❌ | ❌ | ✅ (agents) |

## Concept Progression

```
                                   Time complexity →

Rehearsal 1: MINIMAL FACTORY
├─ Single backend call
├─ One prompt, one result
└─ No state management
    ↓
    Rehearsal 2: FACTORY CATALOG
    ├─ Multiple roles (same backend)
    ├─ Role-specific behavior
    └─ Each role is a separate factory
        ↓
        Rehearsal 3: RESUMABLE FACTORY
        ├─ Single role (like #1)
        ├─ + Session persistence
        ├─ Resume capability
        └─ Longer-running single workflow
            ↓
            Rehearsal 4: SPEC LOOP FACTORY
            ├─ Implement → Test → Review loop
            ├─ Quality gates (checks)
            ├─ Repeats until approved
            └─ Single spec → multiple iterations
                ↓
                Rehearsal 5: AGENT FACTORY
                ├─ Combines: Roles + Sessions + Loops
                ├─ 5 specialized roles
                ├─ Full session persistence
                ├─ 5-phase loop with review gates
                ├─ Resume at any point
                └─ Domain-specific (agent generation)
```

## Feature Combination Table

### Rehearsal 1: Minimal

```python
factory = Factory(spec, backend="claude")
result = factory.run(task)
print(result)
```

**What you get:**
- ✅ Simple factory shape
- ✅ Works with any backend
- ❌ No specialization
- ❌ No persistence
- ❌ No quality gates

### Rehearsal 2: Catalog

```python
for factory_name in ['analyzer', 'fixer', 'planner']:
    factory = FACTORIES[factory_name]
    result = run_factory(factory, task, backend)
```

**What you get:**
- ✅ Multiple roles with different behaviors
- ✅ Same backend, different personas
- ✅ Each factory is a separate policy
- ❌ No persistence
- ❌ No quality gates
- ❌ No iteration

**New concept: ROLES**
```
Role determines:
- Tool access (what agent can do)
- Permission mode (how agent makes changes)
- Max turns (conversation length)
- Behavior (instructions)
```

### Rehearsal 3: Resumable

```python
run(task, resume=True, backend="claude")
# Interrupt (Ctrl+C)
# Later...
run(task, resume=True, backend="claude")  # Continues
```

**What you get:**
- ✅ Session persistence
- ✅ Resume capability
- ✅ Full context restoration
- ❌ No multiple roles
- ❌ No quality gates
- ❌ No iteration

**New concept: SESSIONS**
```
Session state stored in:
.factory-session-id-<backend>

Contains:
- session_id (LLM context)
- Persist across invocations
- Enable recovery from interruption
```

### Rehearsal 4: Spec Loop

```python
run_loop(
    spec={
        'goal': '...',
        'checks': [{'command': '...'}, ...],
        'max_iterations': 5
    },
    backend="claude"
)
# Loop: implement → check → review → approve/retry
```

**What you get:**
- ✅ Iterative workflow
- ✅ Quality gates (checks)
- ✅ Review-based approval
- ✅ Repeats until approved
- ❌ No roles (single role only)
- ❌ No session resumption

**New concept: LOOPS**
```
Workflow phases:
1. IMPLEMENT - code from spec
2. CHECKS - run validation tests
3. REVIEW - assess completion
4. APPROVE/RETRY - decision gate

If not approved, loop back to IMPLEMENT
(max_iterations prevents infinite loop)
```

### Rehearsal 5: Agent Factory

```python
factory = AgentFactory(FactoryConfig("sentiment-analyzer"))
factory.load_or_new()  # Session resumption
exit_code = factory.run(agent_goal)

# Phases:
# SPEC (Spec Writer role) → save state
# IMPLEMENT (Developer role) → save state
# TEST (Tester role) → save state
# REVIEW (Reviewer role) → save state
# FIX (Fixer role) if needed → loop back

# Can resume, inspect, continue across sessions
```

**What you get:**
- ✅ **5 specialized roles** for different phases
- ✅ **Full session persistence** (resume anywhere)
- ✅ **Iterative spec-driven loop** (implement → test → review)
- ✅ **Quality gates** (tests + review)
- ✅ **Domain-specific** (agent generation)
- ✅ **Production-ready** (comprehensive error handling)

**Combined concepts: ROLES + SESSIONS + LOOPS**

---

## Learning Progression

### Week 1: Understand Factories

- **Day 1:** Rehearsal 1 (Minimal Factory)
  - Learn: basic factory structure, backend integration
  - Practice: run with different backends, modify prompts

- **Day 2:** Rehearsal 2 (Catalog)
  - Learn: roles determine behavior, policy-driven design
  - Practice: add new roles, customize tool access

- **Day 3:** Rehearsal 3 (Resumable)
  - Learn: state persistence, session management
  - Practice: interrupt and resume, inspect state files

- **Day 4:** Rehearsal 4 (Spec Loop)
  - Learn: iterative workflows, quality gates, approval loops
  - Practice: write specs, set checks, watch factory iterate

- **Day 5:** Rehearsal 5 (Agent Factory)
  - Learn: combine all concepts into a domain-specific factory
  - Practice: generate agents end-to-end, customize phases

### Week 2: Hands-On Integration

- Extend Agent Factory with custom roles
- Create a factory for your domain (code review, docs generation, etc.)
- Integrate factories with CI/CD pipelines
- Track metrics and success rates

### Week 3: Production Deployment

- Deploy factories as microservices
- Add monitoring and alerting
- Document custom roles and workflows
- Train team on factory-driven development

---

## Concrete Example Across All Rehearsals

**Task:** "Create a Python function that validates email addresses"

### Using Rehearsal 1 (Minimal)

```bash
python 01_minimal_factory.py --backend claude \
  "Create a Python function that validates email addresses"

# Result: Raw code blob returned
```

**Pros:** Simple, one call
**Cons:** No validation, no quality gates, might be wrong

### Using Rehearsal 2 (Catalog)

```bash
# First: Analyze
python 02_factory_catalog.py analyzer --backend claude \
  "Analyze requirements for email validation function"

# Then: Plan
python 02_factory_catalog.py planner --backend claude \
  "Create implementation plan for email validation"

# Finally: Fix
python 02_factory_catalog.py fixer --backend claude \
  "Implement email validation function"

# Result: Code analyzed, planned, then implemented by specialized roles
```

**Pros:** Different expertise at each step
**Cons:** Manual coordination, no persistence, no testing

### Using Rehearsal 3 (Resumable)

```bash
# Start
python 03_resumable_factory.py start --backend claude \
  "Create email validation function"

# ... session runs ... Ctrl+C

# Later: Resume
python 03_resumable_factory.py resume --backend claude \
  "Continue, then add tests"

# Result: Work continues from where it left off with full context
```

**Pros:** Resilient, can pause/resume, long-running work supported
**Cons:** No quality gates, manual testing verification

### Using Rehearsal 4 (Spec Loop)

Create `email-spec.json`:
```json
{
  "goal": "Create a Python function that validates email addresses",
  "checks": [
    {"name": "imports", "command": "{python} -c 'from email_validator import validate_email'"},
    {"name": "valid_email", "command": "{python} -c 'assert validate_email(\"test@example.com\")'"},
    {"name": "invalid_email", "command": "{python} -c 'assert not validate_email(\"invalid\")'"}
  ],
  "max_iterations": 5
}
```

```bash
python 04_spec_loop_factory.py --backend claude --spec email-spec.json

# Loop:
# Iteration 1: Implement → checks fail → review → fix
# Iteration 2: Implement → checks fail → review → fix
# Iteration 3: Implement → checks pass → review → approved
```

**Pros:** Automated validation, quality gates, iterative refinement
**Cons:** No session resumption, no role specialization

### Using Rehearsal 5 (Agent Factory)

```bash
python 05_agent_factory.py start email-validator --backend claude

# At prompt:
# Enter agent goal/purpose: Create an agent that validates email addresses
#                          and explains validation results

# Phases:
# SPEC: Spec Writer generates email validator spec
# IMPLEMENT: Developer implements EmailValidator agent
# TEST: Tester creates tests
# REVIEW: Reviewer approves or requests changes
# FIX: Fixer addresses issues (if needed)
# Loop: Repeats until approved

# Result: Complete agent in session-3-ai-agents/agents/email-validator/
```

**Pros:** All concepts: specialized roles, testable, resumable, iterable
**Cons:** Most complex setup, but most robust result

---

## When to Use Each Rehearsal

| Situation | Use | Reason |
|-----------|-----|--------|
| Quick one-off task | Rehearsal 1 | Simple, minimal overhead |
| Task needs different expertise | Rehearsal 2 | Roles provide specialization |
| Work might be interrupted | Rehearsal 3 | Sessions enable recovery |
| Need quality validation | Rehearsal 4 | Loops + checks ensure correctness |
| Generating complex software | Rehearsal 5 | All concepts for production readiness |

---

## Key Takeaway

Each rehearsal **builds on previous concepts** without replacing them:

```
Rehearsal 1: Factory shape
    ↓ Add roles
Rehearsal 2: Specialized behavior
    ↓ Add sessions
Rehearsal 3: Resilient workflows
    ↓ Add loops
Rehearsal 4: Validated iteration
    ↓ Combine all + domain-specific
Rehearsal 5: Production agent factory
```

The Agent Factory (Rehearsal 5) is not "better" than the others—it's **more complete** because it combines all concepts for a specific domain (agent generation).

You can apply the same approach to other domains:
- Code review factory (add your own roles and phases)
- Documentation factory (add doc-generation role)
- Testing factory (add test-generation role)
- Deployment factory (add deployment role)

---

## Next: Create Your Own Factory

Using the Agent Factory as a template, create a factory for your domain:

1. **Define the goal:** What does this factory generate/validate?
2. **Identify roles:** What expertise is needed?
3. **Design phases:** In what order should work happen?
4. **Set quality gates:** How do you know when it's done?
5. **Implement:** Adapt `05_agent_factory.py` for your domain

Example: **Code Review Factory**

```python
class CodeReviewFactory:
    def _phase_analyze(self):
        role = "Code Analyzer - understand the implementation"
    
    def _phase_check_quality(self):
        role = "Quality Reviewer - assess code quality"
    
    def _phase_check_security(self):
        role = "Security Reviewer - identify vulnerabilities"
    
    def _phase_check_performance(self):
        role = "Performance Reviewer - optimize hotspots"
    
    def _phase_approve(self):
        role = "Final Approver - make approval decision"
```

The same architecture, applied to a different domain!
