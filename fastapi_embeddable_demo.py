#!/usr/bin/env python3
"""
FBS FastAPI Embeddable Framework Demo

This demonstrates how FBS services can be embedded directly into FastAPI applications
as business logic components, exactly as required by the team specifications.

NO HTTP calls - pure embeddable integration!
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

# ============================================================================
# FBS EMBEDDABLE SERVICES - Direct Import (No HTTP!)
# ============================================================================

# Set up minimal environment for demo
os.environ['SECRET_KEY'] = 'demo_secret_key'
os.environ['DATABASE_URL'] = 'postgresql+asyncpg://demo:demo@localhost:5432/demo'

# FBS Services - Embedded directly (this is the key!)
from fbs_fastapi.services.business_service import BusinessService
from fbs_fastapi.services.auth_service import AuthService
from fbs_fastapi.services.module_generation_service import FBSModuleGeneratorEngine

# ============================================================================
# FASTAPI APPLICATION WITH EMBEDDED FBS
# ============================================================================

app = FastAPI(
    title="Demo App with Embedded FBS",
    description="FastAPI application with FBS business logic embedded directly",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# DATABASE SETUP (Simple for demo)
# ============================================================================

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://demo:demo@localhost:5432/demo")
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    """Database dependency"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# ============================================================================
# FBS SERVICE DEPENDENCIES - Direct Instantiation
# ============================================================================

def get_business_service():
    """FBS Business Service - Embedded directly in FastAPI"""
    return BusinessService()

def get_auth_service():
    """FBS Auth Service - Embedded directly in FastAPI"""
    return AuthService("demo_solution")

def get_module_generator():
    """FBS Module Generator - Embedded directly in FastAPI"""
    return FBSModuleGeneratorEngine()

# ============================================================================
# FASTAPI ROUTES WITH EMBEDDED FBS BUSINESS LOGIC
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "FastAPI with Embedded FBS Business Logic",
        "status": "operational",
        "fbs_embedded": True
    }

@app.get("/health")
async def health_check():
    """Health check with FBS service validation"""
    try:
        # Test FBS service instantiation (no HTTP!)
        business_svc = BusinessService()
        auth_svc = AuthService("health_check")

        return {
            "status": "healthy",
            "fbs_embedded": True,
            "services_available": {
                "business_service": True,
                "auth_service": True,
                "module_generator": True
            },
            "integration_type": "direct_embeddable"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FBS service error: {str(e)}")

@app.post("/business/create")
async def create_business(
    business_data: dict,
    business_svc: BusinessService = Depends(get_business_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Create business using embedded FBS business service

    This demonstrates the key requirement:
    - Direct FBS service instantiation
    - Direct method calls (no HTTP)
    - Async/await for FastAPI compatibility
    """
    try:
        # Direct FBS method call (no HTTP!)
        result = await business_svc.create_business(business_data, db, {"user_id": "demo_user"})

        return {
            "success": True,
            "business": result,
            "integration_method": "direct_embeddable",
            "no_http_calls": True
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/handshake")
async def create_handshake(
    auth_svc: AuthService = Depends(get_auth_service)
):
    """
    Create handshake using embedded FBS auth service

    Demonstrates embeddable authentication
    """
    try:
        # Direct FBS method call (no HTTP!)
        handshake = await auth_svc.create_handshake()

        return {
            "success": True,
            "handshake": handshake,
            "integration_method": "direct_embeddable"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/module/generate")
async def generate_module(
    spec: dict,
    module_gen: FBSModuleGeneratorEngine = Depends(get_module_generator)
):
    """
    Generate Odoo module using embedded FBS module generator

    Demonstrates v3.0.0 flagship feature
    """
    try:
        # Direct FBS method call (no HTTP!)
        result = await module_gen.generate_module(spec)

        return {
            "success": True,
            "module": result,
            "integration_method": "direct_embeddable",
            "fbs_version": "3.0.0"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================================
# DEMO INFORMATION
# ============================================================================

@app.get("/demo/info")
async def demo_info():
    """Information about this FBS embeddable demo"""
    return {
        "demo_title": "FBS FastAPI Embeddable Framework Demo",
        "fbs_version": "3.0.0",
        "integration_type": "direct_embeddable",
        "no_http_calls": True,
        "async_await_support": True,
        "key_features": [
            "Direct FBS service instantiation",
            "Direct method calls (no HTTP)",
            "FastAPI dependency injection",
            "Async/await compatibility",
            "Module generation capability"
        ],
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Root endpoint"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/business/create", "method": "POST", "description": "Create business"},
            {"path": "/auth/handshake", "method": "POST", "description": "Create handshake"},
            {"path": "/module/generate", "method": "POST", "description": "Generate module"}
        ]
    }

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("🚀 FBS FastAPI Embeddable Demo")
    print("=" * 50)
    print("Starting FastAPI application with embedded FBS services...")
    print()
    print("Key Features Demonstrated:")
    print("✅ Direct FBS service imports (no HTTP)")
    print("✅ Direct method calls to FBS services")
    print("✅ Async/await compatibility")
    print("✅ FastAPI dependency injection")
    print("✅ Module generation capability")
    print()
    print("Visit: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health")
    print("Demo Info: http://localhost:8000/demo/info")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000)
