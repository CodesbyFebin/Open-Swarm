# Open Swarm 🐝

**Parallel multi-agent coding swarm — local-first, zero-cost**

[![CI](https://github.com/CodesbyFebin/Open-Swarm/actions/workflows/ci.yml/badge.svg)](https://github.com/CodesbyFebin/Open-Swarm/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](pyproject.toml)
[![Status: Alpha](https://img.shields.io/badge/status-alpha-orange.svg)](ROADMAP.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Open Swarm is a local-first design for parallel, heterogeneous multi-agent coding. It keeps the local-first, zero-cost, open-source ethos of OpenMonoAgent while adding true parallel multi-agent swarm execution.

**Landing page:** [open-swarm.vercel.app](https://open-swarm.vercel.app/) · **Docs:** [Architecture](docs/ARCHITECTURE.md) · [Getting Started](docs/GETTING_STARTED.md) · [Roadmap](ROADMAP.md)

> **Project status:** early alpha. The router, blackboard, and orchestrator are implemented and tested, including real human-in-the-loop approval gates (LangGraph `interrupt()`, not simulated) reachable from both the CLI and the API. The TUI is a placeholder, the Docker execution sandbox is design-only (no code yet), and cloud-provider adapters are not load-tested end-to-end. See [ROADMAP.md](ROADMAP.md) for what's next — contributions welcome.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Three Ways to Use It](#three-ways-to-use-it)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

Open Swarm enables multiple AI agents to work in parallel on complex coding tasks, with intelligent routing across multiple free/local LLMs. Agents collaborate through a shared blackboard (stigmergy pattern) instead of expensive direct messaging.

### Key Features

- **Local-first + free-tier hybrid**: prefer local Ollama models; fall back to free cloud tiers automatically
- **Parallel by default**: agents run concurrently where possible
- **Intelligent router**: lightweight heuristic router decides which models handle each sub-task, with rate-limit-aware fallback chains
- **Real human-in-the-loop**: the swarm genuinely pauses (LangGraph `interrupt()`) before coding and before finalizing, resumable from the CLI or the dashboard — not a canned demo step
- **Sandbox + permission model**: `config/permissions.yaml` policy plus a Docker service stack today; per-command Docker execution against that policy is still on the [roadmap](ROADMAP.md)
- **Open & composable**: Python core with playbook workflows and MCP support on the roadmap

## Quick Start

```bash
# Clone and install
git clone https://github.com/CodesbyFebin/Open-Swarm.git
cd Open-Swarm
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

For a step-by-step walkthrough, see [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md).

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

Full design notes, swarm patterns, and data flow live in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Three Ways to Use It

| Interface | Command | Notes |
|---|---|---|
| ⚡ CLI | `openswarm run "your goal"` | Prompts for approval at each gate; pass `-y`/`--yes` for scripted, CI-friendly runs |
| 📱 Dashboard | `openswarm serve` → `http://localhost:8000/dashboard` | Mobile-first chat UI with a live agent timeline, streamed over SSE |
| 🖥️ TUI | `openswarm tui` | Placeholder today — multi-panel view is on the [roadmap](ROADMAP.md) |

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — design principles, core components, swarm patterns
- [Getting Started](docs/GETTING_STARTED.md) — installation and first run
- [Good First Issues](docs/GOOD_FIRST_ISSUES.md) — curated starter tasks
- [Contributing Quick Start](docs/CONTRIBUTING_QUICKSTART.md) — condensed contributor guide
- [Roadmap](ROADMAP.md) — what's shipped, in progress, and planned
- [Security Policy](SECURITY.md) — supported versions and how to report a vulnerability

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for setup, style, and PR process, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community guidelines. Good first issues are labeled [`good first issue`](https://github.com/CodesbyFebin/Open-Swarm/labels/good%20first%20issue) on GitHub.

## License

MIT License — open source, zero-cost, local-first. See [LICENSE](LICENSE).
