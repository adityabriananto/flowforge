from abc import ABC, abstractmethod
from flowforge.domain.models import Job

class WorkerRuntime(ABC):
    @abstractmethod
    async def execute_job(self, job: Job, script_path: str, timeout_seconds: int = 300) -> Job:
        """
        Executes a job asynchronously using the runtime.
        Updates the job instance with stdout, stderr, ended_at, and status.
        Returns the updated Job domain object.
        """
        pass
