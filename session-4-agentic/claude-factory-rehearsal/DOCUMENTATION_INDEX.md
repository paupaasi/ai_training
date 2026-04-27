# Agent Factory Documentation Index

Complete guide to the Agent Factory and its integration with factory rehearsals.

## 📚 Documentation Files

### For First-Time Users

**Start here:**
1. [README.md](README.md) — Overview of all 4 factory rehearsals
2. [QUICKSTART_AGENT_FACTORY.md](QUICKSTART_AGENT_FACTORY.md) — Get started in 5 minutes

**Then explore:**
3. [CONCEPT_INTEGRATION.md](CONCEPT_INTEGRATION.md) — How Roles + Sessions + Loops work together
4. [AGENT_FACTORY.md](AGENT_FACTORY.md) — Full design documentation

### For Understanding the Progression

**Learn the concepts:**
1. [01_minimal_factory.py](01_minimal_factory.py) — Simplest factory (start here if reading code)
2. [02_factory_catalog.py](02_factory_catalog.py) — Multiple roles
3. [03_resumable_factory.py](03_resumable_factory.py) — Session persistence
4. [04_spec_loop_factory.py](04_spec_loop_factory.py) — Iterative loops
5. [05_agent_factory.py](05_agent_factory.py) — Unified concept factory
6. [REHEARSALS_COMPARISON.md](REHEARSALS_COMPARISON.md) — How they relate

### For Production Use

1. [AGENT_FACTORY.md](AGENT_FACTORY.md) — Full reference
2. [05_agent_factory.py](05_agent_factory.py) — Source code
3. [CONCEPT_INTEGRATION.md](CONCEPT_INTEGRATION.md) — Extension guide
4. [backend_runner.py](backend_runner.py) — Backend configuration

---

## 🎯 Quick Navigation by Task

### "I want to run the Agent Factory right now"

```bash
# 1. Read quick start
cat QUICKSTART_AGENT_FACTORY.md

# 2. Run it
python 05_agent_factory.py start my-agent --backend claude

# 3. Check status anytime
python 05_agent_factory.py status my-agent
```

→ See: [QUICKSTART_AGENT_FACTORY.md](QUICKSTART_AGENT_FACTORY.md)

---

### "I want to understand how everything works"

1. Read: [CONCEPT_INTEGRATION.md](CONCEPT_INTEGRATION.md)
   - Shows how Roles, Sessions, and Loops combine

2. Read: [REHEARSALS_COMPARISON.md](REHEARSALS_COMPARISON.md)
   - Shows progression from simple to complex factories

3. Skim: [05_agent_factory.py](05_agent_factory.py) source code
   - See how concepts are implemented

→ See: [CONCEPT_INTEGRATION.md](CONCEPT_INTEGRATION.md) and [REHEARSALS_COMPARISON.md](REHEARSALS_COMPARISON.md)

---

### "I want to customize the Agent Factory"

1. Read: [AGENT_FACTORY.md](AGENT_FACTORY.md) → "Extending the Factory" section
2. Review: [05_agent_factory.py](05_agent_factory.py) → role definitions
3. Modify role functions or add new phases
4. Test with: `python 05_agent_factory.py start test-agent`

→ See: [AGENT_FACTORY.md](AGENT_FACTORY.md) → "Extending the Factory"

---

### "I want to create my own factory for a different domain"

1. Read: [REHEARSALS_COMPARISON.md](REHEARSALS_COMPARISON.md) → "Next: Create Your Own Factory"
2. Copy: [05_agent_factory.py](05_agent_factory.py)
3. Customize: Replace roles, phases, and domain-specific logic
4. Reference: [CONCEPT_INTEGRATION.md](CONCEPT_INTEGRATION.md) for architecture

→ See: [REHEARSALS_COMPARISON.md](REHEARSALS_COMPARISON.md) → bottom section

---

### "Something went wrong, I need troubleshooting"

