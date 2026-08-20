# Contributing to Open Swarm

Thank you for your interest in contributing! Open Swarm is built by the community, for the community.

## Code of Conduct

By participating, you agree to abide by our Code of Conduct. Please read it before contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/open-swarm.git`
3. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`
4. Install in dev mode: `pip install -e ".[dev]"`
5. Create a branch: `git checkout -b feature/your-feature-name`

## Making Changes

### Code Style
- Follow PEP 8
- Use Black for formatting (line length 100)
- Use Ruff for linting
- Write tests for new features

### Commit Messages
Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for refactoring

## Playbooks

Open Swarm extends through playbooks. To add a playbook:
1. Create a YAML file in `config/playbooks/`
2. Follow the existing playbook schema
3. Test it with `openswarm run --playbook your-playbook.yaml`
4. Document it in `docs/playbooks/`

## Pull Request Process

1. Update documentation as needed
2. Add tests for new functionality
3. Ensure tests pass: `pytest tests/`
4. Format code: `black src/ && ruff check src/`
5. Submit PR with clear description

## Good First Issues

Look for issues labeled `good first issue` or `playbook`. These are great starting points!

## Questions?

Open a discussion or issue. We're here to help!
