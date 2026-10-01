from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from backend.app.core.database import get_db
from backend.app.models.simulation import SimulationScenario, SimulationEvent
from backend.app.schemas.common import SimulationScenarioResponse, HazardInjectionRequest
from backend.app.services.world_engine import world_engine
from backend.app.core.events import event_manager
from backend.app.scenarios.suryanagar_data import DISASTER_SCENARIOS

router = APIRouter(prefix="/simulation", tags=["Simulation Control"])

class SpeedUpdateRequest(BaseModel):
    multiplier: float # 1.0, 2.0, 5.0

class LoadScenarioRequest(BaseModel):
    disaster_type: str # flood, cyclone, earthquake, wildfire, landslide

@router.get("/scenarios/available")
async def list_available_scenarios():
    """Lists the 5 supported disaster scenarios with metadata."""
    return [
        {
            "id": k,
            "disaster_type": k,
            "name": v["name"],
            "description": v["description"],
            "weather_summary": v["weather_summary"],
            "hazards": [h["title"] for h in v.get("hazard_events", [])]
        }
        for k, v in DISASTER_SCENARIOS.items()
    ]

@router.get("/current", response_model=Optional[SimulationScenarioResponse])
async def get_current_scenario(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(
        select(SimulationScenario)
        .options(selectinload(SimulationScenario.events))
        .order_by(SimulationScenario.created_at.desc())
    )
    scenario = stmt.scalars().first()
    return scenario

@router.post("/load", response_model=SimulationScenarioResponse)
async def load_scenario(req: LoadScenarioRequest, db: AsyncSession = Depends(get_db)):
    """Loads and resets the world to the selected disaster scenario."""
    scenario = await world_engine.load_scenario(db, req.disaster_type)
    return scenario

@router.post("/start")
async def start_simulation(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(SimulationScenario).order_by(SimulationScenario.created_at.desc()))
    scenario = stmt.scalars().first()
    if not scenario:
        scenario = await world_engine.load_scenario(db, "flood")
    
    scenario.status = "RUNNING"
    await db.commit()
    await event_manager.broadcast("simulation.event", {"action": "STARTED", "scenario_id": scenario.id})
    return {"status": "RUNNING", "current_tick": scenario.current_tick}

@router.post("/pause")
async def pause_simulation(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(SimulationScenario).order_by(SimulationScenario.created_at.desc()))
    scenario = stmt.scalars().first()
    if scenario:
        scenario.status = "PAUSED"
        await db.commit()
        await event_manager.broadcast("simulation.event", {"action": "PAUSED", "scenario_id": scenario.id})
        return {"status": "PAUSED"}
    return {"status": "NO_SCENARIO"}

@router.post("/resume")
async def resume_simulation(db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(SimulationScenario).order_by(SimulationScenario.created_at.desc()))
    scenario = stmt.scalars().first()
    if scenario:
        scenario.status = "RUNNING"
        await db.commit()
        await event_manager.broadcast("simulation.event", {"action": "RESUMED", "scenario_id": scenario.id})
        return {"status": "RUNNING"}
    return {"status": "NO_SCENARIO"}

@router.post("/reset")
async def reset_simulation(db: AsyncSession = Depends(get_db)):
    """A reset must return the scenario to its original state."""
    disaster_type = world_engine.active_scenario_type or "flood"
    scenario = await world_engine.load_scenario(db, disaster_type)
    return {"status": "RESET", "scenario_id": scenario.id, "disaster_type": disaster_type}

@router.post("/speed")
async def set_speed(req: SpeedUpdateRequest, db: AsyncSession = Depends(get_db)):
    stmt = await db.execute(select(SimulationScenario).order_by(SimulationScenario.created_at.desc()))
    scenario = stmt.scalars().first()
    if scenario:
        scenario.speed_multiplier = req.multiplier
        await db.commit()
        return {"status": "SPEED_UPDATED", "multiplier": req.multiplier}
    return {"status": "NO_SCENARIO"}

@router.post("/next-event")
async def advance_next_event(db: AsyncSession = Depends(get_db)):
    """Advances world time by 1 tick, triggering scheduled scenario events."""
    stmt = await db.execute(select(SimulationScenario).order_by(SimulationScenario.created_at.desc()))
    scenario = stmt.scalars().first()
    if not scenario:
        scenario = await world_engine.load_scenario(db, "flood")
    
    result = await world_engine.advance_tick(db, scenario.id)
    return result

@router.post("/inject-hazard")
async def inject_hazard(req: HazardInjectionRequest, db: AsyncSession = Depends(get_db)):
    """
    Manually introduces a new road hazard (e.g. fallen debris, flash surge, bridge damage).
    This immediately triggers Route Invalidation & Continuous Multi-Agent Replanning!
    """
    result = await world_engine.inject_hazard(
        db,
        segment_code=req.segment_code,
        blockage_type=req.blockage_type,
        description=req.description
    )
    return {"status": "HAZARD_INJECTED", "details": result}
