import asyncio
from datetime import datetime, timezone
import os
import sys
from typing import Dict, Any
from flowforge.ports.worker import WorkerRuntime
from flowforge.domain.models import Job

class SubprocessWorkerRuntime(WorkerRuntime):
    async def execute_job(self, job: Job, script_path: str, timeout_seconds: int = 300) -> Job:
        job.status = "RUNNING"
        job.started_at = datetime.now(timezone.utc)

        if not os.path.exists(script_path):
            job.status = "FAILED"
            job.stderr = f"Error: Script file '{script_path}' not found."
            job.ended_at = datetime.now(timezone.utc)
            return job

        # Create isolated environment variables (sanitize env)
        # We only pass essential environment variables to avoid leaking sensitive information
        clean_env = {
            "PATH": os.getenv("PATH", ""),
            "SYSTEMROOT": os.getenv("SYSTEMROOT", ""),  # Required for Windows subprocess
            "COMSPEC": os.getenv("COMSPEC", ""),
            "PYTHONPATH": os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        }

        try:
            # Execute python interpreter with script_path using asyncio subprocess
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=clean_env
            )

            # Wait for execution with timeout
            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout_seconds
                )
                
                job.stdout = stdout_bytes.decode("utf-8", errors="replace")
                job.stderr = stderr_bytes.decode("utf-8", errors="replace")

                if proc.returncode == 0:
                    job.status = "COMPLETED"
                else:
                    job.status = "FAILED"
                    
            except asyncio.TimeoutError:
                # Terminate process if timeout exceeded
                try:
                    proc.kill()
                except ProcessLookupError:
                    pass
                
                # Consume output remaining
                stdout_bytes, stderr_bytes = await proc.communicate()
                
                job.stdout = stdout_bytes.decode("utf-8", errors="replace")
                job.stderr = stderr_bytes.decode("utf-8", errors="replace") + f"\n[TimeoutError: Execution exceeded {timeout_seconds} seconds]"
                job.status = "FAILED"

        except Exception as e:
            job.status = "FAILED"
            job.stderr = f"Exception occurred during execution: {str(e)}"

        job.ended_at = datetime.now(timezone.utc)
        return job
