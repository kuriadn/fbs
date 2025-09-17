"""
FBS FastAPI Application

Main entry point for the FBS FastAPI application.
ASGI application with complete middleware stack and routing.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.config import config
from core.database import create_tables, check_database_health
from core.middleware import DatabaseRoutingMiddleware, RequestLoggingMiddleware

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format=config.log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('fbs_fastapi.log') if not config.debug else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    logger.info("🚀 Starting FBS FastAPI application...")

    # Startup tasks
    try:
        # Try to create database tables (skip if database not available)
        try:
            await create_tables()
            logger.info("✅ Database tables created/verified")
        except Exception as db_error:
            logger.warning(f"⚠️  Database not available, skipping table creation: {db_error}")
            logger.info("ℹ️  Application will start without database connectivity")

        # Log configuration
        logger.info(f"📋 Configuration loaded: {config.app_name} v{config.app_version}")
        logger.info(f"🗄️  Database: {config.database_url.split('/')[-1]}")
        logger.info(f"🔗 Odoo: {config.odoo_base_url}")
        logger.info(f"⚙️  Debug mode: {config.debug}")

    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        # Don't raise error - allow app to start without full functionality
        logger.warning("⚠️  Application starting with reduced functionality")

    yield

    # Shutdown tasks
    logger.info("🛑 Shutting down FBS FastAPI application...")

# Create FastAPI application
app = FastAPI(
    title=config.app_name,
    description="Fayvad Business Suite - Modernized with FastAPI",
    version=config.app_version,
    debug=config.debug,
    lifespan=lifespan,
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
    openapi_url="/openapi.json" if config.debug else None,
)

# ============================================================================
# MIDDLEWARE SETUP
# ============================================================================

# CORS middleware (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins_list,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=config.cors_methods_list,
    allow_headers=config.cors_headers_list,
)

# Custom middleware
app.add_middleware(DatabaseRoutingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# ============================================================================
# ROUTER INCLUDES
# ============================================================================

# Health check endpoints (always available)
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": config.app_name,
        "version": config.app_version,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health/detailed")
async def health_check_detailed():
    """Detailed health check with component status"""
    health_status = {
        "status": "healthy",
        "service": config.app_name,
        "version": config.app_version,
        "components": {}
    }

    # Check database health
    try:
        db_health = await check_database_health()
        health_status["components"]["database"] = db_health
        if db_health["status"] != "healthy":
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    # Check Odoo connectivity
    try:
        # Implement Odoo health check
        try:
            from .services.odoo_service import OdooService
            odoo_service = OdooService("system")
            # Try a simple Odoo connection test
            test_result = await odoo_service.health_check()
            health_status["components"]["odoo"] = {
                "status": "healthy" if test_result.get('status') == 'healthy' else "unhealthy",
                "message": test_result.get('message', 'Odoo connection test completed'),
                "details": test_result
            }
        except Exception as e:
            health_status["components"]["odoo"] = {
                "status": "unhealthy",
                "message": f"Odoo health check failed: {str(e)}"
            }
    except Exception as e:
        health_status["components"]["odoo"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Check cache (Redis)
    try:
        # Implement Redis health check
        try:
            redis_url = getattr(config, 'redis_url', None)
            if redis_url:
                import redis
                redis_client = redis.from_url(redis_url)
                redis_client.ping()
                health_status["components"]["cache"] = {
                    "status": "healthy",
                    "message": "Redis cache connection successful"
                }
            else:
                health_status["components"]["cache"] = {
                    "status": "healthy",
                    "message": "Using in-memory cache (Redis not configured)"
                }
        except Exception as e:
            health_status["components"]["cache"] = {
                "status": "unhealthy",
                "message": f"Cache health check failed: {str(e)}"
            }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    return health_status

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to FBS FastAPI",
        "service": config.app_name,
        "version": config.app_version,
        "docs": "/docs" if config.debug else None,
        "health": "/health",
        "status": "operational"
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if config.debug else "An unexpected error occurred"
        }
    )

# ============================================================================
# CONDITIONAL ROUTER INCLUDES
# ============================================================================

# Include FBS v3 business routes
try:
    from .routers.business import router as business_router
    app.include_router(business_router, prefix="/api/business", tags=["Business Management"])
    logger.info("✅ Business routes loaded")
except ImportError as e:
    logger.warning(f"⚠️  Business routes not loaded: {e}")

# Include DMS routes
if config.enable_dms_features:
    try:
        from .routers.dms import router as dms_router
        app.include_router(dms_router, prefix="/api/dms", tags=["Document Management"])
        logger.info("✅ DMS routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️  DMS routes not loaded: {e}")

# Include licensing routes
if config.enable_licensing_features:
    try:
        from .routers.license import router as license_router
        app.include_router(license_router, prefix="/api/license", tags=["License Management"])
        logger.info("✅ License routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️  Licensing routes not loaded: {e}")

# Include module generation routes
if config.enable_module_generation:
    try:
        from .routers.module_gen import router as module_gen_router
        app.include_router(module_gen_router, prefix="", tags=["Module Generation"])
        logger.info("✅ Module generation routes loaded")
    except ImportError as e:
        logger.warning(f"⚠️  Module generation routes not loaded: {e}")

# ============================================================================
# DEVELOPMENT HELPERS
# ============================================================================

if config.debug:
    @app.get("/debug/config")
    async def debug_config():
        """Debug endpoint to view current configuration"""
        return {
            "app_name": config.app_name,
            "version": config.app_version,
            "debug": config.debug,
            "database_url": config.database_url.replace(config.database_url.split('@')[0].split('//')[1], "***"),
            "odoo_base_url": config.odoo_base_url,
            "cors_origins": config.cors_origins,
            "feature_flags": {
                "msme": config.enable_msme_features,
                "bi": config.enable_bi_features,
                "workflow": config.enable_workflow_features,
                "compliance": config.enable_compliance_features,
                "accounting": config.enable_accounting_features,
                "dms": config.enable_dms_features,
                "licensing": config.enable_licensing_features,
            }
        }

# Export the app for ASGI server
__all__ = ["app"]

# For development server
if __name__ == "__main__":
    import uvicorn

    logger.info("🟡 Starting development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=config.debug,
        reload_dirs=["."],
        log_level=config.log_level.lower()
    )
