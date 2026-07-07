from abc import ABC, abstractmethod

class Workspace(ABC):
    @abstractmethod
    async def setup(self) -> str:
        """Sets up the workspace (cloning, mounting sandbox, etc). Returns sandbox directory path."""
        pass

    @abstractmethod
    async def check_diff(self) -> str:
        """Checks for staged or unstaged modifications. Returns 'SUCCESS' or 'NO_CHANGE'."""
        pass

    @abstractmethod
    async def commit_changes(self, message: str) -> str:
        """Commits changes and returns branch name."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleans up workspace resources."""
        pass
