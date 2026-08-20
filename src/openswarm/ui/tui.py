"""
Open Swarm Textual TUI
Multi-panel terminal interface for swarm monitoring
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import (
    Header, Footer, Button, Input, 
    Log, DataTable, Static, ProgressBar
)
from textual.reactive import reactive
from textual.message import Message
import asyncio
from datetime import datetime

class AgentPanel(Static):
    """Panel showing agent activity"""
    
    def __init__(self, agent_type: str, **kwargs):
        super().__init__(**kwargs)
        self.agent_type = agent_type
        self.logs = Log()
    
    def compose(self) -> ComposeResult:
        yield Static(f"[bold]{self.agent_type.upper()}[/bold]", classes="agent-header")
        yield self.logs
        yield Button("Pause", id=f"pause-{self.agent_type}")
    
    def log(self, message: str):
        self.logs.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


class SwarmTUI(App):
    """Open Swarm Terminal UI"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #top-bar {
        height: 3;
        background: $primary;
    }
    
    #agent-panels {
        height: 1fr;
        layout: horizontal;
    }
    
    AgentPanel {
        width: 1fr;
        border: solid $primary;
        margin: 1;
    }
    
    .agent-header {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
    }
    
    #status-bar {
        height: 3;
        background: $surface;
    }
    
    #input-panel {
        height: 5;
        background: $surface;
    }
    
    DataTable {
        height: 1fr;
    }
    """
    
    TITLE = "Open Swarm"
    SUB_TITLE = "Parallel Multi-Agent Coding Swarm"
    
    def compose(self) -> ComposeResult:
        yield Header()
        
        with Container(id="top-bar"):
            yield Static("🐝 Open Swarm - Parallel Multi-Agent System", classes="header")
        
        with Horizontal(id="agent-panels"):
            with Vertical():
                yield AgentPanel("Scout", id="scout-panel")
            with Vertical():
                yield AgentPanel("Planner", id="planner-panel")
            with Vertical():
                yield AgentPanel("Coder", id="coder-panel")
            with Vertical():
                yield AgentPanel("Critic", id="critic-panel")
        
        with Horizontal(id="status-bar"):
            self.model_table = DataTable()
            self.model_table.add_columns("Model", "Purpose", "Status")
            yield self.model_table
        
        with Container(id="input-panel"):
            self.goal_input = Input(placeholder="Enter your goal...", id="goal-input")
            yield self.goal_input
            yield Button("Run Swarm", id="run-button", variant="primary")
            yield Button("Pause", id="pause-button", variant="error")
            yield Button("Resume", id="resume-button")
        
        yield Footer()
    
    def on_mount(self):
        self.title = "Open Swarm - Running"
        self.status = "idle"
        self.update_models_table()
        asyncio.create_task(self.simulate_agent_activity())
    
    def update_models_table(self):
        """Update models table"""
        self.model_table.clear()
        models = [
            ("qwen2.5-coder:3b", "fast", "✓ Local"),
            ("qwen3:8b", "reasoning", "✓ Local"),
            ("llama-3.3-70b", "reasoning", "☁ Free"),
            ("deepseek-v3", "coding", "☁ Free"),
        ]
        for model, purpose, status in models:
            self.model_table.add_row(model, purpose, status)
    
    async def simulate_agent_activity(self):
        """Simulate agent activity for demo"""
        agents = ["scout", "planner", "coder", "critic"]
        messages = [
            "Exploring codebase...",
            "Found 12 relevant files",
            "Mapping dependencies...",
            "Analyzing patterns...",
            "Planning refactoring steps...",
            "Identified 3 high-risk areas...",
            "Generating code proposal...",
            "Writing async handlers...",
            "Reviewing for security issues...",
            "Found potential race condition...",
            "Synthesizing final output..."
        ]
        
        for msg in messages:
            for agent in agents:
                panel = self.query_one(f"#{agent}-panel", AgentPanel)
                panel.log(msg)
                await asyncio.sleep(0.5)
    
    def on_button_pressed(self, event: Button.Pressed):
        """Handle button presses"""
        if event.button.id == "run-button":
            goal = self.goal_input.value
            if goal:
                self.query_one("#scout-panel", AgentPanel).log(f"Starting: {goal}")
                asyncio.create_task(self.run_swarm(goal))
        
        elif event.button.id == "pause-button":
            self.status = "paused"
        
        elif event.button.id == "resume-button":
            self.status = "running"
    
    async def run_swarm(self, goal: str):
        """Run swarm workflow"""
        # In production, would call actual orchestrator
        self.query_one("#scout-panel", AgentPanel).log(f"Scouting for: {goal}")
        await asyncio.sleep(1)
        
        self.query_one("#planner-panel", AgentPanel).log("Creating plan...")
        await asyncio.sleep(1)
        
        self.query_one("#coder-panel", AgentPanel).log("Generating code...")
        await asyncio.sleep(1)
        
        self.query_one("#critic-panel", AgentPanel).log("Reviewing changes...")
        await asyncio.sleep(1)
        
        self.query_one("#scout-panel", AgentPanel).log("✓ Swarm complete!")


if __name__ == "__main__":
    app = SwarmTUI()
    app.run()
