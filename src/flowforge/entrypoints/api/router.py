from fastapi import APIRouter, HTTPException, Depends
import uuid
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from flowforge.adapters.database.database import async_session_factory
from flowforge.adapters.database.repository import SQLAlchemyRepository
from flowforge.domain.models import Workflow, WorkflowInstance, StateConfig
from flowforge.domain.engine import StateMachine, InvalidTransitionError
from flowforge.entrypoints.api.schemas import (
    WorkflowCreate, WorkflowResponse, InstanceCreate, InstanceResponse,
    TransitionRequest, EventResponse
)
from flowforge.entrypoints.api.websocket_manager import ws_manager

router = APIRouter(prefix="/api")

# Dependency injection for DB session
async def get_db():
    async with async_session_factory() as session:
        yield session

@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(payload: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyRepository(db)
    
    # Map schema to domain model
    states = {}
    for name, config in payload.states.items():
        states[name] = StateConfig(
            name=config.name,
            worker_type=config.worker_type,
            script=config.script,
            timeout_seconds=config.timeout_seconds,
            next_state=config.next_state,
            on_failure=config.on_failure,
            require_human=config.require_human,
            on_approve=config.on_approve,
            on_reject=config.on_reject,
            is_final=config.is_final
        )
        
    workflow = Workflow(
        id=uuid.uuid4(),
        name=payload.name,
        version=payload.version,
        initial_state=payload.initial_state,
        states=states
    )
    
    await repo.save_workflow(workflow)
    await db.commit()
    return workflow

@router.post("/instances", response_model=InstanceResponse)
async def create_instance(payload: InstanceCreate, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyRepository(db)
    
    # Verify workflow exists
    workflow = await repo.get_workflow(payload.workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    instance = WorkflowInstance(
        id=uuid.uuid4(),
        workflow_id=payload.workflow_id,
        current_state=workflow.initial_state,
        variables=payload.variables
    )
    
    await repo.save_instance(instance)
    await db.commit()
    return instance

@router.get("/instances/{instance_id}", response_model=InstanceResponse)
async def get_instance(instance_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyRepository(db)
    instance = await repo.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
    return instance

@router.post("/instances/{instance_id}/transition", response_model=EventResponse)
async def trigger_transition(
    instance_id: uuid.UUID, 
    payload: TransitionRequest, 
    db: AsyncSession = Depends(get_db)
):
    repo = SQLAlchemyRepository(db)
    
    # Fetch instance & workflow
    instance = await repo.get_instance(instance_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Workflow instance not found")
        
    workflow = await repo.get_workflow(instance.workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow template not found")
        
    engine = StateMachine(workflow)
    
    try:
        # Transition state
        transition_event = engine.transition(
            instance, 
            payload.event, 
            triggered_by=payload.triggered_by
        )
        
        # Save updated instance & the new event to database
        await repo.save_instance(instance)
        await repo.save_event(transition_event)
        await db.commit()
        
        # Broadcast the transition update to WebSocket listeners (push-only)
        await ws_manager.broadcast_to_instance(
            str(instance_id),
            {
                "event_type": "STATE_TRANSITION",
                "instance_id": str(instance_id),
                "from_state": transition_event.payload["from_state"],
                "to_state": transition_event.payload["to_state"],
                "trigger_event": payload.event,
                "require_human": transition_event.payload["require_human"]
            }
        )
        
        return transition_event
        
    except InvalidTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/instances/{instance_id}/events", response_model=List[EventResponse])
async def get_instance_events(instance_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = SQLAlchemyRepository(db)
    events = await repo.get_events_for_instance(instance_id)
    return events
