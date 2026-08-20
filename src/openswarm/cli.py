"""
Open Swarm CLI
Command-line interface for swarm operations
"""

import asyncio
import sys
from pathlib import Path

import click

from .core.blackboard import get_blackboard
from .core.orchestrator import get_orchestrator, run_swarm_workflow
from .core.router import get_router


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Open Swarm - Parallel multi-agent coding swarm"""
    pass


def _run_interactive(goal: str, thread_id: str) -> dict:
    """Drive a swarm run, prompting on the CLI at each real approval gate."""

    async def _drive():
        orchestrator = get_orchestrator()
        result = await orchestrator.run_swarm(goal, {"thread_id": thread_id})
        while result.get("status") == "awaiting_approval":
            gate = result.get("gate")
            detail_key = "plan" if gate == "plan" else "final_output"
            detail = result.get("payload", {}).get(detail_key, "")

            click.echo(f"\n--- Approval needed: {gate} ---")
            click.echo(detail)
            click.echo("-" * 60)
            approved = click.confirm(result.get("message") or "Approve?", default=True)
            result = await orchestrator.resume_swarm(thread_id, approved=approved)
        return result

    return asyncio.run(_drive())


@cli.command()
@click.argument("goal")
@click.option("--thread-id", default="default", help="Thread ID for stateful execution")
@click.option("--playbook", default=None, help="Playbook to use")
@click.option("--yes", "-y", is_flag=True, help="Auto-approve every gate instead of prompting")
def run(goal, thread_id, playbook, yes):
    """Run a swarm workflow with the given goal"""
    click.echo(f"[Open Swarm] Running: {goal}")

    if playbook:
        click.echo(f"[Open Swarm] Using playbook: {playbook}")

    try:
        if yes:
            result = asyncio.run(run_swarm_workflow(goal, thread_id))
        else:
            result = _run_interactive(goal, thread_id)

        status = result.get("status")
        if status == "completed":
            click.echo("\n✓ Swarm completed successfully")
            click.echo("\nFinal Output:")
            click.echo("=" * 60)
            click.echo(result.get("final_output", ""))
            click.echo("=" * 60)
        elif status == "aborted":
            click.echo(f"\n✗ Swarm aborted: {result.get('error')}")
            sys.exit(1)
        else:
            click.echo(f"\n✗ Swarm failed: {result.get('error')}")
            sys.exit(1)

    except Exception as e:
        click.echo(f"\n✗ Error: {e}")
        sys.exit(1)


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def serve(host, port):
    """Start Open Swarm API server"""
    click.echo(f"[Open Swarm] Starting API server on {host}:{port}")
    click.echo("Dashboard available at http://localhost:8000/dashboard")

    import uvicorn

    from .api.main import app

    uvicorn.run(app, host=host, port=port)


@cli.command()
def models():
    """List available models and their status"""
    router = get_router()
    stats = router.get_model_stats()

    click.echo("\nOpen Swarm Model Pool")
    click.echo("=" * 60)
    click.echo(f"Total models: {stats['total']}")
    click.echo(f"Local models: {stats['local']}")
    click.echo(f"Free cloud models: {stats['cloud_free']}")

    click.echo("\nBy Purpose:")
    for purpose, count in stats["by_purpose"].items():
        click.echo(f"  {purpose}: {count} models")

    click.echo("\nAvailable Models:")
    click.echo("-" * 60)
    for model in router.models:
        status = "✓" if model.is_local else "☁"
        click.echo(f"{status} {model.name:40s} ({model.purpose}, {model.provider})")


@cli.command()
def tui():
    """Start Textual TUI interface"""
    click.echo("[Open Swarm] TUI interface starting...")
    click.echo("Note: TUI is a placeholder, use 'openswarm serve' for web dashboard")


@cli.command()
def status():
    """Show current swarm status and blackboard state"""
    bb = get_blackboard()
    summary = bb.get_state_summary()

    click.echo("\nOpen Swarm Status")
    click.echo("=" * 60)
    click.echo(f"Session ID: {summary['session_id']}")
    click.echo(f"Total keys: {summary['total_keys']}")
    click.echo(f"Total entries: {summary['total_entries']}")

    if summary["keys"]:
        click.echo("\nBlackboard Contents:")
        for key, info in summary["keys"].items():
            click.echo(f"  {key}: {info['count']} entries")
            click.echo(f"    Agents: {', '.join(info['agents'])}")
            click.echo(f"    Latest: {info['latest_agent']} at {info['latest_timestamp']}")


@cli.command()
@click.argument("path")
def logs(path):
    """View logs for a specific workflow"""
    log_path = Path(path)
    if log_path.exists():
        click.echo(log_path.read_text())
    else:
        click.echo(f"Log file not found: {path}")


if __name__ == "__main__":
    cli()
