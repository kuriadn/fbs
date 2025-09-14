"""
FBS License Manager Router - FastAPI

License management API endpoints migrated from Django.
Provides enterprise-grade licensing, feature flags, and upgrade management.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.dependencies import get_db_session_for_request, get_current_user
from ..services.license_service import LicenseService

router = APIRouter(prefix="/api/license", tags=["license"])

# ============================================================================
# LICENSE MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/info", response_model=Dict[str, Any])
async def get_license_info(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get license information"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        license_service = LicenseService(solution_name)

        result = await license_service.get_license_info()

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to get license information")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check-access", response_model=Dict[str, Any])
async def check_feature_access(
    feature_name: str,
    current_usage: int = 0,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Check feature access and usage limits"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        license_service = LicenseService(solution_name)

        result = await license_service.check_feature_access(
            feature_name=feature_name,
            current_usage=current_usage
        )

        return {
            'success': True,
            'feature_name': feature_name,
            'access_granted': result['access'],
            'reason': result.get('reason'),
            'current_usage': result['current_usage'],
            'limit': result['limit'],
            'remaining': result['remaining'],
            'upgrade_required': result.get('upgrade_required', False)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upgrade-recommendations", response_model=Dict[str, Any])
async def get_upgrade_recommendations(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get upgrade recommendations based on usage"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        license_service = LicenseService(solution_name)

        result = await license_service.get_upgrade_recommendations()

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to get upgrade recommendations")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create", response_model=Dict[str, Any])
async def create_license(
    license_type: str,
    expiry_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Create new license (admin only)"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        license_service = LicenseService(solution_name)

        license_data = {
            'license_type': license_type,
            'expiry_date': expiry_date,
            'source': 'api'
        }

        result = await license_service.create_license(license_data)

        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to create license'))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/limits", response_model=Dict[str, Any])
async def get_license_limits(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get current license limits"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        license_service = LicenseService(solution_name)

        license_info = await license_service.get_license_info()

        if license_info['success']:
            return {
                'success': True,
                'limits': license_info.get('limits', {}),
                'license_type': license_info.get('license', {}).get('type'),
                'is_expired': license_info.get('is_expired', False)
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to get license limits")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/features", response_model=Dict[str, Any])
async def get_enabled_features(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get list of enabled features"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        license_service = LicenseService(solution_name)

        license_info = await license_service.get_license_info()

        if license_info['success']:
            return {
                'success': True,
                'enabled_features': license_info.get('features_enabled', []),
                'license_type': license_info.get('license', {}).get('type'),
                'all_features': [
                    'msme', 'bi', 'workflows', 'compliance',
                    'accounting', 'dms', 'licensing'
                ]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to get enabled features")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage", response_model=Dict[str, Any])
async def get_feature_usage(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get feature usage statistics"""
    try:
        from ..models.license_models import FeatureUsage

        solution_name = current_user.get('solution_name', 'default')

        async for db_session in get_db_session_for_request(None):
            usage_records = await db_session.query(FeatureUsage).filter(
                FeatureUsage.solution_name == solution_name
            ).all()

            usage_data = {}
            for record in usage_records:
                usage_data[record.feature_name] = {
                    'current_usage': record.usage_count,
                    'period_start': record.period_start.isoformat() if record.period_start else None,
                    'period_end': record.period_end.isoformat() if record.period_end else None,
                    'status': record.status.value
                }

            return {
                'success': True,
                'usage': usage_data,
                'total_features': len(usage_data)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-log", response_model=Dict[str, Any])
async def get_audit_log(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """Get license audit log"""
    try:
        from ..models.license_models import LicenseAuditLog

        solution_name = current_user.get('solution_name', 'default')

        async for db_session in get_db_session_for_request(None):
            audit_records = await db_session.query(LicenseAuditLog).filter(
                LicenseAuditLog.solution_name == solution_name
            ).order_by(LicenseAuditLog.created_at.desc()).limit(limit).all()

            audit_data = []
            for record in audit_records:
                audit_data.append({
                    'id': record.id,
                    'action': record.action,
                    'performed_by': record.performed_by,
                    'created_at': record.created_at.isoformat(),
                    'metadata': record.metadata
                })

            return {
                'success': True,
                'audit_log': audit_data,
                'total_records': len(audit_data)
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def license_health_check(
    db: AsyncSession = Depends(get_db_session_for_request),
    current_user: dict = Depends(get_current_user)
):
    """License service health check"""
    try:
        solution_name = current_user.get('solution_name', 'default')
        license_service = LicenseService(solution_name)

        health_result = await license_service.health_check()

        return {
            'success': True,
            'service': 'license_manager',
            'status': 'healthy',
            'license_loaded': health_result.get('license_loaded', False),
            'solution_name': solution_name,
            'timestamp': health_result.get('timestamp')
        }

    except Exception as e:
        return {
            'success': False,
            'service': 'license_manager',
            'status': 'unhealthy',
            'error': str(e)
        }

