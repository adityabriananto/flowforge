import os
import shutil
import tempfile
import asyncio
from flowforge.ports.workspace import Workspace

class LocalWorkspace(Workspace):
    """
    A Local Sandboxed Workspace Adapter that isolates the workspace using git clone locally (Challenge #6).
    """
    def __init__(self, main_repo_path: str, job_id: str = "9999"):
        self.main_repo_path = os.path.abspath(main_repo_path)
        self.job_id = job_id
        self.sandbox_path: Optional[str] = None

    async def setup(self) -> str:
        self.sandbox_path = tempfile.mkdtemp(prefix="flowforge_sandbox_")
        
        proc = await asyncio.create_subprocess_exec(
            "git", "clone", self.main_repo_path, self.sandbox_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        
        await asyncio.create_subprocess_exec("git", "config", "user.name", "FlowForge AI", cwd=self.sandbox_path)
        await asyncio.create_subprocess_exec("git", "config", "user.email", "agent@flowforge.ai", cwd=self.sandbox_path)
        return self.sandbox_path

    async def check_diff(self) -> str:
        if not self.sandbox_path:
            return "NO_CHANGE"
            
        proc = await asyncio.create_subprocess_exec(
            "git", "status", "--porcelain",
            cwd=self.sandbox_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        status_output = stdout.decode("utf-8").strip()
        return "SUCCESS" if len(status_output) > 0 else "NO_CHANGE"

    async def commit_changes(self, message: str) -> str:
        if not self.sandbox_path:
            raise RuntimeError("Workspace sandbox is not initialized.")
            
        branch_name = f"flowforge/JOB-{self.job_id}"
        
        # Checkout new branch
        checkout_proc = await asyncio.create_subprocess_exec(
            "git", "checkout", "-b", branch_name, cwd=self.sandbox_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await checkout_proc.communicate()

        # Add and commit
        await asyncio.create_subprocess_exec("git", "add", ".", cwd=self.sandbox_path)
        commit_proc = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", message, cwd=self.sandbox_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await commit_proc.communicate()
        
        return branch_name

    def cleanup(self) -> None:
        if self.sandbox_path and os.path.exists(self.sandbox_path):
            shutil.rmtree(self.sandbox_path, ignore_errors=True)
            self.sandbox_path = None
