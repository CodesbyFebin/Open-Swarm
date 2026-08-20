"""
Open Swarm Blackboard - Shared Stigmergy Memory
JSONL-persisted shared memory for swarm agents
"""

import asyncio
import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any


@dataclass
class BlackboardEntry:
    """Single entry in the blackboard"""

    id: str
    agent_id: str
    agent_type: str
    key: str
    value: Any
    timestamp: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class Blackboard:
    """
    Shared stigmergy memory for swarm agents.
    Agents write to and read from this central memory space.
    """

    def __init__(self, storage_path: str = "data/blackboard.jsonl"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self._memory: dict[str, list[BlackboardEntry]] = {}
        self._lock = Lock()
        self._session_id = str(uuid.uuid4())

        # Load existing memory if file exists
        self._load_existing()

    def _load_existing(self):
        """Load existing blackboard data from JSONL file"""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path) as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        entry = BlackboardEntry(**data)
                        if entry.key not in self._memory:
                            self._memory[entry.key] = []
                        self._memory[entry.key].append(entry)
        except Exception as e:
            print(f"[Blackboard] Warning: Could not load existing data: {e}")

    def _persist_entry(self, entry: BlackboardEntry):
        """Persist entry to JSONL file"""
        try:
            with open(self.storage_path, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
        except Exception as e:
            print(f"[Blackboard] Warning: Could not persist entry: {e}")

    def write(
        self,
        agent_id: str,
        agent_type: str,
        key: str,
        value: Any,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Write data to blackboard
        Returns entry ID
        """
        with self._lock:
            entry_id = str(uuid.uuid4())
            entry = BlackboardEntry(
                id=entry_id,
                agent_id=agent_id,
                agent_type=agent_type,
                key=key,
                value=value,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {},
            )

            if key not in self._memory:
                self._memory[key] = []

            self._memory[key].append(entry)
            self._persist_entry(entry)

            print(f"[Blackboard] {agent_type} ({agent_id}) wrote to {key}")
            return entry_id

    def read(self, key: str, agent_id: str | None = None) -> list[BlackboardEntry]:
        """
        Read all entries for a key
        Optionally filter by agent_id
        """
        with self._lock:
            entries = self._memory.get(key, [])

            if agent_id:
                entries = [e for e in entries if e.agent_id != agent_id]

            return entries.copy()

    def read_latest(self, key: str, agent_id: str | None = None) -> BlackboardEntry | None:
        """Read the most recent entry for a key"""
        entries = self.read(key, agent_id)

        if not entries:
            return None

        # Return most recent by timestamp
        return max(entries, key=lambda e: e.timestamp)

    def read_all_keys(self) -> dict[str, list[BlackboardEntry]]:
        """Get all entries grouped by key"""
        with self._lock:
            return {k: v.copy() for k, v in self._memory.items()}

    def clear(self, key: str | None = None):
        """Clear blackboard entries"""
        with self._lock:
            if key:
                self._memory.pop(key, None)
            else:
                self._memory.clear()

            # Truncate file if clearing all
            if key is None:
                with open(self.storage_path, "w"):
                    pass

    def get_state_summary(self) -> dict[str, Any]:
        """Get summary of current blackboard state"""
        with self._lock:
            summary = {
                "session_id": self._session_id,
                "total_keys": len(self._memory),
                "total_entries": sum(len(v) for v in self._memory.values()),
                "keys": {},
            }

            for key, entries in self._memory.items():
                latest = max(entries, key=lambda e: e.timestamp) if entries else None
                summary["keys"][key] = {
                    "count": len(entries),
                    "latest_agent": latest.agent_type if latest else None,
                    "latest_timestamp": latest.timestamp if latest else None,
                    "agents": list(set(e.agent_type for e in entries)),
                }

            return summary

    async def watch_key(self, key: str, callback):
        """
        Watch a key for changes and call callback when new entries appear
        """
        last_seen = 0

        while True:
            with self._lock:
                entries = self._memory.get(key, [])
                if len(entries) > last_seen:
                    new_entries = entries[last_seen:]
                    last_seen = len(entries)

                    for entry in new_entries:
                        await callback(entry)

            await asyncio.sleep(0.1)


# Global blackboard instance
_blackboard_instance: Blackboard | None = None


def get_blackboard() -> Blackboard:
    """Get or create blackboard singleton"""
    global _blackboard_instance
    if _blackboard_instance is None:
        _blackboard_instance = Blackboard()
    return _blackboard_instance


# Convenience functions
def write_to_blackboard(
    agent_id: str, agent_type: str, key: str, value: Any, metadata: dict | None = None
):
    """Convenience function to write to blackboard"""
    bb = get_blackboard()
    return bb.write(agent_id, agent_type, key, value, metadata)


def read_from_blackboard(key: str, agent_id: str | None = None) -> list[BlackboardEntry]:
    """Convenience function to read from blackboard"""
    bb = get_blackboard()
    return bb.read(key, agent_id)
