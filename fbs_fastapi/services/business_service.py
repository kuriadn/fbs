"""
FBS v3 Business Service

Core business logic for FBS v3 streamlined architecture.
Handles business entities, metrics, dashboards, and analytics.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from ..models.models import (
    BusinessEntity, BusinessMetric, Dashboard, Report,
    Workflow, BusinessTemplate, AuditLog,
    BusinessType, BusinessSize, MetricType, WorkflowType
)

class BusinessService:
    """Business service for FBS v3 operations"""

    async def create_business(
        self,
        business_data: dict,
        db: AsyncSession,
        current_user: dict
    ) -> Dict[str, Any]:
        """Create a new business entity"""
        try:
            # Create business entity
            business = BusinessEntity(
                id=uuid4(),
                name=business_data.name,
                type=business_data.type.value,
                industry=business_data.industry,
                size=business_data.size.value,
                configuration=business_data.configuration,
                metadata=business_data.metadata
            )

            db.add(business)

            # Create audit log
            audit_log = AuditLog(
                business_id=business.id,
                user_id=current_user.get('id'),
                action='create',
                resource='business_entities',
                resource_id=business.id,
                new_values=business_data.dict(),
                ip_address=current_user.get('ip_address'),
                user_agent=current_user.get('user_agent')
            )

            db.add(audit_log)
            await db.commit()
            await db.refresh(business)

            return {
                'id': str(business.id),
                'name': business.name,
                'type': business.type,
                'industry': business.industry,
                'size': business.size,
                'configuration': business.configuration,
                'metadata': business.metadata,
                'is_active': business.is_active,
                'created_at': business.created_at.isoformat(),
                'updated_at': business.updated_at.isoformat()
            }

        except Exception as e:
            await db.rollback()
            raise Exception(f"Failed to create business: {str(e)}")

    async def list_businesses(
        self,
        db: AsyncSession,
        current_user: dict,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        type_filter: Optional[BusinessType] = None,
        size_filter: Optional[BusinessSize] = None
    ) -> List[Dict[str, Any]]:
        """List businesses with filtering and pagination"""
        try:
            query = select(BusinessEntity)

            # Apply filters
            if search:
                query = query.where(
                    or_(
                        BusinessEntity.name.ilike(f'%{search}%'),
                        BusinessEntity.industry.ilike(f'%{search}%')
                    )
                )

            if type_filter:
                query = query.where(BusinessEntity.type == type_filter.value)

            if size_filter:
                query = query.where(BusinessEntity.size == size_filter.value)

            # Apply pagination
            query = query.offset(skip).limit(limit).order_by(desc(BusinessEntity.created_at))

            result = await db.execute(query)
            businesses = result.scalars().all()

            return [{
                'id': str(b.id),
                'name': b.name,
                'type': b.type,
                'industry': b.industry,
                'size': b.size,
                'is_active': b.is_active,
                'created_at': b.created_at.isoformat(),
                'updated_at': b.updated_at.isoformat()
            } for b in businesses]

        except Exception as e:
            raise Exception(f"Failed to list businesses: {str(e)}")

    async def get_business(
        self,
        business_id: UUID,
        db: AsyncSession,
        current_user: dict
    ) -> Optional[Dict[str, Any]]:
        """Get a specific business entity"""
        try:
            query = select(BusinessEntity).where(BusinessEntity.id == business_id)
            result = await db.execute(query)
            business = result.scalar_one_or_none()

            if not business:
                return None

            return {
                'id': str(business.id),
                'name': business.name,
                'type': business.type,
                'industry': business.industry,
                'size': business.size,
                'configuration': business.configuration,
                'metadata': business.metadata,
                'is_active': business.is_active,
                'created_at': business.created_at.isoformat(),
                'updated_at': business.updated_at.isoformat()
            }

        except Exception as e:
            raise Exception(f"Failed to get business: {str(e)}")

    async def get_business_metrics(
        self,
        business_id: UUID,
        db: AsyncSession,
        current_user: dict,
        metric_type: Optional[str] = None,
        period: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get business metrics with filtering"""
        try:
            query = select(BusinessMetric).where(BusinessMetric.business_id == business_id)

            if metric_type:
                query = query.where(BusinessMetric.metric_type == metric_type)

            if period:
                query = query.where(BusinessMetric.period == period)

            query = query.order_by(desc(BusinessMetric.date)).limit(limit)

            result = await db.execute(query)
            metrics = result.scalars().all()

            return [{
                'id': str(m.id),
                'metric_type': m.metric_type,
                'name': m.name,
                'value': float(m.value),
                'target': float(m.target) if m.target else None,
                'period': m.period,
                'date': m.date.isoformat(),
                'metadata': m.metadata,
                'created_at': m.created_at.isoformat()
            } for m in metrics]

        except Exception as e:
            raise Exception(f"Failed to get business metrics: {str(e)}")

    async def get_business_analytics_summary(
        self,
        business_id: UUID,
        period: str,
        db: AsyncSession,
        current_user: dict
    ) -> Dict[str, Any]:
        """Get business analytics summary"""
        try:
            # Get latest metrics for each type
            query = select(
                BusinessMetric.metric_type,
                func.max(BusinessMetric.date).label('latest_date')
            ).where(
                and_(
                    BusinessMetric.business_id == business_id,
                    BusinessMetric.period == period
                )
            ).group_by(BusinessMetric.metric_type)

            result = await db.execute(query)
            metric_types_dates = result.all()

            summary = {
                'business_id': str(business_id),
                'period': period,
                'metrics': {}
            }

            # Get latest values for each metric type
            for metric_type, latest_date in metric_types_dates:
                metric_query = select(BusinessMetric).where(
                    and_(
                        BusinessMetric.business_id == business_id,
                        BusinessMetric.metric_type == metric_type,
                        BusinessMetric.date == latest_date
                    )
                )
                metric_result = await db.execute(metric_query)
                metrics = metric_result.scalars().all()

                summary['metrics'][metric_type] = [{
                    'name': m.name,
                    'value': float(m.value),
                    'target': float(m.target) if m.target else None,
                    'date': m.date.isoformat()
                } for m in metrics]

            return summary

        except Exception as e:
            raise Exception(f"Failed to get analytics summary: {str(e)}")

    async def get_business_analytics_trends(
        self,
        business_id: UUID,
        metric_name: str,
        days: int,
        db: AsyncSession,
        current_user: dict
    ) -> Dict[str, Any]:
        """Get business analytics trends"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            query = select(BusinessMetric).where(
                and_(
                    BusinessMetric.business_id == business_id,
                    BusinessMetric.name == metric_name,
                    BusinessMetric.date >= cutoff_date
                )
            ).order_by(BusinessMetric.date)

            result = await db.execute(query)
            metrics = result.scalars().all()

            return {
                'business_id': str(business_id),
                'metric_name': metric_name,
                'days': days,
                'data_points': len(metrics),
                'trend': [{
                    'date': m.date.isoformat(),
                    'value': float(m.value),
                    'target': float(m.target) if m.target else None
                } for m in metrics]
            }

        except Exception as e:
            raise Exception(f"Failed to get analytics trends: {str(e)}")

    async def get_business_dashboards(
        self,
        business_id: UUID,
        db: AsyncSession,
        current_user: dict,
        dashboard_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get business dashboards"""
        try:
            query = select(Dashboard).where(
                and_(
                    Dashboard.business_id == business_id,
                    Dashboard.is_active == True
                )
            )

            if dashboard_type:
                query = query.where(Dashboard.type == dashboard_type)

            query = query.order_by(Dashboard.created_at)

            result = await db.execute(query)
            dashboards = result.scalars().all()

            return [{
                'id': str(d.id),
                'name': d.name,
                'type': d.type,
                'layout': d.layout,
                'widgets': d.widgets,
                'is_public': d.is_public,
                'created_by': str(d.created_by) if d.created_by else None,
                'created_at': d.created_at.isoformat(),
                'updated_at': d.updated_at.isoformat()
            } for d in dashboards]

        except Exception as e:
            raise Exception(f"Failed to get business dashboards: {str(e)}")

    async def get_business_workflows(
        self,
        business_id: UUID,
        db: AsyncSession,
        current_user: dict,
        status: Optional[str] = None,
        workflow_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get business workflows"""
        try:
            query = select(Workflow).where(Workflow.business_id == business_id)

            if status:
                query = query.where(Workflow.status == status)

            if workflow_type:
                query = query.where(Workflow.type == workflow_type)

            query = query.order_by(desc(Workflow.started_at))

            result = await db.execute(query)
            workflows = result.scalars().all()

            return [{
                'id': str(w.id),
                'name': w.name,
                'type': w.type,
                'status': w.status,
                'current_step': w.current_step,
                'steps': w.steps,
                'data': w.data,
                'created_by': str(w.created_by) if w.created_by else None,
                'started_at': w.started_at.isoformat(),
                'completed_at': w.completed_at.isoformat() if w.completed_at else None,
                'updated_at': w.updated_at.isoformat()
            } for w in workflows]

        except Exception as e:
            raise Exception(f"Failed to get business workflows: {str(e)}")

    async def get_business_templates(
        self,
        business_type: Optional[BusinessType],
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Get available business templates"""
        try:
            query = select(BusinessTemplate).where(BusinessTemplate.is_active == True)

            if business_type:
                query = query.where(BusinessTemplate.business_type == business_type.value)

            query = query.order_by(BusinessTemplate.business_type, BusinessTemplate.name)

            result = await db.execute(query)
            templates = result.scalars().all()

            return [{
                'id': str(t.id),
                'name': t.name,
                'business_type': t.business_type,
                'description': t.description,
                'configuration': t.configuration,
                'created_at': t.created_at.isoformat()
            } for t in templates]

        except Exception as e:
            raise Exception(f"Failed to get business templates: {str(e)}")

    async def get_business_compliance_status(
        self,
        business_id: UUID,
        db: AsyncSession,
        current_user: dict
    ) -> Dict[str, Any]:
        """Get business compliance status"""
        try:
            # Get compliance-related metrics
            query = select(BusinessMetric).where(
                and_(
                    BusinessMetric.business_id == business_id,
                    BusinessMetric.metric_type == 'compliance'
                )
            ).order_by(desc(BusinessMetric.date))

            result = await db.execute(query)
            compliance_metrics = result.scalars().all()

            # Calculate compliance status
            total_checks = len(compliance_metrics)
            compliant_checks = len([m for m in compliance_metrics if m.value == 1.0])
            at_risk_checks = len([m for m in compliance_metrics if 0 < m.value < 1.0])
            non_compliant_checks = len([m for m in compliance_metrics if m.value == 0])

            return {
                'business_id': str(business_id),
                'total_checks': total_checks,
                'compliant': compliant_checks,
                'at_risk': at_risk_checks,
                'non_compliant': non_compliant_checks,
                'compliance_rate': (compliant_checks / total_checks * 100) if total_checks > 0 else 0,
                'latest_checks': [{
                    'name': m.name,
                    'status': 'compliant' if m.value == 1.0 else 'non_compliant' if m.value == 0 else 'at_risk',
                    'date': m.date.isoformat()
                } for m in compliance_metrics[:10]]
            }

        except Exception as e:
            raise Exception(f"Failed to get compliance status: {str(e)}")

    # Additional methods would be implemented here:
    # - update_business
    # - delete_business
    # - add_business_metric
    # - create_business_dashboard
    # - create_business_workflow
    # - apply_business_template
    # - run_compliance_check
