import asyncio
import os
import shutil
import tempfile
from typing import Optional

class WorkspaceSandbox:
    def __init__(self, main_repo_path: str):
        self.main_repo_path = os.path.abspath(main_repo_path)

    async def clone_sandbox(self) -> str:
        """
        Clones the main repository into a unique temporary sandbox directory 
        to isolate AI modifications (Challenge #6).
        """
        temp_dir = tempfile.mkdtemp(prefix="flowforge_sandbox_")
        
        # Clone using git clone local mapping to save disk space and network bandwidth
        proc = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            self.main_repo_path,
            temp_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
        
        # Configure local dummy git profile inside sandbox to allow automated commits
        await asyncio.create_subprocess_exec("git", "config", "user.name", "FlowForge AI", cwd=temp_dir)
        await asyncio.create_subprocess_exec("git", "config", "user.email", "agent@flowforge.ai", cwd=temp_dir)
        
        return temp_dir

    async def verify_git_diff(self, sandbox_path: str) -> str:
        """
        Verifies if there are actual physical code changes staged or untracked.
        Returns 'SUCCESS' if changes exist, 'NO_CHANGE' otherwise (Challenge #3).
        """
        proc = await asyncio.create_subprocess_exec(
            "git",
            "status",
            "--porcelain",
            cwd=sandbox_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout_bytes, _ = await proc.communicate()
        status_output = stdout_bytes.decode("utf-8").strip()
        
        return "SUCCESS" if len(status_output) > 0 else "NO_CHANGE"

    async def create_auto_commit_branch(self, sandbox_path: str, job_id: str) -> str:
        """
        Auto-stages all modifications, commits them, and checks out a custom 
        JOB branch 'flowforge/JOB-<id>' (Challenge #7).
        """
        branch_name = f"flowforge/JOB-{job_id}"
        
        # 1. Create and checkout custom branch
        proc = await asyncio.create_subprocess_exec(
            "git", "checkout", "-b", branch_name,
            cwd=sandbox_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()

        # 2. Stage and commit changes
        await asyncio.create_subprocess_exec("git", "add", ".", cwd=sandbox_path)
        commit_proc = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", f"feat: completed automated changes for Job {job_id}",
            cwd=sandbox_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await commit_proc.communicate()
        
        return branch_name

    async def merge_to_main(self, sandbox_path: str, branch_name: str) -> None:
        """
        Merges the sandbox branch back to the main branch after approval (Challenge #6).
        """
        # Checkout to master/main in sandbox, merge the job branch, and pull/push
        # Get active default branch name (usually main or master)
        proc_branch = await asyncio.create_subprocess_exec(
            "git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD",
            cwd=sandbox_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc_branch.communicate()
        default_branch = stdout.decode("utf-8").strip().split("/")[-1] or "main"
        
        # Checkout default branch
        await asyncio.create_subprocess_exec("git", "checkout", default_branch, cwd=sandbox_path)
        # Merge job branch
        await asyncio.create_subprocess_exec("git", "merge", branch_name, cwd=sandbox_path)
        
    def cleanup(self, sandbox_path: str) -> None:
        """Deletes the temporary sandbox directory."""
        if os.path.exists(sandbox_path):
            shutil.rmtree(sandbox_path, ignore_errors=True)
