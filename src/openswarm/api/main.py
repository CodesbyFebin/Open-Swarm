"""
Open Swarm FastAPI Server
SSE streaming API with live dashboard
"""

import asyncio
import json
from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..core.blackboard import get_blackboard
from ..core.orchestrator import SwarmOrchestrator
from ..core.router import get_router

app = FastAPI(
    title="Open Swarm API", description="Parallel multi-agent coding swarm API", version="0.1.0"
)


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
    """Serve dashboard HTML"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Open Swarm Dashboard</title>
    <style>
        body { font-family: monospace; margin: 20px; background: #1e1e1e; color: #fff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { font-size: 24px; margin-bottom: 20px; }
        .panel { background: #2d2d2d; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .log { background: #000; padding: 10px; height: 300px; overflow-y: scroll; font-size: 12px }
        input, button { padding: 8px; margin: 5px; }
        button { background: #007acc; color: white; border: none; cursor: pointer; }
        button:hover { background: #005a9e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">🐝 Open Swarm Dashboard</div>

        <div class="panel">
            <h3>Run Swarm</h3>
            <input type="text" id="goal" placeholder="Enter your goal..." style="width: 70%">
            <button onclick="runSwarm()">Run</button>
        </div>

        <div class="panel">
            <h3>Live Stream</h3>
            <div class="log" id="log"></div>
        </div>

        <div class="panel">
            <h3>Models</h3>
            <button onclick="loadModels()">Load Models</button>
            <div id="models"></div>
        </div>
    </div>

    <script>
        const log = document.getElementById('log');

        function logMessage(msg) {
            log.innerHTML += msg + '<br>';
            log.scrollTop = log.scrollHeight;
        }

        async function runSwarm() {
            const goal = document.getElementById('goal').value;
            if (!goal) return;

            log.innerHTML = '';
            logMessage('Starting swarm: ' + goal);

            const response = await fetch('/v1/stream', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({goal: goal})
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const {done, value} = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));
                        logMessage(JSON.stringify(data, null, 2));
                    }
                }
            }
        }

        async function loadModels() {
            const response = await fetch('/v1/models');
            const data = await response.json();
            document.getElementById('models').innerHTML =
                '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
        }
    </script>
</body>
</html>
    """
    from fastapi.responses import HTMLResponse

    return HTMLResponse(content=html)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
