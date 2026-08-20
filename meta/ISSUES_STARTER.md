# Starter Issues for Open Swarm

These are good first issues for new contributors!

## 🐛 Bugs

### [good first issue] Improve error messages for model loading failures
**Description**: When a model fails to load, the error message is generic. Improve it to show which model, why it failed, and suggested fixes.

**Files**: `src/openswarm/core/router.py`
**Labels**: bug, good first issue

### [good first issue] Fix TUI panel resizing on terminal resize
**Description**: Textual TUI panels don't properly resize when terminal window changes size.

**Files**: `src/openswarm/ui/tui.py`
**Labels**: bug, good first issue, ui

## ✨ Features

### [good first issue] Add parallel scout + planner execution
**Description**: Currently scout runs sequentially before planner. Make them run in parallel when scout findings are sufficient.

**Files**: `src/openswarm/core/orchestrator.py`
**Labels**: enhancement, good first issue

### [good first issue] Create security audit playbook
**Description**: Add a new playbook for security auditing that focuses on vulnerability detection.

**Files**: `config/playbooks/security_audit.yaml`
**Labels**: enhancement, playbook, good first issue

### [good first issue] Add model health check endpoint
**Description**: Add `/v1/models/health` endpoint that checks if models are responsive.

**Files**: `src/openswarm/api/main.py`, `src/openswarm/core/router.py`
**Labels**: enhancement, api, good first issue

## 📚 Documentation

### [good first issue] Add more playbook examples
**Description**: Create 2-3 more example playbooks: `feature_implement.yaml`, `test_generation.yaml`, `docs_update.yaml`.

**Files**: `config/playbooks/`
**Labels**: documentation, good first issue

### [good first issue] Improve README with architecture diagram
**Description**: Add a Mermaid diagram showing the swarm flow.

**Files**: `README.md`
**Labels**: documentation, good first issue

## 🧪 Testing

### [good first issue] Add unit tests for Blackboard
**Description**: The blackboard has no tests. Add tests for write/read operations.

**Files**: `tests/test_blackboard.py`
**Labels**: testing, good first issue

### [good first issue] Test router fallback logic
**Description**: Add tests for model fallback when rate limited.

**Files**: `tests/test_router.py`
**Labels**: testing, good first issue

## 🔧 Improvements

### [good first issue] Add progress bar to CLI
**Description**: Show progress during swarm execution in CLI mode.

**Files**: `src/openswarm/cli.py`
**Labels**: enhancement, cli, good first issue

---

Pick an issue, comment on it, and start contributing! Questions welcome in GitHub Discussions.
