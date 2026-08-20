# Open Swarm 🐝

**Parallel multi-agent coding swarm - local-first, zero-cost**

Open Swarm is a production-ready design for parallel, heterogeneous multi-agent execution. It keeps the local-first, zero-cost, open-source ethos of OpenMonoAgent while adding true parallel multi-agent swarm execution.

## Overview

Open Swarm enables multiple AI agents to work in parallel on complex coding tasks, with intelligent routing across multiple free/local LLMs. Agents collaborate through a shared blackboard (stigmergy pattern).

### Key Features

- **Local-first + Free-tier hybrid**: Prefer local models; fall back to free cloud tiers
- **Parallel by default**: Agents run concurrently where possible
- **Intelligent router**: Lightweight LLM router decides which models handle each sub-task
- **Sandbox + Permission model**: Docker isolation with human gates
- **Open & composable**: Python core with MCP support and playbook workflows

## Quick Start

```bash
# Clone and install
cd open-swarm
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Pull a small local model
ollama pull qwen2.5-coder:3b

# Run a swarm
openswarm run "Refactor authentication to use async/await"

# Or start the full API + live dashboard
openswarm serve
# → http://localhost:8000/dashboard
```

## Architecture

```
User Goal → Router → Parallel Swarm Launch
  ├─ Scout Agent → explore codebase
  ├─ Planner Agent → create plan
  ├─ Coder Agent(s) → implement
  └─ Critic Agent → verify
    ↓
Shared Blackboard
    ↓
Synthesis → Human Gate → Execute
```

## License

MIT License - Open source, zero-cost, local-first
