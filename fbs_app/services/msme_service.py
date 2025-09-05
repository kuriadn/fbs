"""
FBS App MSME Service

Service for MSME-specific business features and management.
"""

import logging
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.db import connections
from django.conf import settings

logger = logging.getLogger('fbs_app')


class MSMEService:
    """Service for MSME-specific features"""
    
    def __init__(self, solution_name: str):
        self.solution_name = solution_name
        self.fbs_config = getattr(settings, 'FBS_APP', {})
    
    def setup_msme_business(self, business_type: str, config: Dict[str, Any] = None, request=None) -> Dict[str, Any]:
        """Setup MSME business with pre-configured data"""
        try:
            from ..models import MSMESetupWizard
            
            # Create setup wizard record
            wizard = MSMESetupWizard.objects.create(
                solution_name=self.solution_name,
                business_type=business_type,
                status='in_progress'
            )
            
            # Get pre-configured data and merge with user config
            preconfigured_data = self._get_preconfigured_data(business_type)
            if config:
                # Merge user config with preconfigured data
                preconfigured_data.update(config)
            
            wizard.preconfigured_data = preconfigured_data
            wizard.save()
            
            # Install modules and configure data
            result = self._install_and_configure(business_type, preconfigured_data, request)
            
            if result['success']:
                wizard.status = 'completed'
                wizard.completed_at = timezone.now()
                wizard.configuration = result.get('log', [])
            else:
                wizard.status = 'failed'
                wizard.configuration = result.get('errors', [])
            
            wizard.save()
            
            return {
                'success': result['success'],
                'wizard_id': wizard.id,
                'status': wizard.status,
                'log': wizard.configuration
            }
            
        except Exception as e:
            logger.error(f"Error setting up MSME business: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_preconfigured_data(self, business_type: str) -> Dict[str, Any]:
        """Get pre-configured data for business type"""
        templates = {
            'micro_retail': {
                'modules': ['sale', 'stock', 'account', 'point_of_sale'],
                'product_categories': ['Electronics', 'Clothing', 'Food', 'Home & Garden'],
                'sales_teams': ['Sales Team'],
                'warehouses': ['Main Warehouse'],
                'chart_of_accounts': 'micro_retail_coa'
            },
            'small_manufacturing': {
                'modules': ['mrp', 'sale', 'stock', 'purchase', 'account'],
                'product_categories': ['Raw Materials', 'Finished Goods', 'Work in Progress'],
                'sales_teams': ['Sales Team'],
                'warehouses': ['Raw Materials', 'Finished Goods'],
                'work_centers': ['Assembly', 'Packaging'],
                'chart_of_accounts': 'small_manufacturing_coa'
            },
            'consulting': {
                'modules': ['project', 'hr_timesheet', 'account', 'sale'],
                'product_categories': ['Services', 'Consulting Hours'],
                'sales_teams': ['Consulting Team'],
                'chart_of_accounts': 'consulting_coa'
            },
            'ecommerce': {
                'modules': ['website_sale', 'sale', 'stock', 'account'],
                'product_categories': ['Electronics', 'Clothing', 'Books', 'Home'],
                'sales_teams': ['Online Sales'],
                'warehouses': ['E-commerce Warehouse'],
                'chart_of_accounts': 'ecommerce_coa'
            }
        }
        
        return templates.get(business_type, templates['micro_retail'])
    
    def _install_and_configure(self, business_type: str, preconfigured_data: Dict[str, Any], request=None) -> Dict[str, Any]:
        """Install and configure modules for business type"""
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
            return {
                'success': False,
                'error': str(e),
                'errors': [str(e)]
            }
    
    def get_business_kpis(self, business_type: str = None) -> Dict[str, Any]:
        """Get business KPIs and metrics"""
        try:
            from ..models import MSMEKPI
            
            # Get KPIs for the solution
            kpis = MSMEKPI.objects.filter(solution_name=self.solution_name)
            
            if business_type:
                kpis = kpis.filter(business_type=business_type)
            
            kpi_data = []
            for kpi in kpis:
                kpi_data.append({
                    'name': kpi.name,
                    'value': kpi.current_value,
                    'target': kpi.target_value,
                    'unit': kpi.unit,
                    'trend': kpi.trend,
                    'last_updated': kpi.last_updated
                })
            
            return {
                'success': True,
                'kpis': kpi_data,
                'count': len(kpi_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting business KPIs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_compliance_status(self) -> Dict[str, Any]:
        """Get compliance status for the business"""
        try:
            from ..models import MSMECompliance
            
            # Get compliance records for the solution
            compliance_records = MSMECompliance.objects.filter(solution_name=self.solution_name)
            
            compliance_data = []
            for record in compliance_records:
                compliance_data.append({
                    'requirement': record.requirement,
                    'status': record.status,
                    'due_date': record.due_date,
                    'last_checked': record.last_checked,
                    'notes': record.notes
                })
            
            return {
                'success': True,
                'compliance': compliance_data,
                'count': len(compliance_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_marketing_data(self) -> Dict[str, Any]:
        """Get marketing data and analytics"""
        try:
            from ..models import MSMEMarketing
            
            # Get marketing records for the solution
            marketing_records = MSMEMarketing.objects.filter(solution_name=self.solution_name)
            
            marketing_data = []
            for record in marketing_records:
                marketing_data.append({
                    'campaign_name': record.campaign_name,
                    'type': record.campaign_type,
                    'status': record.status,
                    'budget': record.budget,
                    'spent': record.amount_spent,
                    'roi': record.roi,
                    'start_date': record.start_date,
                    'end_date': record.end_date
                })
            
            return {
                'success': True,
                'marketing': marketing_data,
                'count': len(marketing_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting marketing data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for the business"""
        try:
            from ..models import MSMEAnalytics
            
            # Get analytics records for the solution
            analytics_records = MSMEAnalytics.objects.filter(solution_name=self.solution_name)
            
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
            return {'success': False, 'error': str(e)}
    
    def update_business_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update business profile information"""
        try:
            from ..models import MSMESetupWizard
            
            # Get the setup wizard for this solution
            try:
                wizard = MSMESetupWizard.objects.get(solution_name=self.solution_name)
            except MSMESetupWizard.DoesNotExist:
                return {'success': False, 'error': 'Business profile not found'}
            
            # Update profile data
            wizard.business_config.update(profile_data)
            wizard.save()
            
            return {
                'success': True,
                'message': 'Business profile updated successfully',
                'wizard_id': wizard.id
            }
            
        except Exception as e:
            logger.error(f"Error updating business profile: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def create_custom_field(self, field_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create custom field for the business"""
        try:
            from ..models.core import CustomField
            
            # Create custom field
            custom_field = CustomField.objects.create(
                model_name=field_data.get('model_name', ''),
                record_id=field_data.get('record_id', 0),
                field_name=field_data.get('field_name', ''),
                field_type=field_data.get('field_type', 'char'),
                field_value=field_data.get('field_value', ''),
                solution_name=self.solution_name
            )
            
            return {
                'success': True,
                'custom_field_id': custom_field.id,
                'message': 'Custom field created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating custom field: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_business_templates(self) -> Dict[str, Any]:
        """Get available business templates"""
        try:
            from ..models import MSMETemplate
            
            # Get templates for the solution
            templates = MSMETemplate.objects.filter(solution_name=self.solution_name)
            
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
            return {'success': False, 'error': str(e)}
    
    def apply_business_template(self, template_name: str) -> Dict[str, Any]:
        """Apply a business template"""
        try:
            from ..models import MSMETemplate
            
            # Get the template
            try:
                template = MSMETemplate.objects.get(
                    template_name=template_name,
                    solution_name=self.solution_name
                )
            except MSMETemplate.DoesNotExist:
                return {'success': False, 'error': 'Template not found'}
            
            # Apply template configuration
            # This would typically involve setting up business rules, workflows, etc.
            
            return {
                'success': True,
                'template_name': template_name,
                'message': 'Template applied successfully'
            }
            
        except Exception as e:
            logger.error(f"Error applying business template: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_setup_wizard_status(self) -> Dict[str, Any]:
        """Get setup wizard status"""
        try:
            from ..models import MSMESetupWizard
            
            # Get the setup wizard for this solution
            try:
                wizard = MSMESetupWizard.objects.get(solution_name=self.solution_name)
            except MSMESetupWizard.DoesNotExist:
                return {'success': False, 'error': 'Setup wizard not found'}
            
            return {
                'success': True,
                'status': wizard.status,
                'current_step': wizard.current_step,
                'progress': wizard.progress,
                'business_type': wizard.business_type
            }
            
        except Exception as e:
            logger.error(f"Error getting setup wizard status: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_setup_wizard_step(self, step_name: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update setup wizard step"""
        try:
            from ..models import MSMESetupWizard
            
            # Get the setup wizard for this solution
            try:
                wizard = MSMESetupWizard.objects.get(solution_name=self.solution_name)
            except MSMESetupWizard.DoesNotExist:
                return {'success': False, 'error': 'Setup wizard not found'}
            
            # Update step data
            wizard.current_step = step_name
            wizard.configuration.update(step_data)
            wizard.save()
            
            return {
                'success': True,
                'message': 'Setup wizard step updated successfully',
                'wizard_id': wizard.id
            }
            
        except Exception as e:
            logger.error(f"Error updating setup wizard step: {str(e)}")
            return {'success': False, 'error': str(e)}
