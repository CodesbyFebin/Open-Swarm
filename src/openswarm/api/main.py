"""
Open Swarm FastAPI Server
SSE streaming API with live dashboard
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from ..core.blackboard import get_blackboard
from ..core.orchestrator import SwarmOrchestrator
from ..core.router import get_router

app = FastAPI(
    title="Open Swarm API", description="Parallel multi-agent coding swarm API", version="0.1.0"
)

DASHBOARD_HTML_PATH = Path(__file__).resolve().parent.parent / "ui" / "dashboard.html"


class RunRequest(BaseModel):
    goal: str
    playbook: str | None = None
    thread_id: str | None = "default"


class ApprovalRequest(BaseModel):
    thread_id: str
    approve: bool
    reason: str | None = None


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
    """Run a swarm workflow synchronously"""
    orchestrator = SwarmOrchestrator()
    result = await orchestrator.run_swarm(request.goal, {"thread_id": request.thread_id})

    if result.get("success"):
        return {"status": "completed", "thread_id": request.thread_id, "result": result}
    else:
        raise HTTPException(status_code=500, detail=result.get("error"))


@app.post("/v1/stream")
async def stream_swarm(request: RunRequest) -> StreamingResponse:
    """Stream swarm execution via Server-Sent Events"""

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Initial connection event
            connected = {"type": "connected", "thread_id": request.thread_id}
            yield f"data: {json.dumps(connected)}\n\n"

            # Simulate streaming events
            started = {
                "type": "started",
                "goal": request.goal,
                "timestamp": datetime.now().isoformat(),
            }
            yield f"data: {json.dumps(started)}\n\n"

            # Stream workflow progress
            orchestrator = SwarmOrchestrator()

            # For demo, simulate progress
            stages = [
                ("scout", "Exploring codebase"),
                ("planner", "Creating plan"),
                ("workers", "Running coder and critic"),
                ("synthesizer", "Synthesizing results"),
            ]

            for stage, message in stages:
                stage_event = {
                    "type": "stage",
                    "stage": stage,
                    "message": message,
                    "timestamp": datetime.now().isoformat(),
                }
                yield f"data: {json.dumps(stage_event)}\n\n"
                await asyncio.sleep(0.5)

            # Final result
            result = await orchestrator.run_swarm(request.goal, {"thread_id": request.thread_id})

            completed = {
                "type": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
            yield f"data: {json.dumps(completed)}\n\n"

        except Exception as e:
            error_event = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/v1/status/{thread_id}")
async def get_status(thread_id: str):
    """Get status of a running workflow"""
    bb = get_blackboard()
    summary = bb.get_state_summary()

    return {
        "thread_id": thread_id,
        "blackboard_summary": summary,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/v1/approve")
async def approve_workflow(request: ApprovalRequest):
    """Approve a workflow that requires human intervention"""
    # In production, would resume LangGraph execution
    return {
        "status": "approved" if request.approve else "rejected",
        "thread_id": request.thread_id,
        "reason": request.reason,
        "timestamp": datetime.now().isoformat(),
    }


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
