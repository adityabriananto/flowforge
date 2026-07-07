import sys
import os
import uuid
from datetime import datetime, timezone
import pytest
import pytest_asyncio

# Add src/ folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from flowforge.adapters.database.database import init_db, async_session_factory
from flowforge.adapters.database.repository import SQLAlchemyRepository
from flowforge.domain.models import Workflow, StateConfig, WorkflowInstance, Job, Event

@pytest_asyncio.fixture
async def setup_database():
    # Initialize tables in SQLite memory db before each test
    await init_db()
    yield

@pytest.fixture
def sample_workflow():
    states = {
        "IDLE": StateConfig(name="IDLE", next_state="CODING"),
        "CODING": StateConfig(name="CODING", worker_type="python_agent", script="agents/coder.py", next_state="TESTING", on_failure="FAILED")
    }
    
    return Workflow(
        id=uuid.uuid4(),
        name="Persistence Test Workflow",
        version="1.0.0",
        initial_state="IDLE",
        states=states
    )

@pytest.fixture
def sample_instance(sample_workflow):
    return WorkflowInstance(
        id=uuid.uuid4(),
        workflow_id=sample_workflow.id,
        current_state="IDLE",
        variables={"source_repo": "git://test"}
    )

@pytest.mark.asyncio
async def test_workflow_persistence(setup_database, sample_workflow):
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        # Save workflow
        await repo.save_workflow(sample_workflow)
        await session.commit()
        
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        # Fetch workflow
        fetched = await repo.get_workflow(sample_workflow.id)
        
        assert fetched is not None
        assert fetched.id == sample_workflow.id
        assert fetched.name == "Persistence Test Workflow"
        assert "IDLE" in fetched.states
        assert fetched.states["CODING"].worker_type == "python_agent"

@pytest.mark.asyncio
async def test_workflow_instance_persistence(setup_database, sample_workflow, sample_instance):
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        
        await repo.save_workflow(sample_workflow)
        await repo.save_instance(sample_instance)
        await session.commit()
        
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        fetched = await repo.get_instance(sample_instance.id)
        
        assert fetched is not None
        assert fetched.id == sample_instance.id
        assert fetched.current_state == "IDLE"
        assert fetched.variables["source_repo"] == "git://test"

@pytest.mark.asyncio
async def test_job_persistence(setup_database, sample_workflow, sample_instance):
    job = Job(
        id=uuid.uuid4(),
        instance_id=sample_instance.id,
        state_name="CODING",
        status="RUNNING",
        started_at=datetime.now(timezone.utc)
    )
    
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        
        await repo.save_workflow(sample_workflow)
        await repo.save_instance(sample_instance)
        await repo.save_job(job)
        await session.commit()
        
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        fetched = await repo.get_job(job.id)
        
        assert fetched is not None
        assert fetched.id == job.id
        assert fetched.status == "RUNNING"
        assert fetched.state_name == "CODING"

@pytest.mark.asyncio
async def test_event_persistence(setup_database, sample_workflow, sample_instance):
    event = Event(
        id=uuid.uuid4(),
        instance_id=sample_instance.id,
        event_type="STATE_CHANGED",
        payload={"from_state": "IDLE", "to_state": "CODING"},
        triggered_by="SYSTEM"
    )
    
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        
        await repo.save_workflow(sample_workflow)
        await repo.save_instance(sample_instance)
        await repo.save_event(event)
        await session.commit()
        
    async with async_session_factory() as session:
        repo = SQLAlchemyRepository(session)
        fetched_list = await repo.get_events_for_instance(sample_instance.id)
        
        assert len(fetched_list) == 1
        assert fetched_list[0].id == event.id
        assert fetched_list[0].event_type == "STATE_CHANGED"
        assert fetched_list[0].payload["from_state"] == "IDLE"