→ See: [QUICKSTART_AGENT_FACTORY.md](QUICKSTART_AGENT_FACTORY.md) → "Troubleshooting"

Common issues:
- Factory stopped with error → Check status
- Want to resume → Use `resume` command
- Want to inspect state → View `.factory-agent-<name>.json`
- Want to restart → Delete session file and re-run

---

### "I want to extend with new roles or phases"

→ See: [AGENT_FACTORY.md](AGENT_FACTORY.md) → "Configuration" section

Steps:
1. Define new role function (copy existing, modify text)
2. Create phase method (copy existing, modify prompt)
3. Add to factory loop in `run()` method

Example:
```python
def agent_role_my_role() -> str:
    return "You are a ..."

def _phase_my_phase(self) -> bool:
    prompt = build_my_phase_prompt(...)
    result = run_sync(...)
    return result.ok
```

---

## 📖 Reading Order

### For Learning (Beginner → Expert)

```
Day 1: Concepts
  → README.md (overview)
  → QUICKSTART_AGENT_FACTORY.md (practical intro)

Day 2: Understanding
  → CONCEPT_INTEGRATION.md (how it works)
  → REHEARSALS_COMPARISON.md (context and history)

Day 3: Deep Dive
  → 01_minimal_factory.py (read code)
  → 02_factory_catalog.py (read code)
  → 03_resumable_factory.py (read code)
  → 04_spec_loop_factory.py (read code)
  → 05_agent_factory.py (read code)

Day 4: Production
  → AGENT_FACTORY.md (full reference)
  → Customize and extend
```

### For Implementation (Get Things Done)

```
1. README.md (5 min) — Understand what exists
2. QUICKSTART_AGENT_FACTORY.md (15 min) — Get started
3. Run first agent (30 min) — Try it
4. AGENT_FACTORY.md (30 min) — Reference for customization
5. Extend or adapt (ongoing)
```

---

## 🔍 File Structure

```
session-4-agentic/claude-factory-rehearsal/
│
├── 📄 Factory Scripts (in order of complexity)
│   ├── 01_minimal_factory.py          ⭐ Start here if reading code
│   ├── 02_factory_catalog.py          ⭐⭐ Multiple roles
│   ├── 03_resumable_factory.py        ⭐⭐ Session persistence
│   ├── 04_spec_loop_factory.py        ⭐⭐⭐ Iterative loops
│   ├── 05_agent_factory.py            ⭐⭐⭐⭐⭐ All concepts combined
│   └── backend_runner.py              Backend adapter (don't modify)
│
├── 📚 Documentation (reading order below)
│   ├── README.md                      Overview of all rehearsals
│   ├── QUICKSTART_AGENT_FACTORY.md    ← START HERE (quick intro)
│   ├── CONCEPT_INTEGRATION.md         How concepts work together
│   ├── REHEARSALS_COMPARISON.md       Progression and comparison
│   ├── AGENT_FACTORY.md               Full reference & design
│   └── 📄 DOCUMENTATION_INDEX.md      This file!
│
└── 📋 Configuration
    ├── spec.example.json              Example spec for rehearsal 4
    └── (Session files auto-created)
        └── .factory-agent-<name>.json State persistence
```

---

## 🚀 Common Workflows

### Workflow 1: Generate a New Agent (5 min setup, run time varies)

```bash
# 1. Start factory
python 05_agent_factory.py start sentiment-analyzer

# Prompt: "Create an agent that analyzes sentiment in reviews"

# 2. Factory runs automatically:
#    - Generates spec
#    - Implements agent
#    - Tests implementation
#    - Reviews for quality
#    - Fixes issues if needed
#    - Repeats until approved

# 3. Check result
ls -la ../session-3-ai-agents/agents/sentiment-analyzer/
```

### Workflow 2: Resume Interrupted Work (1 min)

```bash
# Interrupted mid-run? No problem.

# Just resume
python 05_agent_factory.py resume sentiment-analyzer

# Continues from where it left off with full context
```

