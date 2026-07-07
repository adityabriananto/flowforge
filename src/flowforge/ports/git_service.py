from abc import ABC, abstractmethod

class GitService(ABC):
    @abstractmethod
    async def checkout_branch(self, branch_name: str) -> None:
        """
        Creates or checks out to a branch.
        """
        pass

    @abstractmethod
    async def commit_changes(self, message: str) -> None:
        """
        Adds all files to stage and commits with the message.
        """
        pass

    @abstractmethod
    async def push_changes(self, branch_name: str) -> None:
        """
        Pushes changes to the remote branch.
        """
        pass
