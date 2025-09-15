"""
FBS FastAPI Implementation Example

This file demonstrates how to integrate FBS FastAPI into your solution.
Copy relevant parts to your application and customize as needed.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
import uvicorn
import logging

# ============================================================================
# FBS FASTAPI IMPORTS
# ============================================================================

from fbs_fastapi.services.service_interfaces import FBSInterface
from fbs_fastapi.core.config import FBSConfig, config
from fbs_fastapi.core.database import create_tables
from fbs_fastapi.core.middleware import DatabaseRoutingMiddleware

# ============================================================================
# YOUR SOLUTION CONFIGURATION
# ============================================================================

class YourSolutionConfig(FBSConfig):
    """Custom configuration for your solution"""

    # Override defaults for your needs
    app_name: str = "Your Solution - Powered by FBS"
    app_version: str = "1.0.0"

    # Your custom settings
    your_custom_setting: str = "default_value"

# Create your configuration instance
your_config = YourSolutionConfig()

# ============================================================================
# FBS INITIALIZATION
# ============================================================================

# Initialize FBS Interface for your solution
fbs = FBSInterface(
    solution_name="your_solution_name",
    license_key=None  # Use None for unlimited access, or provide license key
)

# ============================================================================
# FASTAPI APPLICATION SETUP
# ============================================================================

app = FastAPI(
    title=your_config.app_name,
    description="Your business solution powered by FBS FastAPI",
    version=your_config.app_version,
    debug=your_config.debug,
    docs_url="/docs" if your_config.debug else None,
    redoc_url="/redoc" if your_config.debug else None,
)

# ============================================================================
# MIDDLEWARE SETUP
# ============================================================================

# CORS middleware (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=your_config.cors_origins_list,
    allow_credentials=your_config.cors_allow_credentials,
    allow_methods=your_config.cors_methods_list,
    allow_headers=your_config.cors_headers_list,
)

# FBS custom middleware
app.add_middleware(DatabaseRoutingMiddleware)

# ============================================================================
# SECURITY SETUP (Optional - extend FBS auth)
# ============================================================================

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Custom authentication dependency"""
    # You can integrate with FBS auth or use your own
    token = credentials.credentials

    # Example: Validate with FBS
    # token_valid = await fbs.auth.validate_token_mapping(token, "your_solution")
    # if not token_valid["valid"]:
    #     raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": "example_user", "token": token}

# ============================================================================
# FBS ROUTER INTEGRATION
# ============================================================================

# Include core FBS business functionality
from fbs_fastapi.routers.business import router as business_router
app.include_router(
    business_router,
    prefix="/api/business",
    tags=["Business Management"],
    dependencies=[Depends(get_current_user)]  # Optional: Add auth
)

# Include DMS if enabled
if your_config.enable_dms_features:
    from fbs_fastapi.routers.dms import router as dms_router
    app.include_router(
        dms_router,
        prefix="/api/dms",
        tags=["Document Management"],
        dependencies=[Depends(get_current_user)]
    )

# Include licensing if enabled
if your_config.enable_licensing_features:
    from fbs_fastapi.routers.license import router as license_router
    app.include_router(
        license_router,
        prefix="/api/license",
        tags=["License Management"]
    )

# Include module generation if enabled
if your_config.enable_module_generation:
    from fbs_fastapi.routers.module_gen import router as module_gen_router
    app.include_router(
        module_gen_router,
        prefix="/api/module",
        tags=["Module Generation"],
        dependencies=[Depends(get_current_user)]
    )

# ============================================================================
# YOUR CUSTOM ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Your custom root endpoint"""
    return {
        "message": f"Welcome to {your_config.app_name}",
        "version": your_config.app_version,
        "powered_by": "FBS FastAPI v3.1.0",
        "docs": "/docs" if your_config.debug else None,
        "health": "/health"
    }

@app.get("/api/your-custom-endpoint")
async def your_custom_endpoint(user: Dict[str, Any] = Depends(get_current_user)):
    """Example custom endpoint that uses FBS services"""

    # Use FBS business service
    try:
        dashboard_data = await fbs.msme.get_dashboard()
    except Exception as e:
        dashboard_data = {"error": f"Dashboard unavailable: {str(e)}"}

    # Your custom logic
    custom_data = {
        "user_id": user["user_id"],
        "timestamp": "2024-01-01T00:00:00Z",
        "your_business_logic": "implemented_here"
    }

    return {
        "success": True,
        "data": {
            **custom_data,
            "fbs_dashboard": dashboard_data
        }
    }

