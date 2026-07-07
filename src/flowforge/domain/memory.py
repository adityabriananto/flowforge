import os
import json
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


class LessonLearnedStore:
    """
    A persistent registry to save 'Lessons Learned' from completed workflow runs,
    allowing future workflow runs to read historical warnings/success cases and self-improve.
    """
    def __init__(self, memory_dir: Optional[str] = None):
        self.memory_dir = memory_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.project/memory"))
        self.lessons: Dict[str, List[str]] = {}  # workflow_name -> list of lesson strings

    def add_lesson(self, workflow_name: str, lesson: str) -> None:
        """Adds a lesson learned to a specific workflow template history."""
        name_key = workflow_name.lower()
        if name_key not in self.lessons:
            self.lessons[name_key] = []
        if lesson not in self.lessons[name_key]:
            self.lessons[name_key].append(lesson)

    def get_lessons(self, workflow_name: str) -> List[str]:
        """Returns list of lessons learned for a workflow."""
        return self.lessons.get(workflow_name.lower(), [])

    async def persist(self) -> None:
        """Saves all lessons to disk in lessons.json."""
        os.makedirs(self.memory_dir, exist_ok=True)
        file_path = os.path.join(self.memory_dir, "lessons.json")
        
        import asyncio
        loop = asyncio.get_event_loop()
        def write_sync():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.lessons, f, indent=2, ensure_ascii=False)
        
        await loop.run_in_executor(None, write_sync)

    async def load(self) -> None:
        """Loads all lessons from lessons.json on disk."""
        file_path = os.path.join(self.memory_dir, "lessons.json")
        if not os.path.exists(file_path):
            return

        import asyncio
        loop = asyncio.get_event_loop()
        def read_sync():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        
        loaded = await loop.run_in_executor(None, read_sync)
        self.lessons = {k.lower(): v for k, v in loaded.items()}
