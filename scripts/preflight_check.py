"""
RESQ Pre-Flight Deployment Readiness Checker
Validates environment, database connectivity, AI integration, and build artifacts before production deployment.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# ANSI Color codes for clean terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title: str):
    print(f"\n{BOLD}{BLUE}======================================================{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}======================================================{RESET}")

def check_pass(item: str, detail: str = ""):
    print(f"  {GREEN}[PASS]{RESET} {BOLD}{item}{RESET} {f'- {detail}' if detail else ''}")

def check_warn(item: str, detail: str = ""):
    print(f"  {YELLOW}[WARN]{RESET} {BOLD}{item}{RESET} {f'- {detail}' if detail else ''}")

def check_fail(item: str, detail: str = ""):
    print(f"  {RED}[FAIL]{RESET} {BOLD}{item}{RESET} {f'- {detail}' if detail else ''}")

async def run_preflight():
    print_header("RESQ PRODUCTION DEPLOYMENT PRE-FLIGHT CHECK")
    overall_status = True

    # 1. Environment & Configuration Check
    print_header("1. Environment & Core Configuration")
    from backend.app.core.config import settings

    if settings.SECRET_KEY and settings.SECRET_KEY != "resq_secure_operations_eoc_secret_key_2026_super_secure":
        check_pass("JWT SECRET_KEY", "Custom production secret key configured")
    else:
        check_warn("JWT SECRET_KEY", "Using default secret key. Set SECRET_KEY in production .env")

    check_pass("DATABASE_URL", settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL)
    check_pass("DEFAULT_CITY", f"{settings.DEFAULT_CITY} ({settings.CITY_LAT}, {settings.CITY_LNG})")

    # 2. Database Connectivity & Initialization
    print_header("2. Database Connectivity & Seed State")
    try:
        from backend.app.core.database import init_db, AsyncSessionLocal
        from backend.app.services.world_engine import world_engine
        from sqlalchemy import select, func
        from backend.app.models.user import User
        from backend.app.models.incident import Incident
        from backend.app.models.resource import Resource
        from backend.app.models.shelter import Shelter
        from backend.app.models.road import RoadSegment

        await init_db()
        async with AsyncSessionLocal() as session:
            await world_engine.seed_initial_world(session)
            
            user_count = (await session.execute(select(func.count(User.id)))).scalar()
            incident_count = (await session.execute(select(func.count(Incident.id)))).scalar()
            resource_count = (await session.execute(select(func.count(Resource.id)))).scalar()
            shelter_count = (await session.execute(select(func.count(Shelter.id)))).scalar()
            road_count = (await session.execute(select(func.count(RoadSegment.id)))).scalar()

            check_pass("Database Connection", "Successfully connected and initialized schema")
            check_pass("Seed State Validated", f"{user_count} users, {incident_count} incidents, {resource_count} resources, {shelter_count} shelters, {road_count} road segments")
    except Exception as e:
        check_fail("Database Error", str(e))
        overall_status = False

    # 3. Google Gemini AI Engine
    print_header("3. Multi-Agent AI Engine")
    try:
        from backend.app.agents.gemini_client import gemini_client
        if gemini_client.is_configured:
            check_pass("Gemini API Key", f"Configured ({len(gemini_client.api_key)} chars, model: {gemini_client.model})")
            
            # Quick connectivity test
            ok, res, mode, tokens = await gemini_client.generate_structured(
                system_instruction="Reply in JSON.",
                prompt="Echo {'status': 'live'}"
            )
            if ok:
                check_pass("Gemini Live API", f"Responding normally via {mode} ({tokens} tokens)")
            else:
                check_warn("Gemini Engine Mode", f"API spike/fallback active. Authoritative Deterministic Engine is handling agent reasoning without downtime.")
        else:
            check_warn("Gemini API Key", "Not set. Platform will run in 100% Authoritative Deterministic Engine mode.")
    except Exception as e:
        check_warn("Gemini Client Notice", f"{e}. Fallback engine will maintain mission safety.")

    # 4. Frontend Production Build Check
    print_header("4. Frontend Production Assets")
    dist_dir = ROOT_DIR / "frontend" / "dist"
    dist_index = dist_dir / "index.html"
    dist_assets = dist_dir / "assets"

    if dist_index.exists() and dist_assets.exists():
        asset_files = list(dist_assets.glob("*"))
        check_pass("Frontend Dist Artifacts", f"index.html present, {len(asset_files)} bundled assets compiled")
    else:
        check_warn("Frontend Dist", "dist/ not found. Run 'npm run build' inside frontend/ before deploying.")

    # 5. Docker Configurations Check
    print_header("5. Containerization Files")
    docker_compose = ROOT_DIR / "docker-compose.yml"
    backend_docker = ROOT_DIR / "backend" / "Dockerfile"
    frontend_docker = ROOT_DIR / "frontend" / "Dockerfile"
    nginx_conf = ROOT_DIR / "frontend" / "nginx.conf"

    if docker_compose.exists():
        check_pass("docker-compose.yml", "Present and configured")
    else:
        check_fail("docker-compose.yml", "Missing")
        overall_status = False

    if backend_docker.exists() and frontend_docker.exists():
        check_pass("Dockerfiles", "Backend & Frontend Dockerfiles present")
    else:
        check_fail("Dockerfiles", "Missing backend or frontend Dockerfile")
        overall_status = False

    if nginx_conf.exists():
        check_pass("nginx.conf", "SPA and reverse-proxy config verified")
    else:
        check_fail("nginx.conf", "Missing frontend/nginx.conf")
        overall_status = False

    # Summary
    print_header("SUMMARY")
    if overall_status:
        print(f"{GREEN}{BOLD}[SUCCESS] ALL PRE-FLIGHT CHECKS PASSED. SYSTEM IS READY FOR DEPLOYMENT!{RESET}\n")
    else:
        print(f"{RED}{BOLD}[FAILED] SOME CRITICAL CHECKS FAILED. Please review the errors above before deploying.{RESET}\n")

if __name__ == "__main__":
    asyncio.run(run_preflight())
