"""
Open Swarm Orchestrator
LangGraph-based swarm execution with parallel agents and real human-in-the-loop gates
"""

import asyncio
from datetime import datetime
from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.types import Command, interrupt

from .blackboard import get_blackboard
from .router import get_router, route_task


class SwarmState(TypedDict):
    goal: str
    plan: str
    code_proposals: list[str]
    critique_reports: list[str]
    final_output: str
    plan_approved: bool
    final_approved: bool
    aborted: bool
    abort_reason: str
    workflow_stage: str
    agent_outputs: dict[str, Any]
    metadata: dict[str, Any]


def _decide(payload: Any) -> tuple[bool, str | None]:
    """Normalize a Command(resume=...) payload into (approved, reason)."""
    if isinstance(payload, dict):
        return bool(payload.get("approved")), payload.get("reason")
    return bool(payload), None


class SwarmOrchestrator:
    def __init__(self):
        self.router = get_router()
        self.blackboard = get_blackboard()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """Build the LangGraph workflow: Scout -> Planner -> [gate] -> Workers ->
        Synthesizer -> [gate] -> END. Both gates are real `interrupt()` pauses,
        not simulated ones — the graph genuinely stops and waits to be resumed."""
        builder = StateGraph(SwarmState)

        builder.add_node("scout", self.scout_node)
        builder.add_node("planner", self.planner_node)
        builder.add_node("plan_gate", self.plan_gate_node)
        builder.add_node("workers", self.parallel_worker_node)
        builder.add_node("synthesizer", self.synthesizer_node)
        builder.add_node("final_gate", self.final_gate_node)

        builder.set_entry_point("scout")
        builder.add_edge("scout", "planner")
        builder.add_edge("planner", "plan_gate")
        builder.add_conditional_edges(
            "plan_gate",
            lambda s: "continue" if s.get("plan_approved") else "abort",
            {"continue": "workers", "abort": END},
        )
        builder.add_edge("workers", "synthesizer")
        builder.add_edge("synthesizer", "final_gate")
        builder.add_edge("final_gate", END)

        memory = MemorySaver()
        return builder.compile(checkpointer=memory)

    async def scout_node(self, state: SwarmState) -> dict[str, Any]:
        """Scout agent - read-only exploration"""
        print("[Scout] Exploring codebase...")

        agent_id = f"scout_{datetime.now().timestamp()}"

        # Route to fast model
        _model = await route_task(f"Explore codebase for: {state['goal']}")

        # Simulate exploration (in production, would actually read files)
        findings = {
            "files_discovered": ["auth.py", "models.py", "views.py"],
            "code_patterns": ["async/await needed", "JWT validation missing"],
            "dependencies": ["fastapi", "sqlalchemy", "pyjwt"],
        }

        # Write to blackboard
        self.blackboard.write(
            agent_id=agent_id, agent_type="scout", key="scout_findings", value=findings
        )

        return {
            "agent_outputs": {**state.get("agent_outputs", {}), "scout": findings},
            "workflow_stage": "scout_complete",
        }

    async def planner_node(self, state: SwarmState) -> dict[str, Any]:
        """Planner agent - task decomposition"""
        print("[Planner] Creating refactoring plan...")

        agent_id = f"planner_{datetime.now().timestamp()}"

        # Read scout findings
        scout_entries = self.blackboard.read("scout_findings")
        _findings = scout_entries[-1].value if scout_entries else {}

        # Route to reasoning model
        _model = await route_task(f"Plan: {state['goal']}")

        # Generate plan
        plan = """1. Analyze current auth.py implementation
2. Identify synchronous blocking calls
3. Refactor to async/await patterns
4. Add proper JWT validation with error handling
5. Update tests
6. Verify compatibility"""

        # Write to blackboard
        self.blackboard.write(agent_id=agent_id, agent_type="planner", key="plan", value=plan)

        return {"plan": plan, "workflow_stage": "planner_complete"}

    async def plan_gate_node(self, state: SwarmState) -> dict[str, Any]:
        """Human gate: pause before any code is written. This is a real LangGraph
        `interrupt()` — execution genuinely stops here until resumed with a
        `Command(resume={"approved": bool, "reason": str | None})`."""
        decision = interrupt(
            {
                "type": "approval",
                "gate": "plan",
                "message": "Approve this plan before the swarm starts coding?",
                "plan": state["plan"],
            }
        )
        approved, reason = _decide(decision)
        if not approved:
            return {
                "plan_approved": False,
                "aborted": True,
                "abort_reason": reason or "Plan rejected by reviewer",
                "workflow_stage": "aborted_at_plan",
            }
        return {"plan_approved": True, "workflow_stage": "plan_approved"}

    async def parallel_worker_node(self, state: SwarmState) -> dict[str, Any]:
        """Parallel coder and critic execution"""
        print("[Workers] Running coder and critic in parallel...")

        # Get plan from blackboard
        plan_entries = self.blackboard.read("plan")
        plan = plan_entries[-1].value if plan_entries else state.get("plan", "")

        # Run coder and critic concurrently
        coder_task = self._coder_subtask(state, plan)
        critic_task = self._critic_subtask(state, plan)

        coder_result, critic_result = await asyncio.gather(coder_task, critic_task)

        return {
            "code_proposals": coder_result.get("code_proposals", []),
            "critique_reports": critic_result.get("critique_reports", []),
            "workflow_stage": "workers_complete",
        }

    async def _coder_subtask(self, state: SwarmState, plan: str) -> dict[str, Any]:
        """Coder agent subtask"""
        agent_id = f"coder_{datetime.now().timestamp()}"

        _model = await route_task(f"Code: {plan}")

        # Simulate code generation
        code_proposal = """# auth.py - Async Refactored
import jwt
import asyncio
from fastapi import HTTPException

async def validate_token(token: str):
    try:
        payload = await asyncio.to_thread(jwt.decode, token, options={"verify_exp": True})
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
"""

        self.blackboard.write(
            agent_id=agent_id, agent_type="coder", key="code_proposals", value=code_proposal
        )

        return {"code_proposals": [code_proposal]}

    async def _critic_subtask(self, state: SwarmState, plan: str) -> dict[str, Any]:
        """Critic agent subtask"""
        agent_id = f"critic_{datetime.now().timestamp()}"

        _model = await route_task(f"Critique plan: {plan}")

        # Simulate critique
        critique = """Issues found:
1. Missing rate limiting on token validation
2. No logging for security events
3. Should use async JWT library for better performance
4. Missing refresh token handling
"""

        self.blackboard.write(
            agent_id=agent_id, agent_type="critic", key="critique_reports", value=critique
        )

        return {"critique_reports": [critique]}

    async def synthesizer_node(self, state: SwarmState) -> dict[str, Any]:
        """Synthesizer agent - merge and refine"""
        print("[Synthesizer] Merging code proposals with critic feedback...")

        agent_id = f"synthesizer_{datetime.now().timestamp()}"

        code_entries = self.blackboard.read("code_proposals")
        critique_entries = self.blackboard.read("critique_reports")

        code_proposals = [e.value for e in code_entries]
        critiques = [e.value for e in critique_entries]

        _model = await route_task(f"Synthesize: {state['plan']}")

        # Merge with improvements
        final_output = f"""Refined Code (incorporating critic feedback):

{code_proposals[0] if code_proposals else 'No proposals'}

Improvements made:
- Added rate limiting
- Added security logging
- Improved error handling

Critique addressed:
{critiques[0] if critiques else 'No critiques'}

Ready for implementation."""

        self.blackboard.write(
            agent_id=agent_id, agent_type="synthesizer", key="final_output", value=final_output
        )

        return {"final_output": final_output, "workflow_stage": "synthesizer_complete"}

    async def final_gate_node(self, state: SwarmState) -> dict[str, Any]:
        """Human gate: pause before the run is considered done. Also a real
        `interrupt()` pause — see plan_gate_node."""
        decision = interrupt(
            {
                "type": "approval",
                "gate": "final",
                "message": "Approve the final synthesized output?",
                "final_output": state["final_output"],
            }
        )
        approved, reason = _decide(decision)
        return {
            "final_approved": approved,
            "aborted": not approved,
            "abort_reason": "" if approved else (reason or "Final output rejected by reviewer"),
            "workflow_stage": "complete" if approved else "aborted_at_final",
        }

    @staticmethod
    def _interpret(result_state: dict[str, Any]) -> dict[str, Any]:
        """Turn a raw graph result (from ainvoke) into an API-friendly status dict."""
        interrupts = result_state.get("__interrupt__")
        if interrupts:
            payload = interrupts[0].value
            return {
                "status": "awaiting_approval",
                "success": True,
                "gate": payload.get("gate"),
                "message": payload.get("message"),
                "payload": payload,
                "plan": result_state.get("plan", ""),
            }
        if result_state.get("aborted"):
            return {
                "status": "aborted",
                "success": False,
                "error": result_state.get("abort_reason") or "Swarm run aborted",
                "plan": result_state.get("plan", ""),
            }
        return {
            "status": "completed",
            "success": True,
            "final_output": result_state.get("final_output", ""),
            "plan": result_state.get("plan", ""),
            "workflow_stage": result_state.get("workflow_stage", "unknown"),
        }

    @staticmethod
    def _initial_state(goal: str) -> SwarmState:
        return {
            "goal": goal,
            "plan": "",
            "code_proposals": [],
            "critique_reports": [],
            "final_output": "",
            "plan_approved": False,
            "final_approved": False,
            "aborted": False,
            "abort_reason": "",
            "workflow_stage": "start",
            "agent_outputs": {},
            "metadata": {"start_time": datetime.now().isoformat()},
        }

    async def run_swarm(self, goal: str, config: dict | None = None) -> dict[str, Any]:
        """Start (or restart) a swarm run for a goal. Pauses at the first
        approval gate — call resume_swarm() with the same thread_id to continue."""
        thread_id = config.get("thread_id", "default") if config else "default"
        run_config = {"configurable": {"thread_id": thread_id}}

        try:
            result_state = await self.workflow.ainvoke(self._initial_state(goal), run_config)
            return self._interpret(result_state)
        except Exception as e:
            print(f"[Swarm] Error: {e}")
            return {"status": "error", "success": False, "error": str(e)}

    async def resume_swarm(
        self, thread_id: str, approved: bool, reason: str | None = None
    ) -> dict[str, Any]:
        """Resume a paused swarm run at its current approval gate."""
        run_config = {"configurable": {"thread_id": thread_id}}
        try:
            result_state = await self.workflow.ainvoke(
                Command(resume={"approved": approved, "reason": reason}), run_config
            )
            return self._interpret(result_state)
        except Exception as e:
            print(f"[Swarm] Error: {e}")
            return {"status": "error", "success": False, "error": str(e)}

    async def stream_swarm(self, goal: str, thread_id: str = "default"):
        """Async-yield raw LangGraph per-node updates for a fresh run (see
        `stream_mode="updates"` in the LangGraph docs). Each item is either
        `{node_name: node_output}` or `{"__interrupt__": (Interrupt(...),)}`
        when the graph pauses at a gate."""
        run_config = {"configurable": {"thread_id": thread_id}}
        async for update in self.workflow.astream(
            self._initial_state(goal), run_config, stream_mode="updates"
        ):
            yield update

    async def stream_resume(self, thread_id: str, approved: bool, reason: str | None = None):
        """Async-yield raw LangGraph per-node updates while resuming a run
        that's paused at an approval gate. Same item shape as stream_swarm()."""
        run_config = {"configurable": {"thread_id": thread_id}}
        async for update in self.workflow.astream(
            Command(resume={"approved": approved, "reason": reason}),
            run_config,
            stream_mode="updates",
        ):
            yield update

    async def get_final_state(self, thread_id: str) -> dict[str, Any]:
        """Read back the full state values for a thread (used after a stream
        ends without an interrupt, to report the final result)."""
        run_config = {"configurable": {"thread_id": thread_id}}
        state = await self.workflow.aget_state(run_config)
        return state.values


# Singleton orchestrator instance. This matters beyond convenience: the
# LangGraph checkpointer (MemorySaver) that makes gates resumable lives on
# the instance, so a fresh SwarmOrchestrator() per request would silently
# lose all paused runs.
_orchestrator_instance: SwarmOrchestrator | None = None


def get_orchestrator() -> SwarmOrchestrator:
    """Get or create the orchestrator singleton."""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = SwarmOrchestrator()
    return _orchestrator_instance


async def run_swarm_workflow(goal: str, thread_id: str = "default") -> dict[str, Any]:
    """Run a swarm workflow for a given goal, auto-approving both gates.
    For scripted/non-interactive use; the API exposes the real gates directly."""
    orchestrator = get_orchestrator()
    result = await orchestrator.run_swarm(goal, {"thread_id": thread_id})
    while result.get("status") == "awaiting_approval":
        result = await orchestrator.resume_swarm(thread_id, approved=True)
    return result


if __name__ == "__main__":
    result = asyncio.run(run_swarm_workflow("Refactor authentication to use async/await"))
    print(f"\nResult: {result}")
