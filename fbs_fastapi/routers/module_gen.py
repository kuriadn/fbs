"""
FBS Module Generation Router

FastAPI router for module generation endpoints with FBS integration.
Provides secure, licensed, and tenant-aware module generation capabilities.
"""

import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

from core.dependencies import get_current_user, get_db_session_for_request
from services.module_generation_service import module_generation_service
from core.config import config

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/module-gen", tags=["Module Generation"])


# Pydantic models for request/response
class ModuleFieldSpec(BaseModel):
    name: str = Field(..., description="Field name")
    type: str = Field(..., description="Field type (char, text, integer, float, boolean, date, datetime, selection, many2one, one2many, many2many)")
    string: Optional[str] = Field(None, description="Display name")
    required: Optional[bool] = Field(False, description="Is field required")
    help: Optional[str] = Field(None, description="Help text")
    default: Optional[Any] = Field(None, description="Default value")
    selection: Optional[Dict[str, str]] = Field(None, description="Selection options for selection fields")
    comodel: Optional[str] = Field(None, description="Related model for relational fields")
    relation: Optional[str] = Field(None, description="Legacy relation field")


class ModuleModelSpec(BaseModel):
    name: str = Field(..., description="Model name (e.g., 'my.module')")
    description: Optional[str] = Field(None, description="Model description")
    inherit_from: Optional[str] = Field(None, description="Inherit from existing Odoo model (e.g., 'res.partner')")
    fields: List[ModuleFieldSpec] = Field(default_factory=list, description="Model fields")
    methods: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Custom methods")


class ModuleWorkflowSpec(BaseModel):
    model: str = Field(..., description="Model this workflow applies to")
    states: List[Dict[str, Any]] = Field(..., description="Workflow states")
    actions: List[Dict[str, Any]] = Field(..., description="Workflow actions")


class ModuleViewSpec(BaseModel):
    model: str = Field(..., description="Model for the view")
    type: str = Field(..., description="View type (form, tree, kanban, etc.)")
    fields: Optional[List[str]] = Field(None, description="Fields to include in view")


class ModuleSecuritySpec(BaseModel):
    groups: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Security groups")
    rules: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Record rules")


class ModuleSpec(BaseModel):
    name: str = Field(..., description="Module name (e.g., 'my_custom_module')")
    description: str = Field(..., description="Module description")
    author: str = Field(..., description="Module author")
    version: Optional[str] = Field("1.0.0", description="Module version")
    category: Optional[str] = Field("Custom", description="Module category")
    depends: Optional[List[str]] = Field(default_factory=lambda: ["base"], description="Module dependencies")
    models: Optional[List[ModuleModelSpec]] = Field(default_factory=list, description="Module models")
    workflows: Optional[List[ModuleWorkflowSpec]] = Field(default_factory=list, description="Module workflows")
    views: Optional[List[ModuleViewSpec]] = Field(None, description="Module views (optional - omit for pure backend modules)")
    security: Optional[ModuleSecuritySpec] = Field(None, description="Module security configuration")


class ModuleTemplateResponse(BaseModel):
    name: str
    description: str
    category: str
    models_count: int
    has_workflow: bool
    is_active: bool = True


class ValidationResponse(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]


class GenerationResponse(BaseModel):
    success: bool
    module_name: str
    files_count: int
    zip_size: int
    dms_reference: str
    generation_time: str
    tenant_id: str
    message: str


class InstallationResponse(BaseModel):
    success: bool
    module_name: str
    installation_status: str
    odoo_module_id: Optional[int] = None
    message: str


