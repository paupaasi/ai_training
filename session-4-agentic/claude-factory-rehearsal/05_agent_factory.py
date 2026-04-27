"""
Agent Factory: A specialized factory for implementing and validating new agents.

Combines three core concepts:
1. ROLES — specialized factory personas (spec-writer, developer, tester, reviewer)
2. RESUMES — session-based resumption to continue previous work
3. LOOPS — iterative implement → test → review cycle

Workflow:
  1. SPEC GENERATION: Create or refine agent specification
  2. IMPLEMENTATION: Code the agent based on spec
  3. TESTING: Run validation checks
  4. REVIEW: Assess completeness and quality
  5. FIXING: Address any issues found
  → Loop back to TESTING until approved

Usage:
  python 05_agent_factory.py start <agent_name> [--backend claude] [--timeout 180]
  python 05_agent_factory.py resume <agent_name> [--backend claude] [--timeout 180]
  python 05_agent_factory.py status <agent_name>
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from backend_runner import Backend, BackendRunOptions, get_default_cwd, run_sync


# ============================================================================
# Configuration & State Management
# ============================================================================


@dataclass
class FactoryConfig:
    """Configuration for agent factory."""

    agent_name: str
    backend: Backend = "claude"  # type: ignore[assignment]
    timeout: int = 180
    agent_max_turns: int = 25
    permission_mode: str = "acceptEdits"
    max_iterations: int = 8


def session_file_for(agent_name: str) -> Path:
    """Return session file path for an agent."""
    return Path(f".factory-agent-{agent_name}.json")


@dataclass
class SessionState:
    """Persisted session state for resumption."""

    agent_name: str
    session_id: str | None = None
    iteration: int = 0
    phase: str = "spec"  # spec, implement, test, review, fix
    spec_content: str = ""
    test_results: dict[str, Any] | None = None
    review_feedback: str = ""

    def save(self) -> None:
        """Persist session state to file."""
        file = session_file_for(self.agent_name)
        file.write_text(json.dumps(asdict(self)), encoding="utf-8")

    @staticmethod
    def load(agent_name: str) -> SessionState | None:
        """Load persisted session state."""
        file = session_file_for(agent_name)
        if not file.exists():
            return None
        data = json.loads(file.read_text(encoding="utf-8"))
        return SessionState(**data)

    @staticmethod
    def new(agent_name: str) -> SessionState:
        """Create fresh session state."""
        return SessionState(agent_name=agent_name, iteration=1, phase="spec")


# ============================================================================
# Agent Role Definitions
# ============================================================================


def agent_role_spec_writer() -> str:
    """Role: Agent Specification Writer — creates comprehensive agent specs."""
    return """
You are an Agent Specification Writer. Your role is to:
1. Analyze the agent goal and requirements
2. Write clear, comprehensive agent specifications including:
   - Agent purpose (1-2 sentences)
   - Core responsibilities and capabilities
   - Input/output contracts
   - Key dependencies and integrations
   - Success criteria and test scenarios
3. Ensure specs are actionable and detailed enough for a developer

Format your spec in a structured markdown format with sections:
## Agent: [Name]
## Purpose
## Responsibilities
## Input/Output Contract
## Dependencies
## Success Criteria (list of testable conditions)

Your spec should be ready for immediate implementation.
""".strip()


def agent_role_developer() -> str:
    """Role: Agent Developer — implements agents following specs."""
    return """
You are an Agent Developer. Your role is to:
1. Read the agent specification carefully
2. Implement the agent code following best practices:
   - Clear class/function organization
   - Proper error handling
   - Comprehensive docstrings
   - Type hints where applicable
   - Integration with specified dependencies
3. Create supporting files (config, utilities, etc.) as needed
4. Ensure code follows the project's patterns and conventions

Focus on clean, readable, testable code. Do not over-engineer.
""".strip()


def agent_role_tester() -> str:
    """Role: Agent Tester — creates and runs validation tests."""
    return """
You are an Agent Tester. Your role is to:
1. Create comprehensive test scenarios based on the agent spec
2. Implement test scripts that validate:
   - Core functionality works as specified
   - Edge cases are handled properly
   - Dependencies are properly integrated
   - Error conditions are managed
3. Run tests and report results clearly
4. Provide actionable failure information

Tests should directly verify success criteria from the spec.
""".strip()


def agent_role_reviewer() -> str:
    """Role: Agent Code Reviewer — assesses completeness and quality."""
    return """
You are an Agent Code Reviewer. Your role is to:
1. Review the agent implementation against its specification
2. Assess:
   - Does implementation match spec requirements? (✓/✗)
   - Are all responsibilities covered?
   - Is code quality acceptable?
   - Are tests comprehensive and passing?
