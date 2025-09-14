"""
FBS v3 Business API Router

Streamlined business entity management with full CRUD operations.
Optimized for React frontend with modern API patterns.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..core.dependencies import get_db_session_for_request, get_current_user
from ..models.models import (
    BusinessEntity, BusinessEntityCreate, BusinessEntityResponse,
    BusinessEntityBase, BusinessType, BusinessSize
)
from ..services.business_service import BusinessService
from ..services.service_interfaces import FBSInterface

router = APIRouter()

# ============================================================================
# BUSINESS ENTITY CRUD
# ============================================================================

@router.post("/", response_model=BusinessEntityResponse)
async def create_business(
    business: BusinessEntityCreate,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Create a new business entity"""
    service = BusinessService()
    return await service.create_business(business, db, current_user)

@router.get("/", response_model=List[BusinessEntityResponse])
async def list_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    type_filter: Optional[BusinessType] = None,
    size_filter: Optional[BusinessSize] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """List businesses with filtering and pagination"""
    service = BusinessService()
    return await service.list_businesses(
        db, current_user,
        skip=skip, limit=limit,
        search=search, type_filter=type_filter, size_filter=size_filter
    )

@router.get("/{business_id}", response_model=BusinessEntityResponse)
async def get_business(
    business_id: UUID,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific business entity"""
    service = BusinessService()
    business = await service.get_business(business_id, db, current_user)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.put("/{business_id}", response_model=BusinessEntityResponse)
async def update_business(
    business_id: UUID,
    business_update: BusinessEntityBase,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Update a business entity"""
    service = BusinessService()
    updated_business = await service.update_business(
        business_id, business_update, db, current_user
    )
    if not updated_business:
        raise HTTPException(status_code=404, detail="Business not found")
    return updated_business

@router.delete("/{business_id}")
async def delete_business(
    business_id: UUID,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Delete a business entity"""
    service = BusinessService()
    deleted = await service.delete_business(business_id, db, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Business not found")
    return {"message": "Business deleted successfully"}

# ============================================================================
# BUSINESS METRICS ENDPOINTS
# ============================================================================

@router.get("/{business_id}/metrics")
async def get_business_metrics(
    business_id: UUID,
    metric_type: Optional[str] = None,
    period: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get business metrics with filtering"""
    service = BusinessService()
    return await service.get_business_metrics(
        business_id, db, current_user,
        metric_type=metric_type, period=period, limit=limit
    )

@router.post("/{business_id}/metrics")
async def add_business_metric(
    business_id: UUID,
    metric_data: dict,  # Would be a proper Pydantic model
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Add a new business metric"""
    service = BusinessService()
    return await service.add_business_metric(
        business_id, metric_data, db, current_user
    )

# ============================================================================
# BUSINESS DASHBOARDS
# ============================================================================

@router.get("/{business_id}/dashboards")
async def get_business_dashboards(
    business_id: UUID,
    dashboard_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get business dashboards"""
    service = BusinessService()
    return await service.get_business_dashboards(
        business_id, db, current_user, dashboard_type=dashboard_type
    )

@router.post("/{business_id}/dashboards")
async def create_business_dashboard(
    business_id: UUID,
    dashboard_data: dict,  # Would be a proper Pydantic model
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Create a new business dashboard"""
    service = BusinessService()
    return await service.create_business_dashboard(
        business_id, dashboard_data, db, current_user
    )

# ============================================================================
# BUSINESS WORKFLOWS
# ============================================================================

@router.get("/{business_id}/workflows")
async def get_business_workflows(
    business_id: UUID,
    status: Optional[str] = None,
    workflow_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get business workflows"""
    service = BusinessService()
    return await service.get_business_workflows(
        business_id, db, current_user,
        status=status, workflow_type=workflow_type
    )

@router.post("/{business_id}/workflows")
async def create_business_workflow(
    business_id: UUID,
    workflow_data: dict,  # Would be a proper Pydantic model
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Create a new business workflow"""
    service = BusinessService()
    return await service.create_business_workflow(
        business_id, workflow_data, db, current_user
    )

# ============================================================================
# BUSINESS ANALYTICS
# ============================================================================

@router.get("/{business_id}/analytics/summary")
async def get_business_analytics_summary(
    business_id: UUID,
    period: str = "monthly",
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get business analytics summary"""
    service = BusinessService()
    return await service.get_business_analytics_summary(
        business_id, period, db, current_user
    )

@router.get("/{business_id}/analytics/trends")
async def get_business_analytics_trends(
    business_id: UUID,
    metric_name: str,
    days: int = 30,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get business analytics trends"""
    service = BusinessService()
    return await service.get_business_analytics_trends(
        business_id, metric_name, days, db, current_user
    )

# ============================================================================
# BUSINESS TEMPLATES
# ============================================================================

@router.get("/templates")
async def get_business_templates(
    business_type: Optional[BusinessType] = None,
    db: AsyncSession = Depends(get_db_session_for_request)
):
    """Get available business templates"""
    service = BusinessService()
    return await service.get_business_templates(business_type, db)

@router.post("/{business_id}/apply-template/{template_id}")
async def apply_business_template(
    business_id: UUID,
    template_id: UUID,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Apply a business template to an existing business"""
    service = BusinessService()
    return await service.apply_business_template(
        business_id, template_id, db, current_user
    )

# ============================================================================
# BUSINESS COMPLIANCE
# ============================================================================

@router.get("/{business_id}/compliance")
async def get_business_compliance_status(
    business_id: UUID,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get business compliance status"""
    service = BusinessService()
    return await service.get_business_compliance_status(business_id, db, current_user)

@router.post("/{business_id}/compliance/check")
async def run_compliance_check(
    business_id: UUID,
    check_type: str,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Run a compliance check"""
    service = BusinessService()
    return await service.run_compliance_check(
        business_id, check_type, db, current_user
    )

# ============================================================================
# FBS SERVICE INTERFACE ENDPOINTS (PRESERVED FROM DJANGO)
# ============================================================================

@router.get("/api/fbs/info")
async def get_fbs_solution_info(request: Request) -> Dict[str, Any]:
    """Get FBS solution information using service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)
        info = await fbs.get_solution_info()

        return {
            'success': True,
            'data': info,
            'message': 'FBS solution information retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/health")
async def get_fbs_system_health(request: Request) -> Dict[str, Any]:
    """Get FBS system health using service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)
        health = await fbs.get_system_health()

        return {
            'success': True,
            'data': health,
            'message': 'FBS system health retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/setup")
async def setup_fbs_business(
    request: Request,
    business_type: str,
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Setup FBS business using MSME service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.setup_business(business_type, config or {})

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS business setup completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/dashboard")
async def get_fbs_dashboard(request: Request) -> Dict[str, Any]:
    """Get FBS dashboard using service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        dashboard = await fbs.msme.get_dashboard()

        return {
            'success': dashboard['success'],
            'data': dashboard.get('data', {}),
            'message': 'FBS dashboard retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/kpis")
async def get_fbs_kpis(request: Request) -> Dict[str, Any]:
    """Get FBS KPIs using service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        kpis = await fbs.msme.calculate_kpis()

        return {
            'success': kpis['success'],
            'data': kpis,
            'message': 'FBS KPIs calculated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/compliance")
async def get_fbs_compliance_status(request: Request) -> Dict[str, Any]:
    """Get FBS compliance status using service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        compliance = await fbs.msme.get_compliance_status()

        return {
            'success': compliance['success'],
            'data': compliance,
            'message': 'FBS compliance status retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/templates")
async def get_fbs_business_templates(request: Request) -> Dict[str, Any]:
    """Get FBS business templates using service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        templates = await fbs.msme.get_business_templates()

        return {
            'success': templates['success'],
            'data': templates,
            'message': 'FBS business templates retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/custom-field")
async def create_fbs_custom_field(
    request: Request,
    field_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS custom field using service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.create_custom_field(field_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS custom field created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BI SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/bi/dashboard")
async def create_fbs_dashboard(
    request: Request,
    dashboard_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS dashboard using BI service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.bi.create_dashboard(dashboard_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS dashboard created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/bi/dashboards")
async def get_fbs_dashboards(
    request: Request,
    dashboard_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS dashboards using BI service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.bi.get_dashboards(dashboard_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS dashboards retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/bi/report")
async def create_fbs_report(
    request: Request,
    report_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS report using BI service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.bi.create_report(report_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS report created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/bi/reports")
async def get_fbs_reports(
    request: Request,
    report_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS reports using BI service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.bi.get_reports(report_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS reports retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/bi/kpi")
async def create_fbs_kpi(
    request: Request,
    kpi_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS KPI using BI service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.bi.create_kpi(kpi_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS KPI created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/bi/kpis")
async def get_fbs_kpis(
    request: Request,
    kpi_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS KPIs using BI service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.bi.get_kpis(kpi_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS KPIs retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# WORKFLOW SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/workflow/definition")
async def create_fbs_workflow_definition(
    request: Request,
    workflow_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS workflow definition using workflow service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.workflows.create_workflow_definition(workflow_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS workflow definition created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/workflow/definitions")
async def get_fbs_workflow_definitions(
    request: Request,
    workflow_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS workflow definitions using workflow service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.workflows.get_workflow_definitions(workflow_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS workflow definitions retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/workflow/start")
async def start_fbs_workflow(
    request: Request,
    workflow_definition_id: str,
    initial_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Start FBS workflow using workflow service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        # Convert string ID to UUID
        from uuid import UUID
        workflow_id = UUID(workflow_definition_id)

        result = await fbs.workflows.start_workflow(workflow_id, initial_data or {})

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS workflow started successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/workflow/active")
async def get_fbs_active_workflows(
    request: Request,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS active workflows using workflow service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        # Convert string ID to UUID if provided
        user_uuid = None
        if user_id:
            from uuid import UUID
            user_uuid = UUID(user_id)

        result = await fbs.workflows.get_active_workflows(user_uuid)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS active workflows retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/workflow/approval")
async def create_fbs_approval_request(
    request: Request,
    approval_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS approval request using workflow service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.workflows.create_approval_request(approval_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS approval request created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# COMPLIANCE SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/compliance/rule")
async def create_fbs_compliance_rule(
    request: Request,
    rule_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS compliance rule using compliance service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.compliance.create_compliance_rule(rule_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS compliance rule created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/compliance/rules")
async def get_fbs_compliance_rules(
    request: Request,
    compliance_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS compliance rules using compliance service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.compliance.get_compliance_rules(compliance_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS compliance rules retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/compliance/status")
async def get_fbs_compliance_status(
    request: Request,
    compliance_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS compliance status using compliance service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.compliance.get_compliance_status(compliance_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS compliance status retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/compliance/calculate-tax")
async def calculate_fbs_tax(
    request: Request,
    tax_type: str,
    amount: float,
    period: str = 'monthly'
) -> Dict[str, Any]:
    """Calculate FBS tax using compliance service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.compliance.calculate_tax(tax_type, amount, period)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS tax calculated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# NOTIFICATION SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/notification")
async def create_fbs_notification(
    request: Request,
    notification_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create FBS notification using notification service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.notifications.create_notification(notification_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS notification created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/notifications")
async def get_fbs_notifications(
    request: Request,
    notification_type: Optional[str] = None,
    is_read: Optional[bool] = None
) -> Dict[str, Any]:
    """Get FBS notifications using notification service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.notifications.get_notifications(notification_type, is_read)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS notifications retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/fbs/notification/{notification_id}/read")
async def mark_fbs_notification_read(
    request: Request,
    notification_id: str
) -> Dict[str, Any]:
    """Mark FBS notification as read using notification service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        # Convert string ID to UUID
        from uuid import UUID
        notification_uuid = UUID(notification_id)

        result = await fbs.notifications.mark_notification_read(notification_uuid)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS notification marked as read'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/notifications/alerts")
async def get_fbs_msme_alerts(
    request: Request,
    alert_type: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """Get FBS MSME alerts using notification service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.notifications.get_msme_alerts(alert_type, limit)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS MSME alerts retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CACHE SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.get("/api/fbs/cache/{key}")
async def get_fbs_cache_value(
    request: Request,
    key: str
) -> Dict[str, Any]:
    """Get FBS cache value using cache service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        value = await fbs.cache.get(key)

        return {
            'success': True,
            'key': key,
            'value': value,
            'message': 'FBS cache value retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/cache/{key}")
async def set_fbs_cache_value(
    request: Request,
    key: str,
    value: Any,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """Set FBS cache value using cache service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        success = await fbs.cache.set(key, value, timeout)

        return {
            'success': success,
            'key': key,
            'timeout': timeout,
            'message': 'FBS cache value set successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/fbs/cache/{key}")
async def delete_fbs_cache_value(
    request: Request,
    key: str
) -> Dict[str, Any]:
    """Delete FBS cache value using cache service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        success = await fbs.cache.delete(key)

        return {
            'success': success,
            'key': key,
            'message': 'FBS cache value deleted successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/cache/stats")
async def get_fbs_cache_stats(request: Request) -> Dict[str, Any]:
    """Get FBS cache statistics using cache service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        stats = await fbs.cache.get_cache_stats()

        return {
            'success': True,
            'data': stats,
            'message': 'FBS cache statistics retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# JWT AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/auth/jwt/login", response_model=Dict[str, Any])
async def jwt_login(user_credentials: Dict[str, Any], db: AsyncSession = Depends(get_db_session_for_request)):
    """Authenticate user and return JWT token"""
    try:
        from ..services.auth_service import AuthService
        auth_service = AuthService("system")

        # Here you would validate user credentials against database
        # For now, create a token for demo purposes
        user_data = {
            'user_id': user_credentials.get('username', 'demo_user'),
            'username': user_credentials.get('username', 'demo_user'),
            'email': user_credentials.get('email', 'demo@fbs.local'),
            'role': 'user',
            'permissions': ['read', 'write']
        }

        token_result = await auth_service.create_jwt_token(user_data)

        if token_result['success']:
            return {
                'success': True,
                'data': {
                    'access_token': token_result['token'],
                    'token_type': token_result['token_type'],
                    'expires_in': token_result['expires_in'],
                    'expires_at': token_result['expires_at'],
                    'user': token_result['user']
                },
                'message': 'JWT token created successfully'
            }
        else:
            raise HTTPException(status_code=401, detail=token_result.get('error', 'Authentication failed'))

    except Exception as e:
        logger.error(f"JWT login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication service error")

@router.post("/auth/jwt/validate", response_model=Dict[str, Any])
async def validate_jwt_token(token_data: Dict[str, str], db: AsyncSession = Depends(get_db_session_for_request)):
    """Validate JWT token"""
    try:
        from ..services.auth_service import AuthService
        auth_service = AuthService("system")

        token = token_data.get('token')
        if not token:
            raise HTTPException(status_code=400, detail="Token is required")

        validation_result = await auth_service.validate_jwt_token(token)

        if validation_result['success']:
            return {
                'success': True,
                'data': {
                    'valid': True,
                    'user': validation_result['user'],
                    'payload': validation_result['payload']
                },
                'message': 'JWT token is valid'
            }
        else:
            return {
                'success': True,
                'data': {
                    'valid': False,
                    'error': validation_result.get('error', 'Invalid token')
                },
                'message': validation_result.get('message', 'Token validation failed')
            }

    except Exception as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token validation service error")

@router.post("/auth/jwt/refresh", response_model=Dict[str, Any])
async def refresh_jwt_token(token_data: Dict[str, str], db: AsyncSession = Depends(get_db_session_for_request)):
    """Refresh JWT token using existing valid token"""
    try:
        from ..services.auth_service import AuthService
        auth_service = AuthService("system")

        token = token_data.get('token')
        if not token:
            raise HTTPException(status_code=400, detail="Token is required")

        # Validate current token
        validation_result = await auth_service.validate_jwt_token(token)

        if not validation_result['success']:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Create new token with same user data
        user_data = validation_result['user']
        new_token_result = await auth_service.create_jwt_token(user_data)

        if new_token_result['success']:
            return {
                'success': True,
                'data': {
                    'access_token': new_token_result['token'],
                    'token_type': new_token_result['token_type'],
                    'expires_in': new_token_result['expires_in'],
                    'expires_at': new_token_result['expires_at'],
                    'user': new_token_result['user']
                },
                'message': 'JWT token refreshed successfully'
            }
        else:
            raise HTTPException(status_code=500, detail="Token refresh failed")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JWT refresh error: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh service error")

# AUTHENTICATION SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/auth/handshake")
async def create_handshake(
    request: Request,
    secret_key: Optional[str] = None,
    expiry_hours: Optional[int] = None
) -> Dict[str, Any]:
    """Create a new handshake for system authentication"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.create_handshake(
            secret_key=secret_key,
            expiry_hours=expiry_hours
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Handshake created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/auth/validate-handshake")
async def validate_handshake(request: Request, handshake_id: str, secret_key: str) -> Dict[str, Any]:
    """Validate a handshake ID and secret key"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.validate_handshake(handshake_id, secret_key)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Handshake validation completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/auth/revoke-handshake")
async def revoke_handshake(request: Request, handshake_id: str) -> Dict[str, Any]:
    """Revoke a handshake"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.revoke_handshake(handshake_id)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Handshake revoked successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/auth/active-handshakes")
async def get_active_handshakes(
    request: Request,
    solution_name: Optional[str] = None
) -> Dict[str, Any]:
    """Get active handshakes for a solution"""
    try:
        fbs = FBSInterface(solution_name or getattr(request.state, 'solution_name', 'system'))

        result = await fbs.auth.get_active_handshakes(solution_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Active handshakes retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/auth/cleanup-expired")
async def cleanup_expired_handshakes(
    request: Request
) -> Dict[str, Any]:
    """Clean up expired handshakes"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.cleanup_expired_handshakes()

        return {
            'success': result['success'],
            'data': result,
            'message': 'Expired handshakes cleaned up successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/auth/token-mapping")
async def create_token_mapping(
    request: Request,
    user_id: str,
    database_name: str,
    odoo_token: str,
    odoo_user_id: int,
    expiry_hours: Optional[int] = None
) -> Dict[str, Any]:
    """Create token mapping for Odoo integration"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.create_token_mapping(
            user_id=user_id,
            database_name=database_name,
            odoo_token=odoo_token,
            odoo_user_id=odoo_user_id,
            expiry_hours=expiry_hours
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Token mapping created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/auth/validate-token")
async def validate_token_mapping(request: Request, token: str, database_name: str) -> Dict[str, Any]:
    """Validate token mapping"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.validate_token_mapping(token, database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Token mapping validation completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/auth/revoke-token")
async def revoke_token_mapping(request: Request, token_mapping_id: str) -> Dict[str, Any]:
    """Revoke token mapping"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.revoke_token_mapping(token_mapping_id)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Token mapping revoked successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/auth/user-tokens/{user_id}")
async def get_user_token_mappings(request: Request, user_id: str) -> Dict[str, Any]:
    """Get all token mappings for a user"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.auth.get_user_token_mappings(user_id)

        return {
            'success': result['success'],
            'data': result,
            'message': 'User token mappings retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MSME SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/msme/setup-business")
async def setup_msme_business(request: Request, business_type: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Setup MSME business with pre-configured data"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.setup_msme_business(business_type, config)

        return {
            'success': result['success'],
            'data': result,
            'message': 'MSME business setup completed'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/msme/kpis")
async def get_business_kpis(request: Request, business_type: Optional[str] = None) -> Dict[str, Any]:
    """Get business KPIs and metrics"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.get_business_kpis(business_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Business KPIs retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/msme/compliance")
async def get_compliance_status(
    request: Request
) -> Dict[str, Any]:
    """Get compliance status for the business"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.get_compliance_status()

        return {
            'success': result['success'],
            'data': result,
            'message': 'Compliance status retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/msme/marketing")
async def get_marketing_data(
    request: Request
) -> Dict[str, Any]:
    """Get marketing data and analytics"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.get_marketing_data()

        return {
            'success': result['success'],
            'data': result,
            'message': 'Marketing data retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/msme/analytics")
async def get_analytics_summary(
    request: Request
) -> Dict[str, Any]:
    """Get analytics summary for the business"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.get_analytics_summary()

        return {
            'success': result['success'],
            'data': result,
            'message': 'Analytics summary retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/fbs/msme/profile")
async def update_business_profile(request: Request, profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update business profile information"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.update_business_profile(profile_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Business profile updated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/msme/custom-field")
async def create_custom_field(request: Request, field_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create custom field for the business"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.create_custom_field(field_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Custom field created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/msme/templates")
async def get_business_templates(
    request: Request
) -> Dict[str, Any]:
    """Get available business templates"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.get_business_templates()

        return {
            'success': result['success'],
            'data': result,
            'message': 'Business templates retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/msme/apply-template")
async def apply_business_template(request: Request, template_name: str) -> Dict[str, Any]:
    """Apply a business template"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.apply_business_template(template_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Business template applied successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/msme/insights")
async def get_business_insights(
    request: Request
) -> Dict[str, Any]:
    """Get business insights and recommendations"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.msme.get_business_insights()

        return {
            'success': result['success'],
            'data': result,
            'message': 'Business insights retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DISCOVERY SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.get("/api/fbs/discovery/models")
async def discover_models(request: Request, database_name: Optional[str] = None) -> Dict[str, Any]:
    """Discover all models in an Odoo database"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.discovery.discover_models(database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Models discovered successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/discovery/modules")
async def discover_modules(request: Request, database_name: Optional[str] = None) -> Dict[str, Any]:
    """Discover installed modules in an Odoo database"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.discovery.discover_modules(database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Modules discovered successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/discovery/fields/{model_name}")
async def discover_model_fields(request: Request, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
    """Discover fields for a specific Odoo model"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.discovery.discover_fields(model_name, database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Model fields discovered successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/discovery/install-module")
async def install_module(request: Request, module_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
    """Install a module in Odoo database"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.discovery.install_module(module_name, database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Module installation initiated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/discovery/uninstall-module")
async def uninstall_module(request: Request, module_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
    """Uninstall a module from Odoo database"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.discovery.uninstall_module(module_name, database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Module uninstallation initiated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/discovery/relationships/{model_name}")
async def get_model_relationships(request: Request, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
    """Get relationships between models"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.discovery.get_model_relationships(model_name, database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Model relationships retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/discovery/workflows/{model_name}")
async def discover_model_workflows(request: Request, model_name: str, database_name: Optional[str] = None) -> Dict[str, Any]:
    """Discover workflows for a model"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.discovery.discover_workflows(model_name, database_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Model workflows discovered successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SIGNALS SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/signals/register")
async def register_custom_signal(request: Request, signal_name: str, handler_name: str) -> Dict[str, Any]:
    """Register a custom signal handler"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        # For now, create a simple handler that logs the signal
        async def signal_handler(**kwargs):
            logger.info(f"Custom signal {signal_name} triggered: {kwargs}")
            from datetime import datetime
            return {"handler": handler_name, "timestamp": datetime.now().isoformat()}

        result = await fbs.signals.register_custom_signal(signal_name, signal_handler)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Custom signal registered successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/signals/send/{signal_name}")
async def send_custom_signal(request: Request, signal_name: str, signal_data: Dict[str, Any]) -> Dict[str, Any]:
    """Send a custom signal"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.signals.send_custom_signal(signal_name, **signal_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Custom signal sent successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/signals/stats")
async def get_signal_stats(
    request: Request
) -> Dict[str, Any]:
    """Get statistics about registered signals"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.signals.get_signal_stats()

        return {
            'success': result['success'],
            'data': result,
            'message': 'Signal statistics retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/signals/trigger/{model_name}")
async def trigger_model_signal(request: Request, model_name: str, operation: str, instance_data: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger a signal for a specific model operation"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.signals.trigger_model_signal(model_name, operation, instance_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Model signal triggered successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ONBOARDING SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/onboarding/start")
async def start_onboarding(request: Request, client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Start client onboarding process using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.start_onboarding(client_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Onboarding process started successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/onboarding/status/{client_id}")
async def get_onboarding_status(request: Request, client_id: UUID) -> Dict[str, Any]:
    """Get onboarding status using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.get_onboarding_status(client_id)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Onboarding status retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/onboarding/step/{client_id}")
async def update_onboarding_step(request: Request, client_id: UUID, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update onboarding step using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.update_onboarding_step(client_id, step_name, step_data)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Onboarding step updated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/onboarding/complete/{client_id}")
async def complete_onboarding(request: Request, client_id: UUID) -> Dict[str, Any]:
    """Complete onboarding process using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.complete_onboarding(client_id)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Onboarding process completed successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/onboarding/templates")
async def get_onboarding_templates(request: Request, business_type: Optional[str] = None) -> Dict[str, Any]:
    """Get onboarding templates using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.get_onboarding_templates(business_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Onboarding templates retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/onboarding/apply-template/{client_id}")
async def apply_onboarding_template(request: Request, client_id: UUID, template_name: str) -> Dict[str, Any]:
    """Apply onboarding template using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.apply_onboarding_template(client_id, template_name)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Onboarding template applied successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/onboarding/demo-data/{client_id}")
async def import_demo_data(request: Request, client_id: UUID, demo_type: str) -> Dict[str, Any]:
    """Import demo data for client using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.import_demo_data(client_id, demo_type)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Demo data import started successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/onboarding/timeline/{client_id}")
async def get_onboarding_timeline(request: Request, client_id: UUID) -> Dict[str, Any]:
    """Get onboarding timeline using onboarding service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.onboarding.get_onboarding_timeline(client_id)

        return {
            'success': result['success'],
            'data': result,
            'message': 'Onboarding timeline retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# VIRTUAL FIELDS SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/fields/{model_name}/{record_id}")
async def set_custom_field(request: Request, model_name: str, record_id: int, field_name: str, field_value: Any, field_type: str = 'char') -> Dict[str, Any]:
    """Set custom field value using virtual fields service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.fields.set_custom_field(
            model_name=model_name,
            record_id=record_id,
            field_name=field_name,
            field_value=field_value,
            field_type=field_type
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Custom field set successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/fields/{model_name}/{record_id}")
async def get_custom_fields(request: Request, model_name: str, record_id: int) -> Dict[str, Any]:
    """Get all custom fields for a record using virtual fields service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.fields.get_custom_fields(
            model_name=model_name,
            record_id=record_id
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Custom fields retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/fields/{model_name}/{record_id}/{field_name}")
async def get_custom_field(request: Request, model_name: str, record_id: int, field_name: str) -> Dict[str, Any]:
    """Get specific custom field value using virtual fields service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.fields.get_custom_field(
            model_name=model_name,
            record_id=record_id,
            field_name=field_name
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Custom field retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/fbs/fields/{model_name}/{record_id}/{field_name}")
async def delete_custom_field(request: Request, model_name: str, record_id: int, field_name: str) -> Dict[str, Any]:
    """Delete custom field using virtual fields service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.fields.delete_custom_field(
            model_name=model_name,
            record_id=record_id,
            field_name=field_name
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Custom field deleted successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/fields/merge/{model_name}/{record_id}")
async def merge_odoo_with_custom(request: Request, model_name: str, record_id: int, odoo_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """Merge Odoo data with custom fields using virtual fields service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.fields.merge_odoo_with_custom(
            model_name=model_name,
            record_id=record_id,
            odoo_fields=odoo_fields
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Data merged successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/fields/schema/{model_name}")
async def get_virtual_model_schema(request: Request, model_name: str) -> Dict[str, Any]:
    """Get virtual model schema including custom fields"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.fields.get_virtual_model_schema(
            model_name=model_name
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'Virtual model schema retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ACCOUNTING SERVICE ENDPOINTS (PRESERVED from Django)
# ============================================================================

@router.post("/api/fbs/accounting/cash-entry")
async def create_fbs_cash_entry(
    request: Request,
    entry_type: str,
    amount: float,
    description: str = '',
    category: str = '',
    date: Optional[str] = None
) -> Dict[str, Any]:
    """Create FBS cash entry using accounting service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.accounting.create_cash_entry(
            entry_type=entry_type,
            amount=amount,
            description=description,
            category=category,
            date=date
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS cash entry created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/accounting/ledger")
async def get_fbs_ledger(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    account_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS basic ledger using accounting service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.accounting.get_basic_ledger(
            start_date=start_date,
            end_date=end_date,
            account_type=account_type
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS ledger retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/accounting/income-expense")
async def create_fbs_income_expense(
    request: Request,
    transaction_type: str,
    amount: float,
    description: str = '',
    category: str = '',
    date: Optional[str] = None
) -> Dict[str, Any]:
    """Create FBS income/expense record using accounting service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.accounting.track_income_expense(
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            category=category,
            date=date
        )

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS income/expense record created successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/accounting/summary")
async def get_fbs_accounting_summary(
    request: Request,
    period: str = 'month'
) -> Dict[str, Any]:
    """Get FBS income and expense summary using accounting service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.accounting.get_income_expense_summary(period)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS accounting summary retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/accounting/health")
async def get_fbs_financial_health(
    request: Request
) -> Dict[str, Any]:
    """Get FBS financial health indicators using accounting service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.accounting.get_financial_health_indicators()

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS financial health indicators retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/fbs/accounting/calculate-tax")
async def calculate_fbs_tax(
    request: Request,
    amount: float,
    tax_type: str = 'vat',
    tax_rate: Optional[float] = None
) -> Dict[str, Any]:
    """Calculate FBS tax using accounting service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.accounting.calculate_tax(amount, tax_type, tax_rate)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS tax calculated successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/fbs/accounting/cash-position")
async def get_fbs_cash_position(
    request: Request,
    date: Optional[str] = None
) -> Dict[str, Any]:
    """Get FBS current cash position using accounting service interface"""
    try:
        solution_name = getattr(request.state, 'solution_name', 'system')
        fbs = FBSInterface(solution_name)

        result = await fbs.accounting.get_cash_position(date)

        return {
            'success': result['success'],
            'data': result,
            'message': 'FBS cash position retrieved successfully'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
