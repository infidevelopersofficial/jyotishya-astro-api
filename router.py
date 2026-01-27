"""
Main Router for Astrology API

Routes requests to either internal calculation engine or FreeAstrologyAPI
based on environment configuration.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from freeastrology.config import get_settings, AstrologyBackend
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Jyotishya Astrology API",
    description="Internal astrology calculation engine with FreeAstrologyAPI fallback",
    version="1.0.0"
)

# Load settings
settings = get_settings()


@app.on_event("startup")
async def startup_event():
    """Log startup configuration"""
    logger.info("=" * 60)
    logger.info("Jyotishya Astrology API Starting")
    logger.info(f"Backend: {settings.astrology_backend.value}")
    logger.info("=" * 60)

    if settings.astrology_backend == AstrologyBackend.INTERNAL:
        logger.info("✅ Using INTERNAL calculation engine (Skyfield)")
        try:
            # Pre-load ephemeris to catch any issues early
            from internal.planetary import _ensure_ephemeris
            _ensure_ephemeris()
            logger.info("✅ Ephemeris data loaded successfully")
        except Exception as e:
            logger.error(f"⚠️  Failed to load ephemeris: {e}")
            logger.error("   API will still start but may fail on first request")

    elif settings.astrology_backend == AstrologyBackend.FREEASTROLOGY:
        logger.info("✅ Using FreeAstrologyAPI.com")
        if not settings.free_api_key:
            logger.warning("⚠️  FREE_API_KEY not set. Requests will fail.")
        else:
            logger.info(f"   API Key configured: {settings.free_api_key[:10]}...")

    else:
        logger.info("✅ Using MOCK data provider")


# Include routes based on backend selection
if settings.astrology_backend == AstrologyBackend.INTERNAL:
    # Use internal calculation engine
    from internal.routes import router as internal_router
    app.include_router(internal_router, tags=["Internal Astrology Engine"])

    @app.get("/")
    async def root():
        return {
            "service": "Jyotishya Astrology API",
            "backend": "internal",
            "version": "1.0.0",
            "endpoints": {
                "birth_chart": "POST /planets",
                "chart_svg": "POST /horoscope-chart-svg-code",
                "health": "GET /health"
            }
        }

elif settings.astrology_backend == AstrologyBackend.FREEASTROLOGY:
    # Proxy to FreeAstrologyAPI
    from freeastrology.main import app as freeastro_app

    # Mount FreeAstrology routes
    @app.get("/")
    async def root():
        return {
            "service": "Jyotishya Astrology API",
            "backend": "freeastrology",
            "version": "1.0.0",
            "proxy": settings.free_api_base_url
        }

    # Delegate all other routes to FreeAstrology proxy
    # This is a simplified approach - in production, you'd want proper route delegation
    logger.info("FreeAstrologyAPI proxy mode - mount freeastrology app")

else:
    # Mock mode
    @app.get("/")
    async def root():
        return {
            "service": "Jyotishya Astrology API",
            "backend": "mock",
            "version": "1.0.0",
            "note": "Using mock data"
        }

    @app.post("/planets")
    async def mock_birth_chart():
        return {
            "message": "Mock mode - no real calculations",
            "planets": []
        }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "backend": settings.astrology_backend.value
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "router:app",
        host="0.0.0.0",
        port=settings.app_port,
        reload=True,
        log_level="info"
    )
