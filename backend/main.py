# FastAPI application entrypoint
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import asyncio
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.core.database import init_db, AsyncSessionLocal
from app.api.router import api_router
from app.services.evidence_cache_service import EvidenceCacheService

async def _background_cache_cleanup():
    async with AsyncSessionLocal() as session:
        try:
            count = await EvidenceCacheService.cleanup_expired_entries(session)
            logger.info(f"Startup cache cleanup deleted {count} expired entries.")
        except Exception as e:
            logger.error(f"Error during startup cache cleanup: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    logger.info(f"Clinical Workstation backend starting — version {settings.app_version}")
    
    # Initialize database
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized.")
    
    # Run cache cleanup in a background task
    asyncio.create_task(_background_cache_cleanup())
    
    # Audit and print all registered routes
    logger.info("Registered routes:")
    for route in app.routes:
        methods = getattr(route, "methods", None)
        methods_str = ", ".join(methods) if methods else "ANY"
        logger.info(f"  {methods_str:12} {route.path}")
        
    logger.info("FastAPI application ready. Health: GET /api/health")
    yield
    
    # Shutdown
    logger.info("Clinical Workstation backend shutting down")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins + ["app://."],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
