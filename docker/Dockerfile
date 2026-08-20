# Open Swarm Agent Dockerfile
# Ephemeral execution environment for swarm agents

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy application
COPY src /app/src
COPY config /app/config
COPY pyproject.toml /app/

# Install dependencies
RUN pip install --no-cache-dir /app

# Create workspace directory
RUN mkdir -p /workspace && chmod 777 /workspace

# Default command
CMD ["python", "-m", "openswarm.cli", "--help"]
