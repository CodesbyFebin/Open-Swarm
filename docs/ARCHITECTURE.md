# Open Swarm Architecture

## Design Principles

1. **Local-first + Free-tier hybrid**: Prefer fully local models; fall back to free cloud tiers
2. **Parallel by default**: Agents run concurrently where possible
3. **Router as first-class citizen**: Lightweight LLM router decides models per sub-task
4. **Sandbox + Permission model**: Inherit Docker isolation from OpenMono
5. **Open & composable**: Python core, MCP support, playbook workflows

## Core Components

### 1. Router (src/core/router.py)
Intelligent local-first routing with automatic fallback and rate limit awareness.

**Features:**
- Semantic + heuristic task classification
- Local-first prioritization
- Rate limit cooldown tracking
- Automatic fallback chains

### 2. Blackboard (src/core/blackboard.py)
Shared stigmergy memory using JSONL persistence.

**Features:**
- Agents write/read to shared memory
- No direct messaging (reduces token waste)
- Persistent across sessions
- Agent-specific filtering

### 3. Orchestrator (src/core/orchestrator.py)
LangGraph-based workflow with parallel nodes and real human-in-the-loop gates.

**Pattern:** Scout → Planner → **[plan gate]** → [Coder + Critic] → Synthesizer → **[final gate]**

The two gates are genuine LangGraph `interrupt()` pauses, not simulated ones:
the graph's execution actually stops at `plan_gate`/`final_gate` and a
`Command(resume={"approved": bool, "reason": str | None})` is required to
continue. A `MemorySaver` checkpointer on the orchestrator singleton
(`get_orchestrator()`) keeps a paused run resumable across separate API
requests, keyed by `thread_id`. Both the CLI (`openswarm run`, interactively
by default) and the API (`/v1/stream`, `/v1/approve`) drive the same gates.

### 4. Sandbox (planned)
`config/permissions.yaml` already declares the intended read-only vs
writable path policy, and `docker/` provides the service stack (Ollama +
LiteLLM + API), but there is **no code yet** that actually executes agent
commands inside a Docker container per that policy — the coder/critic
nodes today produce simulated output rather than shelling out. Tracked in
[ROADMAP.md](../ROADMAP.md).

**Planned features:**
- Read-only mounts for Scout/Critic
- Read-write after human approval
- Resource limits and timeouts

## Agent Roles

- **Scout**: Read-only exploration, fast models
- **Planner**: Task decomposition, reasoning models
- **Coder**: Implementation, coding-specialized models
- **Critic**: Adversarial review, critique models
- **Synthesizer**: Merge results, reasoning models

## Swarm Patterns

1. **Boss-Worker**: Leader decomposes → parallel workers → aggregation
2. **Consensus/Voting**: Multiple agents propose → majority vote
3. **Debate**: Proposer + Critic loop for higher quality
4. **Stigmergy**: Agents leave traces in shared environment

## Data Flow

1. User goal → Router assessment
2. Router selects models + agents
3. Agents read from/write to Blackboard
4. Workflow progresses through LangGraph
5. Human gates for destructive operations
6. Final synthesis with approval
