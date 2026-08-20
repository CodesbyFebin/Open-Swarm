# Good First Issues for Open Swarm

Create these as GitHub issues labeled `good first issue` + `help wanted`

---

## Issue 1 — Add a second playbook

**Title:** `[Playbook] Add security_audit.yaml`

**Labels:** `good first issue`, `playbook`

**Description:**
Create `config/playbooks/security_audit.yaml` following the pattern of `coding_refactor.yaml`.

Suggested workflow:
- Scout → Security Analyst → Critic → Synthesizer
- Focus on finding common issues (secrets, auth gaps, injection risks)
- Produce a clear report
- Include at least one human gate before any suggested fixes are applied

**Acceptance Criteria:**
- Playbook file created and validates as YAML
- Follows same schema as coding_refactor.yaml
- Documented in README with example usage

---

## Issue 2 — Parallel scout + planner

**Title:** `[Orchestrator] Run Scout and Planner in parallel`

**Labels:** `good first issue`, `enhancement`

**Description:**
In `src/openswarm/core/orchestrator.py`, make the Scout and Planner nodes run concurrently instead of strictly sequential.

**Acceptance Criteria:**
- Scout and Planner can run in parallel using LangGraph parallel edges or `asyncio.gather`
- Rest of the graph remains the same (Coder + Critic still parallel after Planner)
- Tests pass with parallel execution
- Performance improvement documented

---

## Issue 3 — Better error messages when Ollama is down

**Title:** `[DX] Friendly error when local models are unavailable`

**Labels:** `good first issue`, `documentation`

**Description:**
When the router or orchestrator can't reach Ollama / configured local model, show a clear message with exact fix instead of raw exception.

**Acceptance Criteria:**
- User sees friendly error: "Ollama not running. Run: ollama serve"
- Error shows which model is missing
- Error suggests: `ollama pull <model-name>`
- Error links to docs/GETTING_STARTED.md

---

## Issue 4 — TUI: show which model each agent is using

**Title:** `[TUI] Display active model name in each agent panel`

**Labels:** `good first issue`, `ui`

**Description:**
In the Textual TUI, show the model currently assigned to Scout / Planner / Coder / Critic.

**Acceptance Criteria:**
- Model name visible in each agent panel (title or badge)
- Updates when router switches models
- Doesn't break existing TUI layout

---

## Issue 5 — Add unit tests for Blackboard

**Title:** `[Tests] Unit tests for Blackboard write/read/snapshot`

**Labels:** `good first issue`, `tests`

**Description:**
Add tests in `tests/test_blackboard.py` covering basic blackboard operations.

**Acceptance Criteria:**
- Tests for `write` operation
- Tests for `read` operation
- Tests for `read_latest` operation
- Tests for `snapshot` operation
- Tests for basic persistence
- All tests pass with `pytest tests/test_blackboard.py`
