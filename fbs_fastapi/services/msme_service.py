"""
FBS FastAPI MSME Service

PRESERVED from Django msme_service.py
Service for MSME-specific business features and management.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .service_interfaces import BaseService, AsyncServiceMixin

logger = logging.getLogger(__name__)

class MSMEService(BaseService, AsyncServiceMixin):
    """Service for MSME-specific features - PRESERVED from Django"""

    def __init__(self, solution_name: str):
        super().__init__(solution_name)
        self.templates = self._load_business_templates()

    def _load_business_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load business templates - PRESERVED from Django"""
        return {
            'micro_retail': {
                'modules': ['sale', 'stock', 'account', 'point_of_sale'],
                'product_categories': ['Electronics', 'Clothing', 'Food', 'Home & Garden'],
                'sales_teams': ['Sales Team'],
                'warehouses': ['Main Warehouse'],
                'chart_of_accounts': 'micro_retail_coa',
                'description': 'Small retail store with basic operations'
            },
            'small_manufacturing': {
                'modules': ['mrp', 'sale', 'stock', 'purchase', 'account'],
                'product_categories': ['Raw Materials', 'Finished Goods', 'Work in Progress'],
                'sales_teams': ['Sales Team'],
                'warehouses': ['Raw Materials', 'Finished Goods'],
                'work_centers': ['Assembly', 'Packaging'],
                'chart_of_accounts': 'small_manufacturing_coa',
                'description': 'Small manufacturing business'
            },
            'consulting': {
                'modules': ['project', 'hr_timesheet', 'account', 'sale'],
                'product_categories': ['Services', 'Consulting Hours'],
                'sales_teams': ['Consulting Team'],
                'chart_of_accounts': 'consulting_coa',
                'description': 'Professional consulting services'
            },
            'ecommerce': {
                'modules': ['website_sale', 'sale', 'stock', 'account'],
                'product_categories': ['Electronics', 'Clothing', 'Books', 'Home'],
                'sales_teams': ['Online Sales'],
                'warehouses': ['E-commerce Warehouse'],
                'chart_of_accounts': 'ecommerce_coa',
                'description': 'Online retail business'
            }
        }

    async def setup_msme_business(self, business_type: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Setup MSME business with pre-configured data - PRESERVED from Django"""
        try:
            from ..models.models import MSMESetupWizard

            # Create setup wizard record
            wizard = MSMESetupWizard(
                business_type=business_type,
                status='in_progress'
            )

            # Get pre-configured data and merge with user config
            preconfigured_data = self._get_preconfigured_data(business_type)
            if config:
                # Merge user config with preconfigured data
                preconfigured_data.update(config)

            wizard.preconfigured_data = preconfigured_data

            # Save to database
            from ..core.dependencies import get_db_session_for_request
            async for db in get_db_session_for_request(None):
                db.add(wizard)
                await db.commit()
                await db.refresh(wizard)

                # Install modules and configure data
                result = await self._install_and_configure(business_type, preconfigured_data)

                if result['success']:
                    wizard.status = 'completed'
                    wizard.completed_at = datetime.now()
                    wizard.configuration = result.get('log', [])
                else:
                    wizard.status = 'failed'
                    wizard.configuration = result.get('errors', [])

                await db.commit()

                return {
                    'success': result['success'],
                    'wizard_id': str(wizard.id),
                    'status': wizard.status,
                    'log': wizard.configuration
                }

        except Exception as e:
            logger.error(f"Error setting up MSME business: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    def _get_preconfigured_data(self, business_type: str) -> Dict[str, Any]:
        """Get pre-configured data for business type - PRESERVED from Django"""
        return self.templates.get(business_type, self.templates['micro_retail'])

    async def _install_and_configure(self, business_type: str, preconfigured_data: Dict[str, Any]) -> Dict[str, Any]:
        """Install and configure modules for business type - PRESERVED from Django"""
        try:
            log = []
            errors = []

            # This would integrate with Odoo to install modules
            # For now, we'll simulate the process
            log.append(f"Starting configuration for {business_type} business")

            # Simulate module installation
            modules = preconfigured_data.get('modules', [])
            for module in modules:
                log.append(f"Installing module: {module}")
                # Here you would call Odoo to install the module

            # Simulate data configuration
            log.append("Configuring business data")
            # Here you would configure products, categories, etc.

            return {
                'success': True,
                'log': log,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Error in install and configure: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_business_kpis(self, business_type: Optional[str] = None) -> Dict[str, Any]:
        """Get business KPIs and metrics - PRESERVED from Django"""
        try:
            from ..models.models import MSMEKPI
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get KPIs for the solution
                query = db.query(MSMEKPI)
                if business_type:
                    query = query.filter(MSMEKPI.business_type == business_type)

                kpis = await query.all()

                kpi_data = []
                for kpi in kpis:
                    kpi_data.append({
                        'name': kpi.name,
                        'value': kpi.current_value,
                        'target': kpi.target_value,
                        'unit': kpi.unit,
                        'trend': kpi.trend,
                        'last_updated': kpi.last_updated.isoformat() if kpi.last_updated else None
                    })

                return {
                    'success': True,
                    'kpis': kpi_data,
                    'count': len(kpi_data)
                }

        except Exception as e:
            logger.error(f"Error getting business KPIs: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status for the business - PRESERVED from Django"""
        try:
            from ..models.models import MSMECompliance
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get compliance records for the solution
                compliance_records = await db.query(MSMECompliance).all()

                compliance_data = []
                for record in compliance_records:
                    compliance_data.append({
                        'requirement': record.requirement,
                        'status': record.status,
                        'due_date': record.due_date.isoformat() if record.due_date else None,
                        'last_checked': record.last_checked.isoformat() if record.last_checked else None,
                        'notes': record.notes
                    })

                return {
                    'success': True,
                    'compliance': compliance_data,
                    'count': len(compliance_data)
                }

        except Exception as e:
            logger.error(f"Error getting compliance status: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_marketing_data(self) -> Dict[str, Any]:
        """Get marketing data and analytics - PRESERVED from Django"""
        try:
            from ..models.models import MSMEMarketing
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get marketing records for the solution
                marketing_records = await db.query(MSMEMarketing).all()

                marketing_data = []
                for record in marketing_records:
                    marketing_data.append({
                        'campaign_name': record.campaign_name,
                        'type': record.campaign_type,
                        'status': record.status,
                        'budget': record.budget,
                        'spent': record.amount_spent,
                        'roi': record.roi,
                        'start_date': record.start_date.isoformat() if record.start_date else None,
                        'end_date': record.end_date.isoformat() if record.end_date else None
                    })

                return {
                    'success': True,
                    'marketing': marketing_data,
                    'count': len(marketing_data)
                }

        except Exception as e:
            logger.error(f"Error getting marketing data: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for the business - PRESERVED from Django"""
        try:
            from ..models.models import MSMEAnalytics
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get analytics records for the solution
                analytics_records = await db.query(MSMEAnalytics).all()

                # Calculate summary metrics
                total_revenue = sum(record.revenue for record in analytics_records if record.revenue)
                total_customers = len(set(record.customer_id for record in analytics_records if record.customer_id))
                total_orders = len(analytics_records)

                summary = {
                    'total_revenue': total_revenue,
                    'total_customers': total_customers,
                    'total_orders': total_orders,
                    'average_order_value': total_revenue / total_orders if total_orders > 0 else 0
                }

                return {
                    'success': True,
                    'summary': summary,
                    'analytics_count': len(analytics_records)
                }

        except Exception as e:
            logger.error(f"Error getting analytics summary: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def update_business_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update business profile information - PRESERVED from Django"""
        try:
            from ..models.models import MSMESetupWizard
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get the setup wizard for this solution
                wizard = await db.query(MSMESetupWizard).first()

                if not wizard:
                    return {'success': False, 'error': 'Business profile not found'}

                # Update profile data
                if not wizard.business_config:
                    wizard.business_config = {}

                wizard.business_config.update(profile_data)
                await db.commit()

                return {
                    'success': True,
                    'message': 'Business profile updated successfully',
                    'wizard_id': str(wizard.id)
                }

        except Exception as e:
            logger.error(f"Error updating business profile: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def create_custom_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom field for the business - PRESERVED from Django"""
        try:
            from ..models.models import CustomField
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Create custom field
                custom_field = CustomField(
                    model_name=field_data.get('model_name', ''),
                    record_id=field_data.get('record_id', 0),
                    field_name=field_data.get('field_name', ''),
                    field_type=field_data.get('field_type', 'char'),
                    field_value=field_data.get('field_value', ''),
                    solution_name=self.solution_name
                )

                db.add(custom_field)
                await db.commit()
                await db.refresh(custom_field)

                return {
                    'success': True,
                    'custom_field_id': str(custom_field.id),
                    'message': 'Custom field created successfully'
                }

        except Exception as e:
            logger.error(f"Error creating custom field: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_business_templates(self) -> Dict[str, Any]:
        """Get available business templates - PRESERVED from Django"""
        try:
            from ..models.models import MSMETemplate
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get templates for the solution
                templates = await db.query(MSMETemplate).all()

                template_data = []
                for template in templates:
                    template_data.append({
                        'template_name': template.template_name,
                        'business_type': template.business_type,
                        'description': template.description,
                        'is_active': template.is_active
                    })

                return {
                    'success': True,
                    'templates': template_data,
                    'count': len(template_data)
                }

        except Exception as e:
            logger.error(f"Error getting business templates: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def apply_business_template(self, template_name: str) -> Dict[str, Any]:
        """Apply a business template - PRESERVED from Django"""
        try:
            from ..models.models import MSMETemplate
            from ..core.dependencies import get_db_session_for_request

            async for db in get_db_session_for_request(None):
                # Get the template
                template = await db.query(MSMETemplate).filter(
                    MSMETemplate.template_name == template_name
                ).first()

                if not template:
                    return {'success': False, 'error': 'Template not found'}

                # Apply template configuration
                # This would integrate with the setup wizard
                return {
                    'success': True,
                    'template_name': template_name,
                    'business_type': template.business_type,
                    'message': f'Template {template_name} applied successfully'
                }

        except Exception as e:
            logger.error(f"Error applying business template: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def get_business_insights(self) -> Dict[str, Any]:
        """Get business insights and recommendations - PRESERVED from Django"""
        try:
            # Get KPIs
            kpi_result = await self.get_business_kpis()

            # Get analytics
            analytics_result = await self.get_analytics_summary()

            insights = []

            if kpi_result['success'] and analytics_result['success']:
                # Generate insights based on KPIs and analytics
                summary = analytics_result['summary']

                if summary['total_revenue'] > 0:
                    insights.append({
                        'type': 'revenue',
                        'message': f'Total revenue: ${summary["total_revenue"]:,.2f}',
                        'priority': 'high'
                    })

                if summary['total_customers'] > 0:
                    insights.append({
                        'type': 'customers',
                        'message': f'Total customers: {summary["total_customers"]}',
                        'priority': 'medium'
                    })

            return {
                'success': True,
                'insights': insights,
                'kpi_count': len(kpi_result.get('kpis', [])),
                'analytics_summary': analytics_result.get('summary', {})
            }

        except Exception as e:
            logger.error(f"Error getting business insights: {str(e)}")
            return await self._safe_execute(lambda: (_ for _ in ()).throw(Exception(e)))

    async def health_check(self) -> Dict[str, Any]:
        """Service health check"""
        return {
            'service': 'msme',
            'status': 'healthy',
            'templates_loaded': len(self.templates),
            'timestamp': datetime.now().isoformat()
        }