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
LangGraph-based workflow with parallel nodes and human-in-the-loop.

**Pattern:** Scout → Planner → [Coder + Critic] → Synthesizer

### 4. Sandbox (src/sandbox/docker_manager.py)
Docker isolation with permission gates.

**Features:**
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
