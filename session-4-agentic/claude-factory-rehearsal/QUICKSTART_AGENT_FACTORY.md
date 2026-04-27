# Agent Factory — Quick Start

## Installation

The agent factory is self-contained. No additional dependencies beyond those in `backend_runner.py`.

## Basic Usage

### 1. Start a New Agent

```bash
cd /path/to/session-4-agentic/claude-factory-rehearsal

python 05_agent_factory.py start my-agent-name --backend claude --timeout 180
```

When prompted, enter the agent's purpose:
```
Enter agent goal/purpose: Create an agent that analyzes customer sentiment from reviews
```

The factory will:
1. Generate a specification for the agent
2. Implement the agent code
3. Create and run tests
4. Review the implementation
5. Fix any issues and re-test
6. Loop until approved (max 8 iterations)

### 2. Resume a Paused Run

If you interrupt a factory run (Ctrl+C), the state is saved. Resume it:

```bash
python 05_agent_factory.py resume my-agent-name
```

The factory will continue from where it left off, with full context restored.

### 3. Check Status

Check the current status of a factory run:

```bash
python 05_agent_factory.py status my-agent-name
```

Output:
```
Agent: my-agent-name
Iteration: 3
Phase: test
Spec (first 200 chars): Agent: Sentiment Analyzer
Purpose: This agent analyzes sentiment in customer reviews...
```

## Example Runs

### Example 1: Simple Agent

```bash
python 05_agent_factory.py start data-validator

# At prompt:
# Enter agent goal/purpose: An agent that validates JSON data structures against schemas
```

Expected phases:
- Spec: ✓ (defines validation logic, error handling)
- Implement: ✓ (creates validator agent)
- Test: ✓ (creates test suite, validates edge cases)
- Review: ✓ (approves if spec is met)
- Done in 1 iteration

### Example 2: Complex Agent with Iterations

```bash
python 05_agent_factory.py start api-docs-generator

# At prompt:
# Enter agent goal/purpose: An agent that reads Python source code and generates API documentation with examples
```

Expected phases:
- Iteration 1: Spec generated, implementation started, tests created
- Iteration 2: Tests fail (missing error handling), review requests fixes
- Iteration 3: Errors fixed, tests pass, review approved
- Done in 3 iterations

### Example 3: Resume After Interruption

```bash
# Start a run
python 05_agent_factory.py start complex-agent
# ... factory runs for a while, then you Ctrl+C

# Later, resume it
python 05_agent_factory.py resume complex-agent

# Factory continues from the last saved phase with full context
```

## What Gets Created

After a successful run, you'll find a new agent in:

```
session-3-ai-agents/agents/my-agent-name/
├── __init__.py
├── agent.py (main implementation)
├── config.py (optional configuration)
├── tests/
│   └── test_agent.py
├── README.md (agent documentation)
└── requirements.txt (if any dependencies)
```

You can then use the agent in your code:

```python
from session_3_ai_agents.agents.my_agent_name.agent import MyAgent

agent = MyAgent()
result = agent.run(input_data)
print(result)
```

## Output Format

The factory prints clear status at each phase:

```
======================================================================
AGENT FACTORY: my-agent-name
======================================================================

--- ITERATION 1/8 ---

[PHASE] Spec Generation...
[ok] Specification generated

[PHASE] Implementation...
[ok] Agent implemented

[PHASE] Testing...
[warn] Some tests failed

[PHASE] Review...
--- REVIEW FEEDBACK ---
FINAL_STATUS: CHANGES_REQUIRED

Issues identified:
1. Error handling missing for invalid input
2. Documentation incomplete

[PHASE] Fixing...
[ok] Issues fixed, looping back to testing...

--- ITERATION 2/8 ---

[PHASE] Testing...
[ok] All tests passed

[PHASE] Review...
--- REVIEW FEEDBACK ---
FINAL_STATUS: APPROVED

✓ Agent factory completed successfully!
```

## Configuration Options

### Backend

Choose which LLM backend to use:

```bash
python 05_agent_factory.py start my-agent --backend claude
python 05_agent_factory.py start my-agent --backend codex
python 05_agent_factory.py start my-agent --backend opencode
```

### Timeout

Set the timeout per phase (in seconds):

```bash
python 05_agent_factory.py start my-agent --timeout 300  # 5 minutes
python 05_agent_factory.py start my-agent --timeout 60   # 1 minute
```

## Troubleshooting

### Q: Factory stopped with error. What happened?

A: Check the status:
```bash
python 05_agent_factory.py status my-agent-name
```

Then check the error message in the console output. Common issues:
- Backend timeout — increase `--timeout`
- Tool permission denied — ensure files exist and are readable
- Spec too vague — provide more detail when starting

### Q: How do I know what state the factory is in?

A: Use `status`:
```bash
python 05_agent_factory.py status my-agent-name
```

Or inspect the session file directly:
```bash
cat .factory-agent-my-agent-name.json | jq .
```

### Q: Can I modify the factory prompts?

A: Yes! Edit the role functions in `05_agent_factory.py`:
```python
def agent_role_developer() -> str:
    return """
You are an Agent Developer. Your role is to:
...
(customize this text)
"""
```

Then restart the factory.

### Q: How many iterations does a typical agent need?

A: It varies:
- **Simple agents** (data validation, format conversion) — 1-2 iterations
- **Medium agents** (analysis, classification) — 2-4 iterations
- **Complex agents** (code generation, multi-step reasoning) — 4-8 iterations

The default max is 8 iterations. Increase if needed by editing `FactoryConfig.max_iterations`.

### Q: Can I resume an old session?

A: Yes, if the session file exists:
```bash
python 05_agent_factory.py resume my-agent-name
```

If the file is deleted, you'll need to start over:
```bash
python 05_agent_factory.py start my-agent-name
```

## Next Steps

1. **Start your first agent:**
   ```bash
   python 05_agent_factory.py start email-classifier
   ```

2. **Inspect the generated agent:**
   ```bash
   ls -la session-3-ai-agents/agents/email-classifier/
   cat session-3-ai-agents/agents/email-classifier/agent.py
   ```

3. **Use the agent in your code:**
   ```python
   from session_3_ai_agents.agents.email_classifier.agent import EmailClassifier
   ```

4. **Extend the factory:**
   - Add new roles or phases in `05_agent_factory.py`
   - Customize prompts for your use case
   - Integrate with CI/CD pipelines

## More Information

- **Full Design:** See [AGENT_FACTORY.md](AGENT_FACTORY.md)
- **Concepts:** See parent factories (`01_*.py`, `02_*.py`, `03_*.py`, `04_*.py`)
- **Backend:** See `backend_runner.py` for LLM execution details
