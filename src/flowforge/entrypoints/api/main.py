from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from flowforge.adapters.database.database import init_db
from flowforge.entrypoints.api.router import router
from flowforge.entrypoints.api.websocket_manager import ws_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup (as agreed for early dev/testing)
    await init_db()
    yield

app = FastAPI(
    title="FlowForge REST API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend dashboard communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(router)

@app.websocket("/ws/instances/{instance_id}")
async def websocket_endpoint(websocket: WebSocket, instance_id: str):
    await ws_manager.connect(instance_id, websocket)
    try:
        # Keep connection alive, listen for client messages (ignored as push-only phase)
        while True:
            # Receive data but discard/ignore it (push-only)
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(instance_id, websocket)
    except Exception:
        ws_manager.disconnect(instance_id, websocket)
