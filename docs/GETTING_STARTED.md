# Getting Started with Open Swarm

Welcome! This guide will get you running in under 5 minutes.

## Prerequisites

- Python 3.10+
- Docker (for sandboxing)
- Ollama (for local models)

## Quick Install

```bash
# Clone the repository
git clone https://github.com/YOUR_ORG/open-swarm.git
cd open-swarm

# Install
./scripts/install.sh

# Or manually:
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Setup Local Models

```bash
# Minimum setup - fast scout model
ollama pull qwen2.5-coder:3b

# Recommended setup - full stack
ollama pull qwen2.5-coder:3b
ollama pull qwen3:8b
ollama pull qwen2.5-coder:14b

# Or start Docker stack
docker-compose -f docker/docker-compose.yml up -d
```

## First Run

```bash
# Command line
openswarm run "Refactor authentication to use async/await"

# Terminal UI
openswarm tui "Add rate limiting to API endpoints"

# Web dashboard
openswarm serve
# Open http://localhost:8000/dashboard
```

## Understanding the Output

Open Swarm uses a 5-stage workflow:

1. **Scout** - Explores codebase (read-only, fast model)
2. **Planner** - Creates refactoring plan (reasoning model)
3. **Coder** - Implements changes (coding model)
4. **Critic** - Adversarial review (critique model)
5. **Synthesizer** - Merges with feedback (reasoning model)

Each stage writes to a shared blackboard, enabling agents to collaborate without direct messaging.

## Configuration

Edit `config/models.yaml` to add your own models:

```yaml
models:
  - name: ollama/your-model
    provider: ollama
    purpose: coding
    is_local: true
```

Edit `config/permissions.yaml` to adjust sandbox rules.

## Playbooks

Use playbooks for reusable workflows:

```bash
openswarm run "Fix the auth bug" --playbook config/playbooks/coding_refactor.yaml
```

Create your own playbooks by copying the example and modifying the workflow.

## Troubleshooting

**Models not loading?**
- Check Ollama is running: `ollama list`
- Verify model names in config

**Permission denied?**
- Check `config/permissions.yaml`
- Ensure workspace is writable

**API not responding?**
- Check Docker containers: `docker ps`
- Verify ports 8000, 11434, 4000 are free

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for deep dive
- Check [ROADMAP.md](../ROADMAP.md) for upcoming features
- Browse [playbooks](../config/playbooks/) for examples
- Join discussions on GitHub

Happy swarming! 🐝
