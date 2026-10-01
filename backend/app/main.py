import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import init_db, AsyncSessionLocal
from backend.app.core.events import event_manager
from backend.app.services.world_engine import world_engine

from backend.app.api.auth import router as auth_router
from backend.app.api.incidents import router as incidents_router
from backend.app.api.resources import router as resources_router
from backend.app.api.shelters import router as shelters_router
from backend.app.api.roads import router as roads_router
from backend.app.api.plans import router as plans_router
from backend.app.api.agents import router as agents_router
from backend.app.api.simulation import router as simulation_router
from backend.app.api.operational import router as operational_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("resq")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing RESQ database tables and authoritative seed datasets...")
    await init_db()
    async with AsyncSessionLocal() as session:
        await world_engine.seed_initial_world(session)
        # Load default flood scenario
        await world_engine.load_scenario(session, "flood")
    logger.info("RESQ Backend initialized successfully in SIMULATION MODE.")
    yield
    logger.info("Shutting down RESQ Backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-agent AI disaster response coordination platform.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)
app.include_router(resources_router, prefix=settings.API_V1_STR)
app.include_router(shelters_router, prefix=settings.API_V1_STR)
app.include_router(roads_router, prefix=settings.API_V1_STR)
app.include_router(plans_router, prefix=settings.API_V1_STR)
app.include_router(agents_router, prefix=settings.API_V1_STR)
app.include_router(simulation_router, prefix=settings.API_V1_STR)
app.include_router(operational_router, prefix=settings.API_V1_STR)

# Health Check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "platform": "RESQ Intelligent Disaster Response Coordination Platform",
        "simulation_mode": True,
        "database": "connected",
        "gemini_configured": bool(settings.GEMINI_API_KEY)
    }

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await event_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, listen for ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        event_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        event_manager.disconnect(websocket)
