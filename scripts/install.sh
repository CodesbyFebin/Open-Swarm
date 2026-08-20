#!/bin/bash
# Open Swarm Installation Script

set -e

echo "🐝 Installing Open Swarm..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3.10+ required"
    exit 1
fi

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package
pip install -e .

# Create directories
mkdir -p data logs workspace

echo "✓ Open Swarm installed successfully"
echo ""
echo "Next steps:"
echo "1. ollama pull qwen2.5-coder:3b"
echo "2. openswarm run 'Your goal here'"
echo ""
echo "Or start the API server:"
echo "openswarm serve"
