"""
Open Swarm FastAPI Server
SSE streaming API with live dashboard and real human-in-the-loop approval gates
"""

import json
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from ..core.blackboard import get_blackboard
from ..core.orchestrator import get_orchestrator
from ..core.router import get_router

app = FastAPI(
    title="Open Swarm API", description="Parallel multi-agent coding swarm API", version="0.1.0"
)

DASHBOARD_HTML_PATH = Path(__file__).resolve().parent.parent / "ui" / "dashboard.html"

# Nodes that represent visible run stages in the client timeline. The two
# approval gates (plan_gate, final_gate) are deliberately excluded here: they
# surface as their own "awaiting_approval" event instead of a stage update.
STAGE_MESSAGES = {
    "scout": "Exploring codebase",
    "planner": "Creating plan",
    "workers": "Running coder and critic",
    "synthesizer": "Synthesizing results",
}


class RunRequest(BaseModel):
    goal: str | None = None
    playbook: str | None = None
    thread_id: str | None = "default"
    resume: dict | None = None


class ApprovalRequest(BaseModel):
    thread_id: str
    approve: bool
    reason: str | None = None


def _now() -> str:
    return datetime.now().isoformat()


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


@app.get("/")
async def root():
    return {
        "name": "Open Swarm",
        "version": "0.1.0",
        "status": "running",
        "endpoints": ["/v1/run", "/v1/stream", "/v1/status", "/v1/approve", "/dashboard"],
    }


@app.post("/v1/run")
async def run_swarm(request: RunRequest):
    """Run a swarm workflow synchronously up to its first approval gate (or
    completion, if there is nothing to approve)."""
    orchestrator = get_orchestrator()

    if request.resume is not None:
        result = await orchestrator.resume_swarm(
            request.thread_id or "default",
            approved=bool(request.resume.get("approved")),
            reason=request.resume.get("reason"),
        )
    else:
        if not request.goal:
            raise HTTPException(status_code=400, detail="goal is required to start a run")
        result = await orchestrator.run_swarm(request.goal, {"thread_id": request.thread_id})

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return {"thread_id": request.thread_id, **result}


@app.post("/v1/stream")
async def stream_swarm(request: RunRequest) -> StreamingResponse:
    """Stream swarm execution via Server-Sent Events.

    A fresh run is started when `goal` is set; passing `resume` instead
    continues a run that's paused at an approval gate, on the same
    `thread_id`. Either way, real per-node LangGraph updates are streamed
    as they happen — nothing here is simulated or pre-scripted.
    """
    thread_id = request.thread_id or "default"

    async def event_generator() -> AsyncGenerator[str, None]:
        orchestrator = get_orchestrator()
        try:
            yield _sse({"type": "connected", "thread_id": thread_id})

            if request.resume is not None:
                node_stream = orchestrator.stream_resume(
                    thread_id,
                    approved=bool(request.resume.get("approved")),
                    reason=request.resume.get("reason"),
                )
            else:
                if not request.goal:
                    yield _sse({"type": "error", "error": "goal is required to start a run"})
                    return
                yield _sse({"type": "started", "goal": request.goal, "timestamp": _now()})
                node_stream = orchestrator.stream_swarm(request.goal, thread_id)

            async for update in node_stream:
                if "__interrupt__" in update:
                    payload = update["__interrupt__"][0].value
                    yield _sse(
                        {
                            "type": "awaiting_approval",
                            "gate": payload.get("gate"),
                            "message": payload.get("message"),
                            "payload": payload,
                            "timestamp": _now(),
                        }
                    )
                    return

                for node_name in update:
                    if node_name not in STAGE_MESSAGES:
                        continue
                    yield _sse(
                        {
                            "type": "stage",
                            "stage": node_name,
                            "message": STAGE_MESSAGES[node_name],
                            "timestamp": _now(),
                        }
                    )

            # Stream ended without an interrupt: the run finished (or was
            # rejected at a gate, which also routes straight to END).
            final_values = await orchestrator.get_final_state(thread_id)
            if final_values.get("aborted"):
                yield _sse(
                    {
                        "type": "aborted",
                        "reason": final_values.get("abort_reason") or "Run aborted",
                        "timestamp": _now(),
                    }
                )
            else:
                yield _sse(
                    {
                        "type": "completed",
                        "result": {
                            "success": True,
                            "final_output": final_values.get("final_output", ""),
                        },
                        "timestamp": _now(),
                    }
                )

        except Exception as e:
            yield _sse({"type": "error", "error": str(e)})

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/v1/status/{thread_id}")
async def get_status(thread_id: str):
    """Get status of a running workflow"""
    bb = get_blackboard()
    summary = bb.get_state_summary()

    return {
        "thread_id": thread_id,
        "blackboard_summary": summary,
        "timestamp": _now(),
    }


@app.post("/v1/approve")
async def approve_workflow(request: ApprovalRequest):
    """Resume a workflow paused at a human approval gate (non-streaming)."""
    orchestrator = get_orchestrator()
    result = await orchestrator.resume_swarm(
        request.thread_id, approved=request.approve, reason=request.reason
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("error"))

    return {"thread_id": request.thread_id, **result}


@app.get("/v1/models")
async def list_models():
    """List available models"""
    router = get_router()
    stats = router.get_model_stats()

    models_data = []
    for model in router.models:
        models_data.append(
            {
                "name": model.name,
                "provider": model.provider,
                "purpose": model.purpose,
                "is_local": model.is_local,
                "free_tier": model.free_tier,
                "max_tokens": model.max_tokens,
            }
        )

    return {"stats": stats, "models": models_data}


@app.get("/dashboard")
async def dashboard():
    """Serve the mobile-app-style Open Swarm dashboard"""
    return HTMLResponse(content=DASHBOARD_HTML_PATH.read_text())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