3. Identify gaps, issues, or improvement needs
4. Return a structured review with:
   - Overall status (APPROVED or CHANGES_REQUIRED)
   - List of issues (if any)
   - Priority of required changes

Be thorough but fair. Don't block on minor style issues.
""".strip()


def agent_role_fixer() -> str:
    """Role: Agent Problem Fixer — diagnoses and resolves issues."""
    return """
You are an Agent Problem Fixer. Your role is to:
1. Analyze test failures and review feedback
2. Identify root causes of failures
3. Make minimal, targeted fixes to resolve issues
4. Re-run relevant tests to validate fixes
5. Report what was fixed and why

Focus on the most impactful issues first. Make surgical changes.
""".strip()


# ============================================================================
# Phase Builders — Build prompts for each factory phase
# ============================================================================


def build_spec_phase_prompt(
    agent_goal: str,
    agent_name: str,
    previous_spec: str | None = None,
    review_feedback: str | None = None,
) -> str:
    """Build prompt for SPEC GENERATION phase."""
    role = agent_role_spec_writer()

    if previous_spec and review_feedback:
        return f"""{role}

AGENT NAME: {agent_name}
GOAL: {agent_goal}

You previously wrote a spec for this agent. Review feedback indicated:
{review_feedback}

TASK: Revise and improve the specification to address the feedback.

PREVIOUS SPEC:
{previous_spec}

Write an improved specification that addresses all feedback.
""".strip()

    return f"""{role}

AGENT NAME: {agent_name}
GOAL: {agent_goal}

TASK: Write a comprehensive specification for this agent.

The specification should be detailed enough that a developer can immediately
begin implementation. Include all sections: Purpose, Responsibilities,
Input/Output Contract, Dependencies, Success Criteria.
""".strip()


def build_implement_phase_prompt(
    agent_name: str,
    spec_content: str,
    previous_code_issues: str | None = None,
) -> str:
    """Build prompt for IMPLEMENTATION phase."""
    role = agent_role_developer()

    if previous_code_issues:
        return f"""{role}

AGENT: {agent_name}

Previous implementation had issues:
{previous_code_issues}

SPECIFICATION:
{spec_content}

TASK: Fix the implementation to resolve the issues above while following
the specification exactly.
""".strip()

    return f"""{role}

AGENT: {agent_name}

SPECIFICATION:
{spec_content}

TASK: Implement this agent according to the specification. Create all
necessary files in the session-3-ai-agents/agents/{agent_name}/ directory.

Ensure:
- Code is clean, readable, and well-documented
- All spec requirements are met
- Error handling is comprehensive
- The agent can be imported and used immediately
""".strip()


def build_test_phase_prompt(agent_name: str, spec_content: str) -> str:
    """Build prompt for TESTING phase."""
    role = agent_role_tester()

    return f"""{role}

AGENT: {agent_name}

SPECIFICATION:
{spec_content}

TASK: Create comprehensive tests that validate the agent implementation
against all success criteria in the spec. Then run the tests and report
results.

Create test files in session-3-ai-agents/agents/{agent_name}/tests/.

Report format:
[PASS] <test name>
[FAIL] <test name>: <reason>
[ERROR] <test name>: <error message>

Summary:
- Total tests: X
- Passed: X
- Failed: X
""".strip()


def build_review_phase_prompt(
    agent_name: str,
    spec_content: str,
    test_results_summary: str,
) -> str:
    """Build prompt for REVIEW phase."""
    role = agent_role_reviewer()

    return f"""{role}

AGENT: {agent_name}

SPECIFICATION:
{spec_content}

TEST RESULTS:
{test_results_summary}

TASK: Review the agent implementation for completeness and quality.
Then output your verdict exactly as shown:

FINAL_STATUS: APPROVED
or
FINAL_STATUS: CHANGES_REQUIRED

If changes required, list the most critical issues:
1. <issue description>
2. <issue description>
""".strip()


def build_fix_phase_prompt(
    agent_name: str,
    review_feedback: str,
) -> str:
    """Build prompt for FIXING phase."""
    role = agent_role_fixer()

    return f"""{role}

AGENT: {agent_name}

REVIEW FEEDBACK:
{review_feedback}

TASK: Fix the agent implementation to resolve the issues identified in
the review feedback. Be surgical — make targeted changes only.

