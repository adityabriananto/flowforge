import sys
import os
import uuid
import pytest

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.adapters.worker.subprocess_runtime import SubprocessWorkerRuntime
from flowforge.domain.models import Job

@pytest.mark.asyncio
async def test_subprocess_execution_success(tmp_path):
    # Setup dummy script that prints output and exits 0
    script_content = "print('Hello from FlowForge Worker!')"
    script_file = tmp_path / "success_worker.py"
    script_file.write_text(script_content)
    
    runtime = SubprocessWorkerRuntime()
    job = Job(id=uuid.uuid4(), instance_id=uuid.uuid4(), state_name="CODING", status="PENDING")
    
    updated_job = await runtime.execute_job(job, str(script_file), timeout_seconds=10)
    
    assert updated_job.status == "COMPLETED"
    assert "Hello from FlowForge Worker!" in updated_job.stdout
    assert updated_job.stderr == ""
    assert updated_job.started_at is not None
    assert updated_job.ended_at is not None
    assert updated_job.started_at <= updated_job.ended_at

@pytest.mark.asyncio
async def test_subprocess_execution_failure(tmp_path):
    # Setup dummy script that prints error message and exits 1
    script_content = "import sys; print('Testing failure log', file=sys.stderr); sys.exit(1)"
    script_file = tmp_path / "fail_worker.py"
    script_file.write_text(script_content)
    
    runtime = SubprocessWorkerRuntime()
    job = Job(id=uuid.uuid4(), instance_id=uuid.uuid4(), state_name="CODING", status="PENDING")
    
    updated_job = await runtime.execute_job(job, str(script_file), timeout_seconds=10)
    
    assert updated_job.status == "FAILED"
    assert "Testing failure log" in updated_job.stderr
    assert updated_job.ended_at is not None

@pytest.mark.asyncio
async def test_subprocess_execution_timeout(tmp_path):
    # Setup dummy script that runs an infinite/long loop
    script_content = "import time; time.sleep(5)"
    script_file = tmp_path / "timeout_worker.py"
    script_file.write_text(script_content)
    
    runtime = SubprocessWorkerRuntime()
    job = Job(id=uuid.uuid4(), instance_id=uuid.uuid4(), state_name="CODING", status="PENDING")
    
    # Run with a short 1 second timeout
    updated_job = await runtime.execute_job(job, str(script_file), timeout_seconds=1)
    
    assert updated_job.status == "FAILED"
    assert "TimeoutError" in updated_job.stderr
    assert "exceeded 1 seconds" in updated_job.stderr
    assert updated_job.ended_at is not None

@pytest.mark.asyncio
async def test_subprocess_execution_file_not_found():
    runtime = SubprocessWorkerRuntime()
    job = Job(id=uuid.uuid4(), instance_id=uuid.uuid4(), state_name="CODING", status="PENDING")
    
    updated_job = await runtime.execute_job(job, "non_existent_file.py", timeout_seconds=10)
    
    assert updated_job.status == "FAILED"
    assert "not found" in updated_job.stderr
    assert updated_job.ended_at is not None
