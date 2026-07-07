import sys
import os
import pytest
from unittest.mock import patch, AsyncMock

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.adapters.git.subprocess_git import SubprocessGitService

@pytest.mark.asyncio
async def test_git_service_local_operations(tmp_path):
    # Initialize a dummy git repository in the temporary path
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    
    # Configure dummy user for local git repo to allow committing
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "config", "user.email", "test@user.com"], cwd=str(tmp_path), check=True)

    git_service = SubprocessGitService(repo_path=str(tmp_path))

    # 1. Create a dummy file in the temp repo and commit it first to establish HEAD
    test_file = tmp_path / "dummy.txt"
    test_file.write_text("Hello Git Integration!")
    await git_service.commit_changes("Initial dummy commit")

    # Verify first commit exists
    log_output = subprocess.run(
        ["git", "log", "-n", "1", "--oneline"], 
        cwd=str(tmp_path), 
        capture_output=True, 
        text=True, 
        check=True
    )
    assert "Initial dummy commit" in log_output.stdout

    # 2. Checkout to a new branch after HEAD has been established
    await git_service.checkout_branch("feature-test-branch")
    
    # Verify current branch is correct
    branch_output = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], 
        cwd=str(tmp_path), 
        capture_output=True, 
        text=True, 
        check=True
    )
    assert branch_output.stdout.strip() == "feature-test-branch"

@pytest.mark.asyncio
async def test_git_push_changes_mocked():
    git_service = SubprocessGitService(repo_path="/fake/path")
    
    # Mock _run_git_cmd to verify push parameters without hitting actual git push shell command
    with patch.object(git_service, "_run_git_cmd", new_callable=AsyncMock) as mock_run:
        await git_service.push_changes("main-branch")
        mock_run.assert_called_once_with(["push", "origin", "main-branch"])
