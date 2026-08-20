"""
Base agent class for Open Swarm
"""

from abc import ABC, abstractmethod
from typing import Any

from ..core.blackboard import get_blackboard


class BaseAgent(ABC):
    """Base class for all swarm agents"""

    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.blackboard = get_blackboard()

    @abstractmethod
    async def execute(self, task: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute agent task"""
        pass

    def write(self, key: str, value: Any, metadata: dict[str, Any] = None):
        """Write to blackboard"""
        return self.blackboard.write(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            key=key,
            value=value,
            metadata=metadata,
        )

    def read(self, key: str):
        """Read from blackboard"""
        return self.blackboard.read(key)
