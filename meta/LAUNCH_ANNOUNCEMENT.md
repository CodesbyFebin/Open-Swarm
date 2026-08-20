# Launch Announcement — Open Swarm

## Open Swarm — local-first parallel multi-agent coding, zero cost after setup

Most coding agents meter your tokens and send your code to the cloud.

Open Swarm runs specialist agents (Scout → Planner → Coder → Critic → Synthesizer) in parallel on your machine, routes across local models + free tiers, and keeps everything sandboxed.

### What it does

- **Local-first** (Ollama / llama.cpp) — runs on your machine
- **Free-tier fallback** — automatic when you want speed
- **Parallel agents** — Scout, Planner, Coder, Critic work concurrently
- **Declarative playbooks** — YAML workflows for reusable patterns
- **Three interfaces** — CLI, multi-panel TUI, live dashboard
- **MIT licensed** — no telemetry, no lock-in

### Quick start

```bash
git clone https://github.com/CodesbyFebin/Open-Swarm.git
cd Open-Swarm
python -m venv .venv && source .venv/bin/activate
pip install -e .
ollama pull qwen2.5-coder:3b

# Run it
openswarm run "Refactor auth to async/await"
# or
openswarm tui
# or
openswarm serve  # dashboard at http://localhost:8000
```

### Repo

https://github.com/CodesbyFebin/Open-Swarm

### Philosophy

AI shouldn't have a meter. Unlimited tokens. Forever. Your machine. Your agent.

Own your swarm.

---

**Tags:** #AI #MultiAgent #LocalFirst #OpenSource #Coding #LangGraph #LLM
