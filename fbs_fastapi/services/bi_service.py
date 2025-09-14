"""
FBS FastAPI Business Intelligence Service

PRESERVED from Django bi_service.py - comprehensive BI capabilities
including analytics, KPI calculations, report generation, and dashboard data.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from uuid import UUID

from .service_interfaces import BusinessIntelligenceInterfaceProtocol, BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class BIService(BaseService, AsyncServiceMixin, BusinessIntelligenceInterfaceProtocol):
    """Business Intelligence Service - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)

    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard - PRESERVED from Django"""
        try:
            from ..models.models import Dashboard

            # Get database session
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                dashboard = Dashboard(
                    name=dashboard_data['name'],
                    dashboard_type=dashboard_data.get('dashboard_type', 'general'),
                    description=dashboard_data.get('description', ''),
                    is_active=dashboard_data.get('is_active', True),
                    created_by_id=UUID(dashboard_data.get('created_by_id')),
                    configuration=dashboard_data.get('configuration', {})
                )

                db.add(dashboard)
                await db.commit()
                await db.refresh(dashboard)

                return {
                    'success': True,
                    'data': {
                        'id': str(dashboard.id),
                        'name': dashboard.name,
                        'dashboard_type': dashboard.dashboard_type,
                        'description': dashboard.description,
                        'is_active': dashboard.is_active
                    }
                }

        except Exception as e:
            logger.error(f"Error creating dashboard: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_dashboards(self, dashboard_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all dashboards or by type - PRESERVED from Django"""
        try:
            from ..models.models import Dashboard
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(Dashboard).filter(Dashboard.is_active == True)

                if dashboard_type:
                    query = query.filter(Dashboard.dashboard_type == dashboard_type)

                dashboards = await query.all()
                dashboard_list = []

                for dashboard in dashboards:
                    dashboard_list.append({
                        'id': str(dashboard.id),
                        'name': dashboard.name,
                        'dashboard_type': dashboard.dashboard_type,
                        'description': dashboard.description,
                        'is_active': dashboard.is_active,
                        'created_at': dashboard.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': dashboard_list,
                    'count': len(dashboard_list)
                }

        except Exception as e:
            logger.error(f"Error getting dashboards: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def update_dashboard(self, dashboard_id: UUID, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update dashboard - PRESERVED from Django"""
        try:
            from ..models.models import Dashboard
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                dashboard = await db.get(Dashboard, dashboard_id)
                if not dashboard:
                    return {
                        'success': False,
                        'error': 'Dashboard not found'
                    }

                # Update only provided fields
                update_fields = ['name', 'dashboard_type', 'description', 'is_active', 'configuration']
                for field in update_fields:
                    if field in dashboard_data:
                        setattr(dashboard, field, dashboard_data[field])

                await db.commit()
                await db.refresh(dashboard)

                return {
                    'success': True,
                    'data': {
                        'id': str(dashboard.id),
                        'name': dashboard.name,
                        'dashboard_type': dashboard.dashboard_type,
                        'description': dashboard.description,
                        'is_active': dashboard.is_active
                    }
                }

        except Exception as e:
            logger.error(f"Error updating dashboard: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def delete_dashboard(self, dashboard_id: UUID) -> Dict[str, Any]:
        """Delete dashboard - PRESERVED from Django"""
        try:
            from ..models.models import Dashboard
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                dashboard = await db.get(Dashboard, dashboard_id)
                if not dashboard:
                    return {
                        'success': False,
                        'error': 'Dashboard not found'
                    }

                await db.delete(dashboard)
                await db.commit()

                return {
                    'success': True,
                    'message': f'Dashboard {dashboard_id} deleted successfully'
                }

        except Exception as e:
            logger.error(f"Error deleting dashboard: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def create_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report - PRESERVED from Django"""
        try:
            from ..models.models import Report
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                report = Report(
                    name=report_data['name'],
                    report_type=report_data.get('report_type', 'general'),
                    description=report_data.get('description', ''),
                    parameters=report_data.get('parameters', {}),
                    is_active=report_data.get('is_active', True),
                    created_by_id=UUID(report_data.get('created_by_id'))
                )

                db.add(report)
                await db.commit()
                await db.refresh(report)

                return {
                    'success': True,
                    'data': {
                        'id': str(report.id),
                        'name': report.name,
                        'report_type': report.report_type,
                        'description': report.description,
                        'is_active': report.is_active
                    }
                }

        except Exception as e:
            logger.error(f"Error creating report: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_reports(self, report_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all reports or by type - PRESERVED from Django"""
        try:
            from ..models.models import Report
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(Report).filter(Report.is_active == True)

                if report_type:
                    query = query.filter(Report.report_type == report_type)

                reports = await query.all()
                report_list = []

                for report in reports:
                    report_list.append({
                        'id': str(report.id),
                        'name': report.name,
                        'report_type': report.report_type,
                        'description': report.description,
                        'is_active': report.is_active,
                        'created_at': report.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': report_list,
                    'count': len(report_list)
                }

        except Exception as e:
            logger.error(f"Error getting reports: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def generate_report(self, report_id: UUID, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate report with parameters - PRESERVED from Django"""
        try:
            from ..models.models import Report
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                report = await db.get(Report, report_id)
                if not report:
                    return {
                        'success': False,
                        'error': 'Report not found'
                    }

                # Generate report data based on type
                report_data = await self._generate_report_data(report, parameters or {})

                return {
                    'success': True,
                    'report_id': str(report_id),
                    'report_name': report.name,
                    'data': report_data,
                    'generated_at': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def _generate_report_data(self, report, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actual report data - PRESERVED from Django patterns"""
        if report.report_type == 'financial':
            return await self._generate_financial_report(parameters)
        elif report.report_type == 'operational':
            return await self._generate_operational_report(parameters)
        elif report.report_type == 'customer':
            return await self._generate_customer_report(parameters)
        else:
            return {'message': 'General report generated', 'data': []}

    async def _generate_financial_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate financial report - PRESERVED from Django"""
        # Implement actual financial data aggregation
        try:
            from .accounting_service import SimpleAccountingService
            accounting = SimpleAccountingService(self.solution_name)

            # Get financial summary from accounting service
            summary = await accounting.get_income_expense_summary()

            if summary['success']:
                income_expense = summary['summary']
                revenue = income_expense.get('income', 0)
                expenses = income_expense.get('expense', 0)
                profit = revenue - expenses

                return {
                    'revenue': revenue,
                    'expenses': expenses,
                    'profit': profit,
                    'period': parameters.get('period', 'monthly'),
                    'data_source': 'accounting_service'
                }
            else:
                return {
                    'revenue': 0,
                    'expenses': 0,
                    'profit': 0,
                    'period': parameters.get('period', 'monthly'),
                    'error': 'Failed to retrieve accounting data'
                }

        except Exception as e:
            logger.error(f"Error aggregating financial data: {str(e)}")
            return {
                'revenue': 0,
                'expenses': 0,
                'profit': 0,
                'period': parameters.get('period', 'monthly'),
                'error': str(e)
            }

    async def _generate_operational_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate operational report - PRESERVED from Django"""
        # Implement actual operational data aggregation
        try:
            from ..models.models import WorkflowInstance
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get workflow instances for operational metrics
                workflows = await db.query(WorkflowInstance).filter(
                    WorkflowInstance.solution_name == self.solution_name
                ).all()

                total_workflows = len(workflows)
                completed_workflows = len([w for w in workflows if w.status == 'completed'])
                active_workflows = len([w for w in workflows if w.status == 'in_progress'])

                # Calculate efficiency
                efficiency = (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0

                # Calculate productivity (workflows per day)
                productivity = total_workflows / 30  # Assuming monthly period

                # Calculate utilization
                utilization = (active_workflows / total_workflows * 100) if total_workflows > 0 else 0

                return {
                    'efficiency': round(efficiency, 2),
                    'productivity': round(productivity, 2),
                    'utilization': round(utilization, 2),
                    'total_workflows': total_workflows,
                    'active_workflows': active_workflows,
                    'completed_workflows': completed_workflows,
                    'period': parameters.get('period', 'monthly'),
                    'data_source': 'workflow_instances'
                }

        except Exception as e:
            logger.error(f"Error aggregating operational data: {str(e)}")
            return {
                'efficiency': 0,
                'productivity': 0,
                'utilization': 0,
                'period': parameters.get('period', 'monthly'),
                'error': str(e)
            }

    async def _generate_customer_report(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate customer report - PRESERVED from Django"""
        # Implement actual customer data aggregation
        try:
            from ..models.models import MSMEAnalytics
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get customer analytics data
                analytics = await db.query(MSMEAnalytics).filter(
                    MSMEAnalytics.solution_name == self.solution_name
                ).all()

                # Extract unique customers
                customers = set()
                active_customers = 0

                for record in analytics:
                    if record.customer_id:
                        customers.add(record.customer_id)
                        # Count customers with recent activity
                        if record.created_at and (datetime.now() - record.created_at).days <= 30:
                            active_customers += 1

                total_customers = len(customers)

                # Calculate satisfaction score (simplified based on activity)
                satisfaction_score = min(100, (active_customers / total_customers * 100)) if total_customers > 0 else 0

                return {
                    'total_customers': total_customers,
                    'active_customers': active_customers,
                    'satisfaction_score': round(satisfaction_score, 2),
                    'customer_engagement': round((active_customers / total_customers * 100), 2) if total_customers > 0 else 0,
                    'period': parameters.get('period', 'monthly'),
                    'data_source': 'customer_analytics'
                }

        except Exception as e:
            logger.error(f"Error aggregating customer data: {str(e)}")
            return {
                'total_customers': 0,
                'active_customers': 0,
                'satisfaction_score': 0,
                'period': parameters.get('period', 'monthly'),
                'error': str(e)
            }

    async def create_kpi(self, kpi_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new KPI - PRESERVED from Django"""
        try:
            from ..models.models import KPI
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                kpi = KPI(
                    name=kpi_data['name'],
                    kpi_type=kpi_data.get('kpi_type', 'general'),
                    description=kpi_data.get('description', ''),
                    calculation_method=kpi_data.get('calculation_method', ''),
                    target_value=kpi_data.get('target_value'),
                    unit=kpi_data.get('unit', ''),
                    is_active=kpi_data.get('is_active', True),
                    created_by_id=UUID(kpi_data.get('created_by_id'))
                )

                db.add(kpi)
                await db.commit()
                await db.refresh(kpi)

                return {
                    'success': True,
                    'data': {
                        'id': str(kpi.id),
                        'name': kpi.name,
                        'kpi_type': kpi.kpi_type,
                        'description': kpi.description,
                        'target_value': kpi.target_value,
                        'unit': kpi.unit,
                        'is_active': kpi.is_active
                    }
                }

        except Exception as e:
            logger.error(f"Error creating KPI: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_kpis(self, kpi_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all KPIs or by type - PRESERVED from Django"""
        try:
            from ..models.models import KPI
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(KPI).filter(KPI.is_active == True)

                if kpi_type:
                    query = query.filter(KPI.kpi_type == kpi_type)

                kpis = await query.all()
                kpi_list = []

                for kpi in kpis:
                    kpi_list.append({
                        'id': str(kpi.id),
                        'name': kpi.name,
                        'kpi_type': kpi.kpi_type,
                        'description': kpi.description,
                        'target_value': kpi.target_value,
                        'unit': kpi.unit,
                        'is_active': kpi.is_active,
                        'created_at': kpi.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': kpi_list,
                    'count': len(kpi_list)
                }

        except Exception as e:
            logger.error(f"Error getting KPIs: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def calculate_kpi(self, kpi_id: UUID) -> Dict[str, Any]:
        """Calculate KPI value - PRESERVED from Django"""
        try:
            from ..models.models import KPI
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                kpi = await db.get(KPI, kpi_id)
                if not kpi:
                    return {
                        'success': False,
                        'error': 'KPI not found'
                    }

                # Calculate current value based on KPI type
                current_value = await self._calculate_kpi_value(kpi)

                return {
                    'success': True,
                    'kpi_id': str(kpi_id),
                    'kpi_name': kpi.name,
                    'current_value': current_value,
                    'target_value': kpi.target_value,
                    'unit': kpi.unit,
                    'calculated_at': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error calculating KPI: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def _calculate_kpi_value(self, kpi) -> float:
        """Calculate actual KPI value - PRESERVED from Django patterns"""
        # Implement actual KPI calculations based on business data
        try:
            if kpi.kpi_type == 'financial':
                # Financial KPIs from accounting service
                from .accounting_service import SimpleAccountingService
                accounting = SimpleAccountingService(self.solution_name)

                if 'revenue' in kpi.name.lower():
                    summary = await accounting.get_income_expense_summary()
                    return summary['summary'].get('income', 0.0) if summary['success'] else 0.0
                elif 'profit' in kpi.name.lower():
                    summary = await accounting.get_income_expense_summary()
                    if summary['success']:
                        income = summary['summary'].get('income', 0)
                        expenses = summary['summary'].get('expense', 0)
                        return income - expenses
                    return 0.0
                return 0.0

            elif kpi.kpi_type == 'operational':
                # Operational KPIs from workflow data
                from ..models.models import WorkflowInstance
                from ..core.dependencies import get_db_session_for_request

                async for db in get_db_session_for_request(None):
                    workflows = await db.query(WorkflowInstance).filter(
                        WorkflowInstance.solution_name == self.solution_name
                    ).all()

                    if 'efficiency' in kpi.name.lower():
                        total = len(workflows)
                        completed = len([w for w in workflows if w.status == 'completed'])
                        return (completed / total * 100) if total > 0 else 0.0
                    elif 'productivity' in kpi.name.lower():
                        return len(workflows) / 30  # workflows per day
                    return len(workflows)

            elif kpi.kpi_type == 'customer':
                # Customer KPIs from analytics data
                from ..models.models import MSMEAnalytics
                from ..core.dependencies import get_db_session_for_request

                async for db in get_db_session_for_request(None):
                    analytics = await db.query(MSMEAnalytics).filter(
                        MSMEAnalytics.solution_name == self.solution_name
                    ).all()

                    customers = set(r.customer_id for r in analytics if r.customer_id)
                    total_customers = len(customers)

                    if 'satisfaction' in kpi.name.lower():
                        # Calculate satisfaction based on activity
                        active_customers = len([r for r in analytics if r.created_at and (datetime.now() - r.created_at).days <= 30])
                        return (active_customers / total_customers * 100) if total_customers > 0 else 0.0
                    elif 'retention' in kpi.name.lower():
                        return (len([r for r in analytics if r.created_at and (datetime.now() - r.created_at).days <= 90]) / total_customers * 100) if total_customers > 0 else 0.0
                    return total_customers

            return 0.0

        except Exception as e:
            logger.error(f"Error calculating KPI value: {str(e)}")
            return 0.0

    async def create_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chart - PRESERVED from Django"""
        try:
            from ..models.models import Chart
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                chart = Chart(
                    name=chart_data['name'],
                    chart_type=chart_data.get('chart_type', 'bar'),
                    description=chart_data.get('description', ''),
                    data_source=chart_data.get('data_source', ''),
                    configuration=chart_data.get('configuration', {}),
                    is_active=chart_data.get('is_active', True),
                    created_by_id=UUID(chart_data.get('created_by_id'))
                )

                db.add(chart)
                await db.commit()
                await db.refresh(chart)

                return {
                    'success': True,
                    'data': {
                        'id': str(chart.id),
                        'name': chart.name,
                        'chart_type': chart.chart_type,
                        'description': chart.description,
                        'is_active': chart.is_active
                    }
                }

        except Exception as e:
            logger.error(f"Error creating chart: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_charts(self, chart_type: Optional[str] = None) -> Dict[str, Any]:
        """Get all charts or by type - PRESERVED from Django"""
        try:
            from ..models.models import Chart
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):

                query = db.query(Chart).filter(Chart.is_active == True)

                if chart_type:
                    query = query.filter(Chart.chart_type == chart_type)

                charts = await query.all()
                chart_list = []

                for chart in charts:
                    chart_list.append({
                        'id': str(chart.id),
                        'name': chart.name,
                        'chart_type': chart.chart_type,
                        'description': chart.description,
                        'data_source': chart.data_source,
                        'is_active': chart.is_active,
                        'created_at': chart.created_at.isoformat()
                    })

                return {
                    'success': True,
                    'data': chart_list,
                    'count': len(chart_list)
                }

        except Exception as e:
            logger.error(f"Error getting charts: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_analytics_data(self, data_source: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get analytics data from various sources - PRESERVED from Django"""
        try:
            # Implement actual analytics data aggregation
            try:
                from ..models.models import MSMEAnalytics
                from ..core.dependencies import get_db_session_for_request

                async for db in get_db_session_for_request(None):
                    # Build query based on data source
                    query = db.query(MSMEAnalytics).filter(
                        MSMEAnalytics.solution_name == self.solution_name
                    )

                    # Apply filters
                    if filters:
                        if 'date_from' in filters:
                            query = query.filter(MSMEAnalytics.created_at >= filters['date_from'])
                        if 'date_to' in filters:
                            query = query.filter(MSMEAnalytics.created_at <= filters['date_to'])
                        if 'customer_id' in filters:
                            query = query.filter(MSMEAnalytics.customer_id == filters['customer_id'])

                    analytics_data = await query.all()

                    # Aggregate data based on source
                    if data_source == 'revenue':
                        revenue_data = {}
                        for record in analytics_data:
                            date_key = record.created_at.strftime('%Y-%m-%d') if record.created_at else 'unknown'
                            revenue_data[date_key] = revenue_data.get(date_key, 0) + (record.revenue or 0)

                        return {
                            'success': True,
                            'data_source': data_source,
                            'data': [{'date': k, 'revenue': v} for k, v in revenue_data.items()],
                            'filters': filters or {},
                            'total_records': len(analytics_data)
                        }

                    elif data_source == 'customers':
                        customer_data = {}
                        for record in analytics_data:
                            if record.customer_id:
                                customer_data[record.customer_id] = customer_data.get(record.customer_id, 0) + 1

                        return {
                            'success': True,
                            'data_source': data_source,
                            'data': [{'customer_id': k, 'interactions': v} for k, v in customer_data.items()],
                            'filters': filters or {},
                            'total_records': len(analytics_data)
                        }

                    # Default aggregation
                    return {
                        'success': True,
                        'data_source': data_source,
                        'data': [{'record': i, 'value': getattr(record, 'revenue', 0)} for i, record in enumerate(analytics_data[:100])],
                        'filters': filters or {},
                        'total_records': len(analytics_data)
                    }

            except Exception as e:
                logger.error(f"Error aggregating analytics data: {str(e)}")
                return {
                    'success': False,
                    'data_source': data_source,
                    'data': [],
                    'filters': filters or {},
                    'error': str(e)
                }

        except Exception as e:
            logger.error(f"Error getting analytics data: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'bi',
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
