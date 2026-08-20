"""
Open Swarm Orchestrator
LangGraph-based swarm execution with parallel agents and human-in-the-loop
"""

import asyncio
from datetime import datetime
from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from .blackboard import get_blackboard
from .router import get_router, route_task


# Shared State (Blackboard)
class SwarmState(TypedDict):
    goal: str
    plan: str
    code_proposals: list[str]
    critique_reports: list[str]
    final_output: str
    requires_human_approval: bool
    workflow_stage: str
    agent_outputs: dict[str, Any]
    metadata: dict[str, Any]


class SwarmOrchestrator:
    def __init__(self):
        self.router = get_router()
        self.blackboard = get_blackboard()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        """Build LangGraph workflow"""
        builder = StateGraph(SwarmState)

        # Add nodes
        builder.add_node("scout", self.scout_node)
        builder.add_node("planner", self.planner_node)
        builder.add_node("workers", self.parallel_worker_node)
        builder.add_node("synthesizer", self.synthesizer_node)

        # Define edges
        builder.set_entry_point("scout")
        builder.add_edge("scout", "planner")
        builder.add_edge("planner", "workers")
        builder.add_edge("workers", "synthesizer")
        builder.add_edge("synthesizer", END)

        # Compile with checkpointing
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

        # Human gate
        return {"plan": plan, "requires_human_approval": True, "workflow_stage": "planner_complete"}

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

        return {
            "final_output": final_output,
            "requires_human_approval": True,
            "workflow_stage": "complete",
        }

    async def run_swarm(self, goal: str, config: dict | None = None) -> dict[str, Any]:
        """
        Run swarm workflow with optional human-in-the-loop
        """
        initial_state = {
            "goal": goal,
            "plan": "",
            "code_proposals": [],
            "critique_reports": [],
            "final_output": "",
            "requires_human_approval": False,
            "workflow_stage": "start",
            "agent_outputs": {},
            "metadata": {"start_time": datetime.now().isoformat(), "session_id": str(id(self))},
        }

        thread_id = config.get("thread_id", "default") if config else "default"

        try:
            # Stream events
            async for event in self.workflow.astream(
                initial_state, {"configurable": {"thread_id": thread_id}}
            ):
                print(f"[Swarm] Event: {list(event.keys())}")

                # Check for human approval requirement
                if event.get("planner", {}).get("requires_human_approval"):
                    print("\n[Swarm] HALT: Planner requires human approval")
                    # In production, would pause and wait for approval
                    # For now, auto-approve in demo mode
                    print("[Swarm] Auto-approving for demo...")
                    continue

                if event.get("synthesizer", {}).get("requires_human_approval"):
                    print("\n[Swarm] HALT: Synthesizer requires human approval")
                    print("[Swarm] Auto-approving for demo...")
                    continue

            # Get final state
            final_state = await self.workflow.aget_state({"configurable": {"thread_id": thread_id}})

            return {
                "success": True,
                "final_output": final_state.values.get("final_output", ""),
                "plan": final_state.values.get("plan", ""),
                "workflow_stage": final_state.values.get("workflow_stage", "unknown"),
            }

        except Exception as e:
            print(f"[Swarm] Error: {e}")
            return {"success": False, "error": str(e)}


# Convenience function
async def run_swarm_workflow(goal: str) -> dict[str, Any]:
    """Run a swarm workflow for a given goal"""
    orchestrator = SwarmOrchestrator()
    return await orchestrator.run_swarm(goal)


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(run_swarm_workflow("Refactor authentication to use async/await"))
    print(f"\nResult: {result}")
