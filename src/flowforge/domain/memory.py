import os
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

@dataclass
class MemoryEntry:
    role: str  # system, user, assistant, worker
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class Memory:
    def __init__(self, memory_dir: Optional[str] = None):
        self.entries: List[MemoryEntry] = []
        self.memory_dir = memory_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.project/memory"))

    def add_entry(self, role: str, content: str) -> MemoryEntry:
        """Adds a short-term memory entry in memory."""
        entry = MemoryEntry(role=role, content=content)
        self.entries.append(entry)
        return entry

    def get_history(self) -> List[MemoryEntry]:
        """Returns the in-memory short-term context history."""
        return self.entries

    def clear(self) -> None:
        """Clears current short-term memory."""
        self.entries.clear()

    async def save_to_disk(self, filename: str) -> None:
        """Persists short-term memory entries to a JSON file on disk (long-term)."""
        os.makedirs(self.memory_dir, exist_ok=True)
        file_path = os.path.join(self.memory_dir, filename)
        
        serialized = [entry.to_dict() for entry in self.entries]
        
        # Asynchronously write to disk in a separate executor to prevent blocking event loop
        import asyncio
        loop = asyncio.get_event_loop()
        def write_sync():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(serialized, f, indent=2, ensure_ascii=False)
        
        await loop.run_in_executor(None, write_sync)

    async def load_from_disk(self, filename: str) -> None:
        """Loads long-term memory entries from a JSON file into short-term memory."""
        file_path = os.path.join(self.memory_dir, filename)
        if not os.path.exists(file_path):
            return

        import asyncio
        loop = asyncio.get_event_loop()
        def read_sync():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        serialized = await loop.run_in_executor(None, read_sync)
        self.entries = [MemoryEntry.from_dict(item) for item in serialized]
