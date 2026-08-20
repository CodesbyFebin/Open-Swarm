# Open Swarm Roadmap

## 🎯 Vision

**AI shouldn't have a meter. Unlimited tokens. Forever. Your machine. Your agent.**

Open Swarm makes parallel multi-agent coding accessible, private, and zero-cost.

## ✅ Completed

- [x] Core router with local-first routing
- [x] Blackboard stigmergy memory
- [x] LangGraph orchestrator with parallel workers
- [x] **Real LangGraph interrupts** for human gates (plan + final approval,
      resumable via CLI prompt or `/v1/stream` + `/v1/approve`)
- [x] FastAPI SSE server with a mobile-first dashboard
- [x] CLI interface (including a real interactive approval flow)
- [x] Docker service stack (Ollama + LiteLLM)
- [x] Playbook system
- [x] Configuration system

## 🚧 In Progress (v0.2)

- [ ] **Docker execution sandbox** — `config/permissions.yaml` declares the
      policy, but no code yet actually runs agent commands in a container
      against it (see ARCHITECTURE.md)
- [ ] **Parallel scout + planner** nodes
- [ ] **Full Textual TUI** with multi-panel view
- [ ] **Playbook validation** schema
- [ ] **MCP tool support** integration
- [ ] **Agent state persistence** across process restarts (currently
      in-memory per orchestrator process, via LangGraph's `MemorySaver`)

## 📋 Next (v0.3)

- [ ] **Consensus voting** patterns
- [ ] **Debate loops** between proposer and critic
- [ ] **Code intelligence** integration (LSP, AST)
- [ ] **Vision support** for UI/code screenshots
- [ ] **VS Code extension** with SSE client
- [ ] **Mobile companion** app

## 🔮 Later (v0.4+)

- [ ] **Hierarchical swarms** (Leader → Workers → Verifiers)
- [ ] **Graphify integration** for semantic code graphs
- [ ] **Dual-box mode** (local + remote inference)
- [ ] **Plugin marketplace** for custom agents
- [ ] **Performance profiling** and optimization
- [ ] **Enterprise features** (SSO, audit logs, team workspaces)

## 💡 Community Requests

Vote on features via GitHub Discussions:
- [ ] Web UI improvements
- [ ] More playbook examples
- [ ] Documentation translations
- [ ] Video tutorials

## Contributing to Roadmap

Want a feature? Open a discussion or issue with the `enhancement` label. We prioritize based on community impact and alignment with the local-first, zero-cost mission.

---

*Last updated: 2026-08-20*
