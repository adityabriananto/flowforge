import asyncio
import os
from typing import Optional
from flowforge.ports.git_service import GitService

class SubprocessGitService(GitService):
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = repo_path or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))

    async def _run_git_cmd(self, args: list[str]) -> str:
        """Helper method to run a git command in the repository path."""
        try:
            # Clean env with PATH for Git execution
            clean_env = {
                "PATH": os.getenv("PATH", ""),
                "SYSTEMROOT": os.getenv("SYSTEMROOT", ""),
                "COMSPEC": os.getenv("COMSPEC", ""),
                "GIT_AUTHOR_NAME": "FlowForge AI",
                "GIT_AUTHOR_EMAIL": "agent@flowforge.ai",
                "GIT_COMMITTER_NAME": "FlowForge AI",
                "GIT_COMMITTER_EMAIL": "agent@flowforge.ai"
            }
            
            proc = await asyncio.create_subprocess_exec(
                "git",
                *args,
                cwd=self.repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=clean_env
            )
            
            stdout_bytes, stderr_bytes = await proc.communicate()
            stdout = stdout_bytes.decode("utf-8", errors="replace").strip()
            stderr = stderr_bytes.decode("utf-8", errors="replace").strip()
            
            if proc.returncode != 0:
                raise RuntimeError(
                    f"Git command failed: git {' '.join(args)}. "
                    f"Exit code: {proc.returncode}. Stderr: {stderr}"
                )
            return stdout
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise e
            raise RuntimeError(f"Exception executing git command: {str(e)}")

    async def checkout_branch(self, branch_name: str) -> None:
        # Try checking out existing branch, if fails, create and checkout new branch
        try:
            await self._run_git_cmd(["checkout", branch_name])
        except RuntimeError:
            await self._run_git_cmd(["checkout", "-b", branch_name])

    async def commit_changes(self, message: str) -> None:
        await self._run_git_cmd(["add", "."])
        # Only commit if there are actual changes staged to avoid committing empty
        status = await self._run_git_cmd(["status", "--porcelain"])
        if status:
            await self._run_git_cmd(["commit", "-m", message])

    async def push_changes(self, branch_name: str) -> None:
        # Note: In mock tests this will be intercepted/mocked, in real environment this pushes to origin
        await self._run_git_cmd(["push", "origin", branch_name])