### Workflow 3: Inspect Intermediate State (1 min)

```bash
# Want to see what's been done?
python 05_agent_factory.py status sentiment-analyzer

# Or view raw state
cat .factory-agent-sentiment-analyzer.json | jq .
```

### Workflow 4: Customize Roles (30 min)

```bash
# 1. Edit 05_agent_factory.py
vi 05_agent_factory.py

# 2. Find role functions (search for "def agent_role_")
# 3. Modify text to customize behavior
# 4. Save and test

python 05_agent_factory.py start custom-agent

# Your customized roles are now active
```

### Workflow 5: Create New Factory for Different Domain (2-4 hours)

```bash
# 1. Copy agent factory as template
cp 05_agent_factory.py 06_my_custom_factory.py

# 2. Customize:
#    - Change factory name
#    - Add/remove roles
#    - Modify phases
#    - Update prompts for your domain

# 3. Test
python 06_my_custom_factory.py start test-run

# 4. Iterate and refine
```

---

## 📊 Documentation Map

```
                        README.md
                            ↓
                  (Choose your path)
                      ↙    ↓    ↘
                     /     |     \
            I'm new      I'm      I'm
            to this    learning  building

              ↓           ↓         ↓
        QUICKSTART    CONCEPT   AGENT_FACTORY
        (5 min)     INTEGRATION (full ref)
                    (30 min)
              ↓           ↓         ↓
          Run it!   Understand   Customize
         Then read   progression  & extend
         AGENT_     REHEARSALS_  CONCEPT_
         FACTORY      COMPARISON  INTEGRATION
              ↓           ↓         ↓
        Refer to     Master all   Build your
        full ref     concepts     own factory
```

---

## 🎓 Learning Outcomes

After working through all materials, you'll understand:

- ✅ What a software factory is and why it matters
- ✅ How roles enable specialized behavior
- ✅ How session persistence enables resilience
- ✅ How spec-driven loops ensure quality
- ✅ How to combine all three for production automation
- ✅ How to extend factories for your domain
- ✅ When to use each factory pattern

---

## 💡 Tips & Tricks

### Tip 1: Increasing Timeout for Complex Agents

```bash
python 05_agent_factory.py start my-agent --timeout 600

# Default is 180 seconds (3 min)
# Use 600 for complex agents (10 min per phase)
```

### Tip 2: Using Different Backends

```bash
# Claude (recommended)
python 05_agent_factory.py start my-agent --backend claude

# Codex (faster, less capable)
python 05_agent_factory.py start my-agent --backend codex

# OpenCode (experimental)
python 05_agent_factory.py start my-agent --backend opencode
```

### Tip 3: Customizing Max Iterations

Edit `FactoryConfig` in source code:
```python
@dataclass
class FactoryConfig:
    ...
    max_iterations: int = 8  # ← Change here
```

### Tip 4: Debugging Phase Prompts

Add debug prints in `05_agent_factory.py`:
```python
def _phase_spec(self, agent_goal: str) -> bool:
    prompt = build_spec_phase_prompt(...)
    print(f"[DEBUG] SPEC PROMPT:\n{prompt}\n")  # ← Add this
    result = run_sync(...)
```

---

## 🔗 External References

- [Backend Runner](backend_runner.py) — LLM backend integration
- [Session 3 AI Agents](../agents/) — Generated agents output
- [Spec Format](spec.example.json) — Example specification

---

## ✉️ Questions?

**Check these in order:**

1. [QUICKSTART_AGENT_FACTORY.md](QUICKSTART_AGENT_FACTORY.md) → "Troubleshooting"
2. [AGENT_FACTORY.md](AGENT_FACTORY.md) → "Error Handling"
3. Review [CONCEPT_INTEGRATION.md](CONCEPT_INTEGRATION.md) for architecture
4. Inspect source code in [05_agent_factory.py](05_agent_factory.py)

---

**Happy factory building!** 🏭✨
