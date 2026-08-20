# Show HN: Open Swarm — local-first parallel multi-agent coding, zero cost

Most coding agents meter your tokens and send your code to the cloud. Open Swarm runs specialist agents in parallel on your machine.

**What it is:**
- Parallel multi-agent system: Scout → Planner → Coder → Critic → Synthesizer
- Local-first routing: prefers Ollama models, falls back to free cloud tiers automatically
- Stigmergy blackboard: agents collaborate via shared memory, no direct messaging
- LangGraph orchestration with human-in-the-loop gates
- Three interfaces: CLI, Textual TUI, FastAPI dashboard

**Why build it?**
OpenMonoAgent proved mono-agent local coding works. Open Swarm asks: what if we run multiple agents in parallel, route across models intelligently, and keep everything private?

**Try it:**
```bash
git clone https://github.com/CodesbyFebin/Open-Swarm.git
cd Open-Swarm
pip install -e .
ollama pull qwen2.5-coder:3b
openswarm run "Refactor auth to async/await"
```

Or `openswarm tui` for a multi-panel terminal UI.

**Repo:** https://github.com/CodesbyFebin/Open-Swarm

**Philosophy:** AI shouldn't have a meter. Unlimited tokens. Forever. Your machine. Your agent.

Would love feedback on the router design and stigmergy pattern!
