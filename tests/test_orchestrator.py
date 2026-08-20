"""
Tests for the real human-in-the-loop approval gates in the orchestrator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from openswarm.core.orchestrator import SwarmOrchestrator


@pytest.mark.asyncio
async def test_run_pauses_at_plan_gate():
    orchestrator = SwarmOrchestrator()
    result = await orchestrator.run_swarm("Refactor auth", {"thread_id": "test-plan-pause"})

    assert result["status"] == "awaiting_approval"
    assert result["gate"] == "plan"
    assert "plan" in result["payload"]


@pytest.mark.asyncio
async def test_rejecting_plan_gate_aborts_without_running_workers():
    orchestrator = SwarmOrchestrator()
    await orchestrator.run_swarm("Refactor auth", {"thread_id": "test-plan-reject"})

    result = await orchestrator.resume_swarm("test-plan-reject", approved=False, reason="not now")

    assert result["status"] == "aborted"
    assert result["success"] is False
    assert result["error"] == "not now"

    final_state = await orchestrator.get_final_state("test-plan-reject")
    assert final_state["code_proposals"] == []
    assert final_state["critique_reports"] == []


@pytest.mark.asyncio
async def test_full_run_through_both_gates_completes():
    orchestrator = SwarmOrchestrator()
    result = await orchestrator.run_swarm("Refactor auth", {"thread_id": "test-full-run"})
    assert result["status"] == "awaiting_approval"
    assert result["gate"] == "plan"

    result = await orchestrator.resume_swarm("test-full-run", approved=True)
    assert result["status"] == "awaiting_approval"
    assert result["gate"] == "final"
    assert "final_output" in result["payload"]

    result = await orchestrator.resume_swarm("test-full-run", approved=True)
    assert result["status"] == "completed"
    assert result["success"] is True
    assert result["final_output"]


@pytest.mark.asyncio
async def test_rejecting_final_gate_aborts_after_work_is_done():
    orchestrator = SwarmOrchestrator()
    await orchestrator.run_swarm("Refactor auth", {"thread_id": "test-final-reject"})
    await orchestrator.resume_swarm("test-final-reject", approved=True)

    result = await orchestrator.resume_swarm(
        "test-final-reject", approved=False, reason="needs more critique"
    )

    assert result["status"] == "aborted"
    assert result["error"] == "needs more critique"

    final_state = await orchestrator.get_final_state("test-final-reject")
    assert final_state["code_proposals"], "workers should have already run before this gate"


@pytest.mark.asyncio
async def test_stream_swarm_emits_scout_and_planner_before_interrupting():
    orchestrator = SwarmOrchestrator()
    seen_nodes = []

    async for update in orchestrator.stream_swarm("Refactor auth", "test-stream"):
        if "__interrupt__" in update:
            break
        seen_nodes.extend(update.keys())

    assert seen_nodes == ["scout", "planner"]