# Routes
@router.get("/templates", response_model=List[ModuleTemplateResponse])
async def list_templates(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    List available module generation templates

    GET /api/module-gen/templates
    """
    try:
        tenant_id = current_user.get('tenant_id', 'default')
        templates = await module_generation_service.list_templates(tenant_id)

        return [
            ModuleTemplateResponse(
                name=template['name'],
                description=template['description'],
                category=template['category'],
                models_count=template['models_count'],
                has_workflow=template['has_workflow']
            )
            for template in templates
        ]

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to list templates")


@router.post("/validate", response_model=ValidationResponse)
async def validate_specification(
    spec: ModuleSpec,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate module specification without generating

    POST /api/module-gen/validate
    """
    try:
        spec_dict = spec.dict()
        result = await module_generation_service.validate_specification(spec_dict)

        return ValidationResponse(**result)

    except Exception as e:
        logger.error(f"Error validating specification: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate specification")


@router.post("/validate-installation", response_model=ValidationResponse)
async def validate_installation_request(
    spec: ModuleSpec,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Validate if a module installation request is valid

    POST /api/module-gen/validate-installation
    """
    try:
        # Check if module generation is enabled
        if not config.enable_module_generation:
            raise HTTPException(403, "Module generation is not enabled")

        tenant_id = current_user.get('tenant_id', 'default')

        # Validate specification first
        spec_dict = spec.dict()
        validation_result = await module_generation_service.validate_specification(spec_dict)

        if not validation_result['valid']:
            return ValidationResponse(**validation_result)

        # Check license and permissions
        # This would integrate with FBS license service
        license_valid = True  # Placeholder - would check actual license

        if not license_valid:
            return ValidationResponse(
                valid=False,
                errors=["Module generation license not valid"],
                warnings=[]
            )

        # Validate Odoo connectivity (if needed)
        # This would test connection to tenant's Odoo instance

        return ValidationResponse(
            valid=True,
            errors=[],
            warnings=[]
        )

    except Exception as e:
        logger.error(f"Error validating installation request: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate installation request")


@router.post("/generate", response_model=GenerationResponse)
async def generate_module(
    spec: ModuleSpec,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate Odoo module from specification

    POST /api/module-gen/generate
    """
    try:
        # Check if module generation is enabled
        if not config.enable_module_generation:
            raise HTTPException(403, "Module generation is not enabled")

        user_id = current_user.get('id', 'unknown')
        tenant_id = current_user.get('tenant_id', 'default')

        spec_dict = spec.dict()
        result = await module_generation_service.generate_module(spec_dict, user_id, tenant_id)

        # Log the generation activity
        background_tasks.add_task(
            _log_module_generation_activity,
            user_id=user_id,
            tenant_id=tenant_id,
            module_name=spec.name,
            activity_type="generate",
            success=True,
            request=request
        )

        return GenerationResponse(
            success=True,
            module_name=result['module_name'],
            files_count=result['files_count'],
            zip_size=result['zip_size'],
            dms_reference=result['dms_reference'],
            generation_time=result['generation_time'],
            tenant_id=result['tenant_id'],
            message="Module generated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating module: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate module")


@router.post("/generate-and-install", response_model=InstallationResponse)
async def generate_and_install_module(
    spec: ModuleSpec,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate module and install in tenant's Odoo instance

    POST /api/module-gen/generate-and-install
    """
    try:
        # Check if module generation is enabled
        if not config.enable_module_generation:
            raise HTTPException(403, "Module generation is not enabled")

        user_id = current_user.get('id', 'unknown')
        tenant_id = current_user.get('tenant_id', 'default')

        spec_dict = spec.dict()
        result = await module_generation_service.generate_and_install(spec_dict, user_id, tenant_id)

        # Log the generation and installation activity
        background_tasks.add_task(
            _log_module_generation_activity,
            user_id=user_id,
            tenant_id=tenant_id,
            module_name=spec.name,
            activity_type="generate_and_install",
            success=True,
            request=request
        )

        return InstallationResponse(
            success=True,
            module_name=result['module_name'],
            installation_status="completed",
            odoo_module_id=result.get('installation', {}).get('odoo_module_id'),
            message="Module generated and installed successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating and installing module: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate and install module")


@router.get("/generated")
async def list_generated_modules(
    request: Request,
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """
    List generated modules for current tenant

    GET /api/module-gen/generated?skip=0&limit=50
    """
    try:
        tenant_id = current_user.get('tenant_id', 'default')

        async for db in get_db_session_for_request(None):
            from models.models import GeneratedModule

            query = db.query(GeneratedModule).filter(GeneratedModule.tenant_id == tenant_id)
            total = query.count()
            modules = query.offset(skip).limit(limit).all()

            return {
                "total": total,
                "modules": [
                    {
                        "id": str(module.id),
                        "module_name": module.module_name,
                        "version": module.version,
                        "category": module.category,
                        "description": module.description,
                        "generation_time": module.generation_time.isoformat(),
                        "is_installed": module.is_installed,
                        "files_count": module.files_count,
                        "zip_size": module.zip_size,
                        "dms_reference": module.dms_reference
                    }
                    for module in modules
                ]
            }

    except Exception as e:
        logger.error(f"Error listing generated modules: {e}")
        raise HTTPException(status_code=500, detail="Failed to list generated modules")


@router.get("/history")
async def get_generation_history(
    request: Request,
    current_user: dict = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """
    Get module generation history for current tenant

    GET /api/module-gen/history?skip=0&limit=50
    """
    try:
        tenant_id = current_user.get('tenant_id', 'default')

        async for db in get_db_session_for_request(None):
            from models.models import ModuleGenerationHistory

            query = db.query(ModuleGenerationHistory).filter(ModuleGenerationHistory.tenant_id == tenant_id)
            total = query.count()
            history = query.order_by(ModuleGenerationHistory.generation_time.desc()).offset(skip).limit(limit).all()

            return {
                "total": total,
                "history": [
                    {
                        "id": str(entry.id),
                        "module_name": entry.module_name,
                        "activity_type": entry.activity_type,
                        "generation_time": entry.generation_time.isoformat(),
                        "success": entry.success,
                        "spec_summary": entry.spec_summary,
                        "processing_time_ms": entry.processing_time_ms,
                        "error_message": entry.error_message
                    }
                    for entry in history
                ]
            }

    except Exception as e:
        logger.error(f"Error getting generation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get generation history")


# Helper functions
async def _log_module_generation_activity(
    user_id: str,
    tenant_id: str,
    module_name: str,
    activity_type: str,
    success: bool,
    request: Request
):
    """Log module generation activity asynchronously"""
    try:
        async for db in get_db_session_for_request(None):
            from models.models import ModuleGenerationHistory

            log_entry = ModuleGenerationHistory(
                module_name=module_name,
                user_id=user_id,
                tenant_id=tenant_id,
                activity_type=activity_type,
                success=success,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get('user-agent')
            )

            db.add(log_entry)
            await db.commit()

    except Exception as e:
        logger.error(f"Error logging module generation activity: {e}")