After making fixes, run the tests again to validate they resolve the issues.
""".strip()


# ============================================================================
# Factory State Machine
# ============================================================================


class AgentFactory:
    """Factory for generating and validating new agents."""

    def __init__(self, config: FactoryConfig) -> None:
        self.config = config
        self.state = SessionState.new(config.agent_name)
        self.agent_dir = (
            Path("/Users/pauliina.paasivirta/VSCode/ai_training/session-3-ai-agents/agents")
            / config.agent_name
        )

    def load_or_new(self) -> None:
        """Load existing session or create new."""
        loaded = SessionState.load(self.config.agent_name)
        if loaded:
            self.state = loaded
        else:
            self.state = SessionState.new(self.config.agent_name)

    def save_state(self) -> None:
        """Persist current state."""
        self.state.save()

    def run(self, agent_goal: str) -> int:
        """Execute the agent factory loop."""
        print(f"\n{'='*70}")
        print(f"AGENT FACTORY: {self.config.agent_name}")
        print(f"{'='*70}\n")

        for iteration in range(self.state.iteration, self.config.max_iterations + 1):
            print(f"\n--- ITERATION {iteration}/{self.config.max_iterations} ---")
            self.state.iteration = iteration

            try:
                if not self._phase_spec(agent_goal):
                    return 1
                self.state.phase = "implement"
                self.save_state()

                if not self._phase_implement():
                    return 1
                self.state.phase = "test"
                self.save_state()

                if not self._phase_test():
                    return 1
                self.state.phase = "review"
                self.save_state()

                approved = self._phase_review()
                self.state.phase = "review"
                self.save_state()

                if approved:
                    print("\n✓ Agent factory completed successfully!")
                    return 0

                self.state.phase = "fix"
                self.save_state()
                if not self._phase_fix():
                    return 1

            except KeyboardInterrupt:
                print("\n[info] Factory paused. Resume with: python 05_agent_factory.py resume <name>")
                self.save_state()
                return 1
            except Exception as e:
                print(f"\n[error] Unexpected error: {e}")
                self.save_state()
                return 1

        print("\n[warn] Reached max iterations without completion.")
        return 1

    def _phase_spec(self, agent_goal: str) -> bool:
        """SPEC GENERATION phase."""
        print("\n[PHASE] Spec Generation...")

        prompt = build_spec_phase_prompt(
            agent_goal=agent_goal,
            agent_name=self.config.agent_name,
            previous_spec=self.state.spec_content if self.state.iteration > 1 else None,
            review_feedback=self.state.review_feedback if self.state.iteration > 1 else None,
        )

        result = run_sync(
            BackendRunOptions(
                backend=self.config.backend,  # type: ignore[arg-type]
                prompt=prompt,
                cwd=get_default_cwd(),
                allowed_tools=["Read", "Glob"],
                permission_mode="default",
                max_turns=15,
                resume_session_id=self.state.session_id,
                timeout_seconds=self.config.timeout,
            )
        )

        if not result.ok:
            print(f"[error] Spec generation failed: {result.stop_reason}")
            return False

        self.state.session_id = result.session_id or self.state.session_id
        self.state.spec_content = result.text or ""
        print("[ok] Specification generated")
        print(f"\n{self.state.spec_content[:800]}...\n")
        return True

    def _phase_implement(self) -> bool:
        """IMPLEMENTATION phase."""
        print("\n[PHASE] Implementation...")

        prompt = build_implement_phase_prompt(
            agent_name=self.config.agent_name,
            spec_content=self.state.spec_content,
            previous_code_issues=None,  # TODO: extract from test/review results
        )

        result = run_sync(
            BackendRunOptions(
                backend=self.config.backend,  # type: ignore[arg-type]
                prompt=prompt,
                cwd=get_default_cwd(),
                allowed_tools=["Read", "Glob", "Grep", "Edit", "Bash"],
                permission_mode="acceptEdits",
                max_turns=self.config.agent_max_turns,
                resume_session_id=self.state.session_id,
                timeout_seconds=self.config.timeout,
            )
        )

        if not result.ok:
            print(f"[error] Implementation failed: {result.stop_reason}")
            return False

        self.state.session_id = result.session_id or self.state.session_id
        print("[ok] Agent implemented")
        return True

    def _phase_test(self) -> bool:
        """TESTING phase."""
        print("\n[PHASE] Testing...")

        prompt = build_test_phase_prompt(
            agent_name=self.config.agent_name,
            spec_content=self.state.spec_content,
        )

        result = run_sync(
            BackendRunOptions(
                backend=self.config.backend,  # type: ignore[arg-type]
                prompt=prompt,
                cwd=get_default_cwd(),
                allowed_tools=["Read", "Glob", "Grep", "Edit", "Bash"],
                permission_mode="acceptEdits",
                max_turns=self.config.agent_max_turns,
                resume_session_id=self.state.session_id,
                timeout_seconds=self.config.timeout,
            )
        )

        if not result.ok:
            print(f"[error] Testing failed: {result.stop_reason}")
            return False

        self.state.session_id = result.session_id or self.state.session_id
        self.state.test_results = {"output": result.text or ""}

        # Parse test summary
        output = result.text or ""
        if "[FAIL]" in output or "[ERROR]" in output:
            print("[warn] Some tests failed")
            print(f"\n{output[-1000:]}\n")
        else:
            print("[ok] All tests passed")

        return True

    def _phase_review(self) -> bool:
        """REVIEW phase — returns True if approved."""
        print("\n[PHASE] Review...")

        test_summary = self.state.test_results.get("output", "") if self.state.test_results else ""

        prompt = build_review_phase_prompt(
            agent_name=self.config.agent_name,
            spec_content=self.state.spec_content,
            test_results_summary=test_summary,
        )

        result = run_sync(
            BackendRunOptions(
                backend=self.config.backend,  # type: ignore[arg-type]
                prompt=prompt,
                cwd=get_default_cwd(),
                allowed_tools=["Read", "Glob", "Grep"],
                permission_mode="default",
                max_turns=12,
                resume_session_id=self.state.session_id,
                timeout_seconds=self.config.timeout,
            )
        )

        if not result.ok:
            print(f"[error] Review failed: {result.stop_reason}")
            return False

        self.state.session_id = result.session_id or self.state.session_id
        review_text = result.text or ""
        self.state.review_feedback = review_text

        print("\n--- REVIEW FEEDBACK ---")
        print(f"{review_text[:1200]}\n")

        approved = "FINAL_STATUS: APPROVED" in review_text.upper()
        if approved:
            print("[ok] Review approved implementation")
        else:
            print("[info] Review requested changes")

        return approved

    def _phase_fix(self) -> bool:
        """FIXING phase."""
        print("\n[PHASE] Fixing...")

        prompt = build_fix_phase_prompt(
            agent_name=self.config.agent_name,
            review_feedback=self.state.review_feedback,
        )

        result = run_sync(
            BackendRunOptions(
                backend=self.config.backend,  # type: ignore[arg-type]
                prompt=prompt,
                cwd=get_default_cwd(),
                allowed_tools=["Read", "Glob", "Grep", "Edit", "Bash"],
                permission_mode="acceptEdits",
                max_turns=self.config.agent_max_turns,
                resume_session_id=self.state.session_id,
                timeout_seconds=self.config.timeout,
            )
        )

        if not result.ok:
            print(f"[error] Fixing failed: {result.stop_reason}")
            return False

        self.state.session_id = result.session_id or self.state.session_id
        print("[ok] Issues fixed, looping back to testing...")
        self.state.phase = "test"  # Loop back to testing
        return True


# ============================================================================
# CLI Interface
# ============================================================================


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Agent Factory: Generate and validate new agents with spec-driven loops",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python 05_agent_factory.py start my-agent --backend claude
  python 05_agent_factory.py resume my-agent
  python 05_agent_factory.py status my-agent
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to run")

    # START command
    start = subparsers.add_parser("start", help="Start a new agent factory run")
    start.add_argument("agent_name", help="Name of the agent to create")
    start.add_argument("--goal", help="Agent goal/purpose (interactive if not provided)")
    start.add_argument(
        "--backend", choices=["claude", "codex", "opencode"], default="claude"
    )
    start.add_argument("--timeout", type=int, default=180, help="Timeout in seconds")

    # RESUME command
    resume = subparsers.add_parser("resume", help="Resume a paused agent factory run")
    resume.add_argument("agent_name", help="Name of the agent to resume")
    resume.add_argument(
        "--backend", choices=["claude", "codex", "opencode"], default="claude"
    )
    resume.add_argument("--timeout", type=int, default=180, help="Timeout in seconds")

    # STATUS command
    status = subparsers.add_parser("status", help="Check status of an agent factory run")
    status.add_argument("agent_name", help="Name of the agent to check")

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.command == "status":
        state = SessionState.load(args.agent_name)
        if not state:
            print(f"[info] No session found for agent '{args.agent_name}'")
            return

        print(f"\nAgent: {state.agent_name}")
        print(f"Iteration: {state.iteration}")
        print(f"Phase: {state.phase}")
        if state.spec_content:
            print(f"Spec (first 200 chars): {state.spec_content[:200]}...")
        return

    # START or RESUME
    config = FactoryConfig(
        agent_name=args.agent_name,
        backend=args.backend,  # type: ignore[arg-type]
        timeout=args.timeout,
    )

    factory = AgentFactory(config)

    if args.command == "start":
        goal = args.goal or input("\nEnter agent goal/purpose: ").strip()
        if not goal:
            raise SystemExit("Agent goal is required")
        exit_code = factory.run(goal)
    else:  # resume
        factory.load_or_new()
        if not factory.state.spec_content:
            raise SystemExit(
                f"No previous session found for agent '{args.agent_name}'. "
                "Use 'start' instead."
            )
        # For resume, we need the original goal — extract from spec if possible
        goal = f"Resume work on: {factory.state.spec_content[:100]}"
        exit_code = factory.run(goal)

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