@app.post("/api/create-business")
async def create_business_endpoint(
    business_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user)
):
    """Create new business using FBS MSME service"""

    try:
        # Use FBS to create business
        result = await fbs.msme.setup_business(
            business_type=business_data.get("type", "general"),
            config={
                **business_data,
                "created_by": user["user_id"],
                "solution_name": "your_solution_name"
            }
        )

        return {
            "success": True,
            "message": "Business created successfully",
            "data": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create business: {str(e)}"
        )

@app.get("/api/odoo-models")
async def get_odoo_models(user: Dict[str, Any] = Depends(get_current_user)):
    """Get available Odoo models using FBS discovery"""

    try:
        models = await fbs.discovery.discover_models("your_solution")
        return {
            "success": True,
            "models": models
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to discover Odoo models: {str(e)}"
        )

# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logging.info(f"🚀 Starting {your_config.app_name} v{your_config.app_version}")

    # Initialize FBS database tables
    try:
        await create_tables()
        logging.info("✅ Database tables ready")
    except Exception as e:
        logging.warning(f"⚠️ Database initialization failed: {e}")
        logging.info("ℹ️ Application will start without database connectivity")

    # Log FBS capabilities
    solution_info = await fbs.get_solution_info()
    logging.info(f"📋 FBS Solution Info: {solution_info}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logging.info(f"🛑 Shutting down {your_config.app_name}")

# ============================================================================
# HEALTH CHECKS
# ============================================================================

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": your_config.app_name,
        "version": your_config.app_version,
        "fbs_version": "3.1.0",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with FBS status"""

    # Get FBS health
    fbs_health = await fbs.get_system_health()

    # Your custom health checks
    custom_health = {
        "custom_service": {
            "status": "healthy",
            "message": "Your custom service is operational"
        }
    }

    return {
        "status": "healthy" if fbs_health["status"] == "healthy" else "degraded",
        "service": your_config.app_name,
        "version": your_config.app_version,
        "components": {
            **fbs_health.get("services", {}),
            **custom_health
        },
        "fbs_license": await fbs.get_license_info()
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logging.error(f"Unhandled error: {exc}", exc_info=True)

    return {
        "success": False,
        "error": "Internal server error",
        "message": str(exc) if your_config.debug else "An unexpected error occurred"
    }

# ============================================================================
# DEVELOPMENT HELPERS
# ============================================================================

if your_config.debug:
    @app.get("/debug/config")
    async def debug_config():
        """Debug endpoint to view configuration"""
        return {
            "app_config": {
                "name": your_config.app_name,
                "version": your_config.app_version,
                "debug": your_config.debug
            },
            "fbs_config": {
                "solution_name": fbs.solution_name,
                "fastapi_db": fbs.fastapi_db_name,
                "odoo_db": fbs.odoo_db_name,
                "license_available": fbs._licensing_available
            },
            "database": your_config.database_url.replace(
                your_config.database_url.split('@')[0].split('//')[1], "***"
            ),
            "odoo": your_config.odoo_base_url,
            "features": {
                "msme": your_config.enable_msme_features,
                "dms": your_config.enable_dms_features,
                "bi": your_config.enable_bi_features,
                "workflows": your_config.enable_workflow_features,
                "compliance": your_config.enable_compliance_features,
                "module_generation": your_config.enable_module_generation,
            }
        }

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Development server configuration
    uvicorn.run(
        "main:app",  # This file is main.py
        host="0.0.0.0",
        port=8000,
        reload=your_config.debug,
        reload_dirs=["."],
        log_level=your_config.log_level.lower()
    )

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
USAGE EXAMPLES:

1. Start the server:
   python main.py

2. Access API documentation:
   http://localhost:8000/docs

3. Test FBS integration:
   GET http://localhost:8000/health/detailed

4. Create a business:
   POST http://localhost:8000/api/create-business
   {
     "name": "My Business",
     "type": "retail",
     "industry": "ecommerce"
   }

5. Get Odoo models:
   GET http://localhost:8000/api/odoo-models

6. Use FBS services directly in your code:
   dashboard = await fbs.msme.get_dashboard()
   models = await fbs.discovery.discover_models("your_solution")

7. Debug configuration:
   GET http://localhost:8000/debug/config
"""

# ============================================================================
# ENVIRONMENT VARIABLES EXAMPLE
# ============================================================================

"""
Create a .env file with:

# Application
APP_NAME=Your Solution - Powered by FBS
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/fpi_your_solution_db

# Odoo Integration
ODOO_BASE_URL=http://localhost:8069
ODOO_USER=odoo
ODOO_PASSWORD=your_password

# Features
ENABLE_MSME_FEATURES=true
ENABLE_DMS_FEATURES=true
ENABLE_MODULE_GENERATION=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# ============================================================================
# INTEGRATED WORKFLOWS - DISCOVERY + MODULE GENERATION
# ============================================================================

INTEGRATED_WORKFLOWS_NOTES = '''
FBS FastAPI v3.1.0 - INTEGRATED WORKFLOWS

What was fixed:
- ❌ Discovery and Module Generation were independent alternatives
- ❌ Different database naming conventions
- ❌ No workflow connecting exploration to implementation

What is now integrated:
- ✅ Unified database naming (fbs_{solution}_db, fpi_{solution}_db)
- ✅ Discovery informs Module Generation
- ✅ Integrated workflows combining both approaches
- ✅ Hybrid extension workflows

Integrated Workflow Examples:

1. DISCOVER & EXTEND WORKFLOW:
POST /api/fbs/discover-and-extend
{
  "user_id": "developer@example.com",
  "tenant_id": "my_solution"
}
// Result: Discovers models → Generates extensions → Installs modules

2. HYBRID EXTENSION WORKFLOW:
POST /api/fbs/hybrid-extension
{
  "base_model": "res.partner",
  "custom_fields": [
    {"name": "loyalty_points", "type": "integer"},
    {"name": "vip_status", "type": "boolean"}
  ],
  "user_id": "developer@example.com"
}
// Result: Adds virtual fields immediately + generates structured module

3. DISCOVERY-INFORMED GENERATION:
const findings = await fbs.discovery.discover_models();
const modules = await fbs.module_gen.generate_from_discovery(findings, userId, tenantId);
'''

# ============================================================================
# INHERITANCE DEMONSTRATION - RESTORED FROM ORIGINAL MOD_GEN
# ============================================================================

PURE_BACKEND_MODULES_NOTES = '''
FBS FastAPI v3.1.0 - PURE BACKEND MODULES SUPPORT

What was fixed:
- ❌ Manifest always included views (even when not needed)
- ❌ Views generated unconditionally

What is now supported:
- ✅ Conditional manifest generation (no views for backend-only modules)
- ✅ Pure backend modules without XML views
- ✅ Clean separation of backend logic from frontend presentation

Pure Backend Module Example:
POST /api/module-gen/generate
{
  "name": "business_logic_only",
  "description": "Pure backend module for React frontend",
  "models": [{
    "name": "business.processor",
    "description": "Business logic processor",
    "fields": [
      {"name": "input_data", "type": "text"},
      {"name": "processed_result", "type": "text"},
      {"name": "status", "type": "selection", "selection": "[('pending','Pending'),('done','Done')]"}
    ],
    "methods": [{
      "name": "process_data",
      "body": "self.processed_result = self._process_business_logic(self.input_data); self.status = 'done'"
    }]
  }],
  "security": {
    "rules": [{
      "name": "API Access",
      "model": "business.processor",
      "permissions": ["read", "write", "create"]
    }]
  }
  // Note: No "views" key - pure backend!
}

Generated Manifest (No views!):
{
    'name': 'Business Logic Only',
    'version': '1.0.0',
    'depends': ['base'],
    'data': ['security/ir.model.access.csv'],  // Only security, no views!
    'installable': True,
    'application': False,
}

React Integration:
const processData = async (inputData) => {
    // Call FBS API (which uses the pure backend module)
    const response = await fetch('/api/odoo/business.processor/create', {
        method: 'POST',
        body: JSON.stringify({data: {input_data: inputData}})
    });
    return await response.json();
};
'''

INHERITANCE_RESTORATION_NOTES = '''
FBS FastAPI v3.1.0 - INHERITANCE SUPPORT RESTORED

What was lost during migration:
- ❌ _inherit field support in ModuleSpec
- ❌ Model inheritance generation
- ❌ Clean extension patterns

What has been restored:
- ✅ inherit_from field in ModuleSpec
- ✅ _inherit generation in model classes
- ✅ Extension inheritance patterns
- ✅ Clean inheritance from existing Odoo models

Example Usage:
POST /api/module-gen/generate
{
  "name": "rental_tenant",
  "models": [{
    "name": "rental.tenant",
    "inherit_from": "res.partner",  // ← This works again!
    "fields": [
      {"name": "tenant_id", "type": "char"},
      {"name": "credit_score", "type": "integer"}
    ]
  }]
}

Generated Output:
class RentalTenant(models.Model):
    _name = 'rental.tenant'
    _inherit = 'res.partner'  # ← Clean inheritance!
    _description = 'Rental Tenant'

    tenant_id = fields.Char('Tenant ID')
    credit_score = fields.Integer('Credit Score')
'''
"""
